from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book_full.md"
DIST = ROOT / "dist"
ASSETS = ROOT / "assets"
CONFIG = ROOT / "config"
CONSULTATION_CONFIG = CONFIG / "consultation_entry.json"

TITLE = "别把孩子的分数浪费在志愿表里"
SUBTITLE = "新疆家长高考志愿风险识别手册"
AUTHOR = "黄昊 Rex / 问路"
VERSION = "MVP 初稿 2026-06-25"

DEFAULT_CONTACT = {
    "status": "draft",
    "owner": AUTHOR,
    "service_name": "新疆高考志愿风险体检",
    "primary_action": "先做资料核验，再决定是否进入一对一方案。",
    "wechat_id": "",
    "public_account": "",
    "video_account": "",
    "booking_url": "",
    "workbench_url": "",
    "qr_image": "",
    "notice": "当前公开版未配置真实咨询入口。正式发布前请填写微信、公众号、预约链接或二维码。",
    "service_boundary": "只做风险识别、方案复核和决策辅助，不承诺录取结果。",
}

SECTION_FILES = [
    "chapters/00_前言.md",
    "chapters/01_志愿填报的第一性原理.md",
    "chapters/02_新疆家长的第一道锁.md",
    "chapters/03_冲稳保不是万能药.md",
    "chapters/04_招生章程才是硬门槛.md",
    "chapters/05_AI能帮什么不能替你做什么.md",
    "chapters/06_家长决策会怎么开.md",
    "chapters/07_低分段不是没路.md",
    "chapters/08_专项场景不能套通用模板.md",
    "chapters/09_填报前72小时行动表.md",
    "chapters/10_合格志愿方案长什么样.md",
    "appendix/附录A_招生章程核验表.md",
    "appendix/附录B_官方证据清单.md",
    "appendix/附录C_联系与服务边界.md",
    "appendix/附录D_专项类型核验卡.md",
    "appendix/附录E_系统证据留存与案例脱敏卡.md",
]


def read_book_header() -> str:
    source = (ROOT / "book.md").read_text(encoding="utf-8").strip()
    marker = "\n---\n"
    if marker in source:
        return source.split(marker, 1)[0].strip()
    return source


def read_contact_config() -> dict[str, str]:
    if not CONSULTATION_CONFIG.exists():
        return DEFAULT_CONTACT.copy()
    data = json.loads(CONSULTATION_CONFIG.read_text(encoding="utf-8"))
    merged = DEFAULT_CONTACT.copy()
    for key, value in data.items():
        merged[key] = "" if value is None else str(value)
    return merged


def assemble_book() -> None:
    parts = [read_book_header()]
    for rel_path in SECTION_FILES:
        path = ROOT / rel_path
        if not path.exists():
            raise FileNotFoundError(path)
        parts.append(path.read_text(encoding="utf-8").strip())
    BOOK.write_text("\n\n---\n\n".join(parts) + "\n", encoding="utf-8")


def inline_md(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def is_table_line(line: str) -> bool:
    return line.strip().startswith("|") and line.strip().endswith("|")


def parse_table(lines: list[str], start: int) -> tuple[str, int]:
    table_lines: list[str] = []
    i = start
    while i < len(lines) and is_table_line(lines[i]):
        table_lines.append(lines[i].strip())
        i += 1
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"^:?-{3,}:?$", c) for c in cells):
            continue
        rows.append(cells)
    if not rows:
        return "", i
    head = rows[0]
    body = rows[1:]
    out = ["<div class=\"table-wrap\"><table>", "<thead><tr>"]
    out.extend(f"<th>{inline_md(c)}</th>" for c in head)
    out.append("</tr></thead>")
    if body:
        out.append("<tbody>")
        for row in body:
            out.append("<tr>")
            out.extend(f"<td>{inline_md(c)}</td>" for c in row)
            out.append("</tr>")
        out.append("</tbody>")
    out.append("</table></div>")
    return "\n".join(out), i


def markdown_to_html(md: str) -> tuple[str, str]:
    lines = md.splitlines()
    out: list[str] = []
    toc: list[str] = []
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    para: list[str] = []
    list_buf: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append(f"<p>{inline_md(' '.join(para).strip())}</p>")
            para = []

    def flush_list() -> None:
        nonlocal list_buf
        if list_buf:
            out.append("<ul>")
            for item in list_buf:
                out.append(f"<li>{inline_md(item)}</li>")
            out.append("</ul>")
            list_buf = []

    def flush_code() -> None:
        nonlocal code_buf, code_lang
        cls = f" language-{html.escape(code_lang)}" if code_lang else ""
        out.append(f"<pre><code class=\"{cls.strip()}\">{html.escape('\n'.join(code_buf))}</code></pre>")
        code_buf = []
        code_lang = ""

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip("\n")

        if line.strip().startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_para(); flush_list()
                in_code = True
                code_lang = line.strip().strip("`").strip()
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if not line.strip():
            flush_para(); flush_list()
            i += 1
            continue

        if is_table_line(line):
            flush_para(); flush_list()
            table_html, i = parse_table(lines, i)
            if table_html:
                out.append(table_html)
            continue

        if line.strip() in {"---", "***"}:
            flush_para(); flush_list()
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            flush_para(); flush_list()
            level = len(m.group(1))
            text = m.group(2).strip()
            slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text).strip("-").lower()
            if level <= 2:
                toc.append(f'<a class="toc-level-{level}" href="#{slug}">{inline_md(text)}</a>')
            out.append(f'<h{level} id="{slug}">{inline_md(text)}</h{level}>')
            i += 1
            continue

        if line.startswith(">"):
            flush_para(); flush_list()
            out.append(f"<blockquote>{inline_md(line.lstrip('>').strip())}</blockquote>")
            i += 1
            continue

        m = re.match(r"^\s*[-*]\s+(.+)$", line)
        if m:
            flush_para()
            list_buf.append(m.group(1).strip())
            i += 1
            continue

        m = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if m:
            flush_para()
            list_buf.append(m.group(1).strip())
            i += 1
            continue

        para.append(line.strip())
        i += 1

    flush_para(); flush_list()
    return "\n".join(out), "\n".join(toc)


def style() -> str:
    return r'''
:root {
  --ink: #1D2939;
  --muted: #667085;
  --line: #D0D5DD;
  --soft-line: #EAECF0;
  --paper: #FFFFFF;
  --warm: #F7F2E9;
  --accent: #E0892F;
  --danger-bg: #FEF3F2;
  --note-bg: #FFFAEB;
  --ok-bg: #ECFDF3;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background:
    radial-gradient(circle at 12% 8%, rgba(224,137,47,.18), transparent 26rem),
    linear-gradient(135deg, #fbf7ef 0%, #fff 46%, #f5f7f8 100%);
  color: var(--ink);
  font-family: "Source Han Sans SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  line-height: 1.72;
}
a { color: #9A5B1E; text-decoration-thickness: 1px; text-underline-offset: 3px; }
.layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); min-height: 100vh; }
.sidebar {
  position: sticky; top: 0; height: 100vh; overflow: auto;
  padding: 28px 22px; border-right: 1px solid var(--soft-line);
  background: rgba(255,255,255,.82); backdrop-filter: blur(12px);
}
.sidebar .brand { font-weight: 700; letter-spacing: .04em; margin-bottom: 4px; }
.sidebar .sub { color: var(--muted); font-size: 13px; line-height: 1.5; margin-bottom: 22px; }
.sidebar nav { display: grid; gap: 6px; }
.sidebar nav a { display: block; padding: 7px 8px; border-radius: 9px; color: var(--ink); text-decoration: none; font-size: 13px; line-height: 1.35; }
.sidebar nav a:hover { background: var(--warm); }
.toc-level-1 { font-weight: 700; }
.toc-level-2 { padding-left: 16px !important; color: var(--muted) !important; }
main { max-width: 940px; width: 100%; margin: 0 auto; padding: 48px 42px 96px; }
.cover {
  min-height: 72vh; display: grid; align-content: center; gap: 18px;
  padding: 56px; margin-bottom: 46px; border: 1px solid var(--line); border-radius: 28px;
  background:
    linear-gradient(155deg, rgba(29,41,57,.95), rgba(29,41,57,.88)),
    radial-gradient(circle at 88% 20%, rgba(224,137,47,.35), transparent 20rem);
  color: white; position: relative; overflow: hidden;
}
.cover::after {
  content: ""; position: absolute; right: -70px; bottom: -90px; width: 260px; height: 260px;
  border: 34px solid rgba(224,137,47,.45); border-radius: 50%;
}
.cover .kicker { color: #F7D4A8; font-weight: 600; letter-spacing: .18em; }
.cover h1 { font-size: clamp(42px, 8vw, 78px); line-height: 1.05; margin: 0; letter-spacing: -.04em; }
.cover .subtitle { font-size: clamp(18px, 3vw, 28px); color: #F7F2E9; }
.cover .meta { color: rgba(255,255,255,.72); margin-top: 18px; }
h1, h2, h3, h4 { line-height: 1.25; letter-spacing: -.02em; }
h1 { font-size: 42px; margin: 56px 0 24px; padding-top: 16px; }
h2 { font-size: 27px; margin: 44px 0 14px; padding-left: 14px; border-left: 5px solid var(--accent); }
h3 { font-size: 21px; margin: 32px 0 10px; }
p { margin: 13px 0; }
blockquote { margin: 22px 0; padding: 18px 22px; background: var(--note-bg); border-left: 5px solid var(--accent); border-radius: 12px; }
ul { padding-left: 1.25rem; }
li { margin: 6px 0; }
hr { border: 0; border-top: 1px solid var(--line); margin: 54px 0; }
pre { background: #101828; color: #F8FAFC; padding: 18px; border-radius: 16px; overflow: auto; font-size: 13px; line-height: 1.55; }
code { font-family: "Cascadia Code", Consolas, monospace; }
p code, li code { background: #F2F4F7; color: #344054; padding: 1px 5px; border-radius: 5px; }
.table-wrap { overflow-x: auto; margin: 22px 0; border: 1px solid var(--line); border-radius: 16px; background: white; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 10px 12px; border-bottom: 1px solid var(--soft-line); vertical-align: top; }
th { text-align: left; background: #F9FAFB; font-weight: 700; }
tr:last-child td { border-bottom: 0; }
.contact-panel {
  margin: 72px 0 0; padding: 34px; border: 1px solid var(--line); border-radius: 24px;
  background:
    radial-gradient(circle at 90% 0%, rgba(224,137,47,.18), transparent 18rem),
    #fff;
}
.contact-panel .status {
  display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 700;
  background: var(--note-bg); color: #9A5B1E; margin-bottom: 10px;
}
.contact-panel h2 { margin-top: 0; }
.contact-grid { display: grid; grid-template-columns: 1fr 190px; gap: 24px; align-items: center; }
.contact-list { display: grid; gap: 8px; margin-top: 16px; }
.contact-list div { padding: 9px 11px; background: #F9FAFB; border-radius: 10px; }
.qr-box {
  width: 190px; height: 190px; display: grid; place-items: center; text-align: center;
  border: 2px dashed var(--line); border-radius: 18px; color: var(--muted); background: #F9FAFB;
}
.footer { margin-top: 72px; color: var(--muted); font-size: 13px; border-top: 1px solid var(--line); padding-top: 22px; }
.print-actions { position: fixed; right: 20px; bottom: 20px; display: flex; gap: 10px; z-index: 10; }
.print-actions button { border: 0; border-radius: 999px; background: var(--ink); color: white; padding: 10px 16px; cursor: pointer; box-shadow: 0 8px 24px rgba(16,24,40,.18); }
@media (max-width: 920px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar { position: relative; height: auto; border-right: 0; border-bottom: 1px solid var(--soft-line); }
  main { padding: 28px 18px 72px; }
  .cover { padding: 32px 24px; min-height: 58vh; border-radius: 22px; }
  .contact-grid { grid-template-columns: 1fr; }
}
@media print {
  body { background: white; }
  .layout { display: block; }
  .sidebar, .print-actions { display: none; }
  main { max-width: none; padding: 0; }
  .cover { break-after: page; min-height: 92vh; border-radius: 0; }
  .contact-panel { break-before: page; }
  h1 { break-before: page; }
  h2, h3 { break-after: avoid; }
  table, pre, blockquote { break-inside: avoid; }
  a { color: inherit; text-decoration: none; }
}
'''


def cover_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2400" viewBox="0 0 1600 2400">
  <defs>
    <radialGradient id="g" cx="82%" cy="18%" r="55%">
      <stop offset="0" stop-color="#E0892F" stop-opacity="0.55"/>
      <stop offset="0.55" stop-color="#1D2939" stop-opacity="0.12"/>
      <stop offset="1" stop-color="#1D2939"/>
    </radialGradient>
  </defs>
  <rect width="1600" height="2400" fill="#1D2939"/>
  <rect width="1600" height="2400" fill="url(#g)"/>
  <path d="M250 1840 L460 1840 L460 1630 L670 1630 L670 1420 L880 1420 L880 1210" fill="none" stroke="#F7F2E9" stroke-width="46" stroke-linecap="round" stroke-linejoin="round" opacity="0.94"/>
  <path d="M880 1210 L1090 1210 L1090 1000" fill="none" stroke="#E0892F" stroke-width="46" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M1120 760 L1158 880 L1280 920 L1158 960 L1120 1080 L1082 960 L960 920 L1082 880 Z" fill="#E0892F"/>
  <text x="160" y="300" fill="#F7D4A8" font-family="Microsoft YaHei, sans-serif" font-size="44" font-weight="700" letter-spacing="8">新疆家长高考志愿风险识别手册</text>
  <text x="160" y="520" fill="#FFFFFF" font-family="Microsoft YaHei, sans-serif" font-size="132" font-weight="700">别把孩子的</text>
  <text x="160" y="690" fill="#FFFFFF" font-family="Microsoft YaHei, sans-serif" font-size="132" font-weight="700">分数浪费在</text>
  <text x="160" y="860" fill="#FFFFFF" font-family="Microsoft YaHei, sans-serif" font-size="132" font-weight="700">志愿表里</text>
  <text x="160" y="2090" fill="#F7F2E9" font-family="Microsoft YaHei, sans-serif" font-size="48">黄昊 Rex / 问路</text>
  <text x="160" y="2170" fill="#98A2B3" font-family="Microsoft YaHei, sans-serif" font-size="34">MVP 初稿 · 2026-06-25</text>
</svg>'''


def contact_rows(config: dict[str, str]) -> list[tuple[str, str]]:
    rows = [
        ("微信", config.get("wechat_id", "")),
        ("公众号", config.get("public_account", "")),
        ("视频号", config.get("video_account", "")),
        ("预约链接", config.get("booking_url", "")),
        ("问路工作台", config.get("workbench_url", "")),
    ]
    return [(label, value) for label, value in rows if value]


def contact_block(config: dict[str, str]) -> str:
    is_active = config.get("status") == "active"
    status_text = "咨询入口已配置" if is_active else "咨询入口待配置"
    rows = contact_rows(config)
    if rows:
        rows_html = "\n".join(
            f"<div><strong>{html.escape(label)}：</strong>{inline_md(value)}</div>"
            for label, value in rows
        )
    else:
        rows_html = "<div><strong>当前状态：</strong>尚未填写真实微信、公众号、预约链接或二维码。</div>"
    qr_image = config.get("qr_image", "").strip()
    if qr_image:
        qr_html = f'<img class="qr-box" src="{html.escape(qr_image, quote=True)}" alt="咨询二维码">'
    else:
        qr_html = '<div class="qr-box">二维码待配置<br>不要带占位图发布</div>'
    return f'''
      <section class="contact-panel" id="咨询入口">
        <div class="status">{status_text}</div>
        <h2>Rex / 问路咨询入口</h2>
        <div class="contact-grid">
          <div>
            <p><strong>{inline_md(config.get("service_name", ""))}</strong></p>
            <p>{inline_md(config.get("primary_action", ""))}</p>
            <div class="contact-list">{rows_html}</div>
            <p><strong>服务边界：</strong>{inline_md(config.get("service_boundary", ""))}</p>
            <p>{inline_md(config.get("notice", ""))}</p>
          </div>
          {qr_html}
        </div>
      </section>
'''


def contact_card_svg(config: dict[str, str]) -> str:
    is_active = config.get("status") == "active"
    status = "入口已配置" if is_active else "入口待配置"
    rows = contact_rows(config)
    if not rows:
        rows = [("当前状态", "尚未填写真实入口")]
    row_text = "\n".join(
        f'<text x="130" y="{980 + i * 66}" fill="#F7F2E9" font-family="Microsoft YaHei, sans-serif" font-size="34">{html.escape(label)}：{html.escape(value)}</text>'
        for i, (label, value) in enumerate(rows[:5])
    )
    qr_image = config.get("qr_image", "").strip()
    if qr_image:
        qr = f'<image href="{html.escape(qr_image, quote=True)}" x="1040" y="890" width="300" height="300" preserveAspectRatio="xMidYMid meet"/>'
    else:
        qr = '''<rect x="1040" y="890" width="300" height="300" rx="28" fill="#F7F2E9" opacity="0.94"/>
  <text x="1190" y="1028" fill="#1D2939" font-family="Microsoft YaHei, sans-serif" font-size="34" text-anchor="middle">二维码</text>
  <text x="1190" y="1080" fill="#1D2939" font-family="Microsoft YaHei, sans-serif" font-size="30" text-anchor="middle">待配置</text>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1200" viewBox="0 0 1600 1200">
  <defs>
    <radialGradient id="g" cx="82%" cy="20%" r="65%">
      <stop offset="0" stop-color="#E0892F" stop-opacity="0.65"/>
      <stop offset="0.55" stop-color="#1D2939" stop-opacity="0.18"/>
      <stop offset="1" stop-color="#1D2939"/>
    </radialGradient>
  </defs>
  <rect width="1600" height="1200" fill="#1D2939"/>
  <rect width="1600" height="1200" fill="url(#g)"/>
  <rect x="86" y="76" width="1428" height="1048" rx="54" fill="none" stroke="#F7D4A8" stroke-width="4" opacity="0.85"/>
  <text x="130" y="190" fill="#F7D4A8" font-family="Microsoft YaHei, sans-serif" font-size="36" font-weight="700" letter-spacing="6">{html.escape(status)}</text>
  <text x="130" y="330" fill="#FFFFFF" font-family="Microsoft YaHei, sans-serif" font-size="86" font-weight="700">Rex / 问路咨询入口</text>
  <text x="130" y="445" fill="#FFFFFF" font-family="Microsoft YaHei, sans-serif" font-size="54" font-weight="700">{html.escape(config.get("service_name", ""))}</text>
  <text x="130" y="540" fill="#F7F2E9" font-family="Microsoft YaHei, sans-serif" font-size="38">{html.escape(config.get("primary_action", ""))}</text>
  <text x="130" y="640" fill="#98A2B3" font-family="Microsoft YaHei, sans-serif" font-size="30">服务边界：{html.escape(config.get("service_boundary", ""))}</text>
  <text x="130" y="720" fill="#F7D4A8" font-family="Microsoft YaHei, sans-serif" font-size="30">{html.escape(config.get("notice", ""))}</text>
  {row_text}
  {qr}
</svg>'''


def contact_page(config: dict[str, str]) -> str:
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rex / 问路咨询入口</title>
  <style>{style()}</style>
</head>
<body>
  <main>{contact_block(config)}</main>
</body>
</html>'''


def main() -> None:
    DIST.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    CONFIG.mkdir(exist_ok=True)
    contact_config = read_contact_config()
    assemble_book()
    md = BOOK.read_text(encoding="utf-8")
    body, toc = markdown_to_html(md)
    html_doc = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{TITLE}｜{SUBTITLE}</title>
  <meta name="description" content="{SUBTITLE}，作者 {AUTHOR}。">
  <style>{style()}</style>
</head>
<body>
  <div class="print-actions"><button onclick="window.print()">打印 / 导出 PDF</button></div>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">{TITLE}</div>
      <div class="sub">{SUBTITLE}<br>{AUTHOR}<br>{VERSION}</div>
      <nav>{toc}</nav>
    </aside>
    <main>
      <section class="cover">
        <div class="kicker">{SUBTITLE}</div>
        <h1>{TITLE}</h1>
        <div class="subtitle">不是推荐学校，是先帮家长排掉不可逆错误。</div>
        <div class="meta">{AUTHOR}<br>{VERSION}</div>
      </section>
      {body}
      {contact_block(contact_config)}
      <section class="footer">本页由 scripts/build_publish.py 从 book_full.md 生成。发布前请复核官方政策、招生计划和一分一段表。</section>
    </main>
  </div>
</body>
</html>'''
    (DIST / "index.html").write_text(html_doc, encoding="utf-8")
    (ASSETS / "cover.svg").write_text(cover_svg(), encoding="utf-8")
    (ASSETS / "contact-card.svg").write_text(contact_card_svg(contact_config), encoding="utf-8")
    (DIST / "contact.html").write_text(contact_page(contact_config), encoding="utf-8")
    (DIST / "README.md").write_text(f"# 发布版\n\n- index.html：网页/打印版\n- contact.html：咨询入口页\n- ../assets/cover.svg：封面图\n- ../assets/contact-card.svg：联系卡\n\n生成命令：`python scripts/build_publish.py`\n\n构建脚本会先重新生成根目录的 `book_full.md`。\n", encoding="utf-8")
    print(DIST / "index.html")
    print(ASSETS / "cover.svg")
    print(ASSETS / "contact-card.svg")
    print(DIST / "contact.html")


if __name__ == "__main__":
    main()
