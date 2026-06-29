from __future__ import annotations

import html
import json
import os
import re
import urllib.parse
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
    "appendix/附录F_脱敏真实案例.md",
]


def read_book_header() -> str:
    source = (ROOT / "book.md").read_text(encoding="utf-8-sig").strip()
    marker = "\n---\n"
    if marker in source:
        return source.split(marker, 1)[0].strip()
    return source


def read_contact_config() -> dict[str, str]:
    if not CONSULTATION_CONFIG.exists():
        return DEFAULT_CONTACT.copy()
    data = json.loads(CONSULTATION_CONFIG.read_text(encoding="utf-8-sig"))
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
        parts.append(path.read_text(encoding="utf-8-sig").strip())
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
    body = "\n".join(out)
    body = re.sub(
        r'(<h2 id="本章自查">本章自查</h2>\n<ul>.*?</ul>)',
        r'<section class="keep-block checklist-block">\1</section>',
        body,
        flags=re.S,
    )
    body = re.sub(
        r'(<h2 id="怎么使用这本书">怎么使用这本书</h2>\n(?:<p>.*?</p>\n?){4})',
        r'<section class="compact-tail use-guide-block">\1</section>',
        body,
        flags=re.S,
    )
    return body, "\n".join(toc)


def style() -> str:
    return r'''
:root {
  --ink: #16202E;
  --muted: #66737F;
  --line: #C9D1D9;
  --soft-line: #E6E2D8;
  --paper: #FFFDF7;
  --canvas: #EFE7D7;
  --warm: #F4E7CF;
  --accent: #A33A32;
  --accent-2: #B08A54;
  --navy: #111B29;
  --sage: #667866;
  --danger-bg: #FFF0E7;
  --note-bg: #FFF7E3;
  --ok-bg: #ECF6ED;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background:
    radial-gradient(circle at 10% 12%, rgba(163,58,50,.12), transparent 28rem),
    radial-gradient(circle at 88% 8%, rgba(17,27,41,.10), transparent 32rem),
    linear-gradient(135deg, #F1E7D5 0%, #FFFDF7 44%, #F7F3EA 100%);
  color: var(--ink);
  font-family: "Source Han Serif SC", "Noto Serif SC", "SimSun", "Songti SC", serif;
  line-height: 1.78;
  font-size: 16px;
}
a { color: #82312A; text-decoration-thickness: 1px; text-underline-offset: 4px; }
.layout { display: grid; grid-template-columns: 304px minmax(0, 1fr); min-height: 100vh; }
.sidebar {
  position: sticky; top: 0; height: 100vh; overflow: auto;
  padding: 30px 24px; border-right: 1px solid rgba(22,32,46,.12);
  background:
    linear-gradient(180deg, rgba(255,253,247,.94), rgba(244,231,207,.88)),
    var(--paper);
  backdrop-filter: blur(14px);
}
.sidebar .brand {
  font-family: "Microsoft YaHei", "DengXian", sans-serif;
  font-weight: 900; letter-spacing: .02em; margin-bottom: 8px; line-height: 1.25;
}
.sidebar .sub { color: var(--muted); font-size: 12px; line-height: 1.65; margin-bottom: 26px; }
.sidebar nav { display: grid; gap: 5px; }
.sidebar nav a {
  display: block; padding: 8px 10px; border-radius: 999px; color: var(--ink);
  text-decoration: none; font-size: 13px; line-height: 1.35;
  font-family: "Microsoft YaHei", "DengXian", sans-serif;
}
.sidebar nav a:hover { background: #EADBC2; }
.toc-level-1 { font-weight: 800; }
.toc-level-2 { padding-left: 18px !important; color: var(--muted) !important; border-radius: 12px !important; }
main { max-width: 980px; width: 100%; margin: 0 auto; padding: 52px 48px 104px; }
.cover {
  min-height: 78vh; display: grid; align-content: stretch;
  padding: 0; margin-bottom: 54px; border-radius: 34px;
  background:
    linear-gradient(90deg, rgba(163,58,50,.10), transparent 14rem),
    radial-gradient(circle at 84% 18%, rgba(17,27,41,.10), transparent 18rem),
    linear-gradient(145deg, #FBF7EF 0%, #FFFDF8 56%, #EEE3D2 100%);
  color: var(--ink); position: relative; overflow: hidden;
  border: 1px solid #CFC1AD;
  box-shadow: 0 24px 80px rgba(22,32,46,.14);
}
.cover::before {
  content: ""; position: absolute; right: -28px; top: 96px; width: 46%; height: 68%;
  border: 2px solid rgba(22,32,46,.18); border-radius: 18px; transform: rotate(-2deg);
  background:
    linear-gradient(90deg, transparent 0 32%, rgba(22,32,46,.10) 32% calc(32% + 1px), transparent calc(32% + 1px)),
    repeating-linear-gradient(0deg, rgba(22,32,46,.10) 0 1px, transparent 1px 72px),
    rgba(255,255,255,.52);
  pointer-events: none;
}
.cover::after {
  content: "风险识别"; position: absolute; right: 86px; top: 214px;
  padding: 12px 26px; border: 4px solid #A33A32; color: #A33A32; border-radius: 10px;
  font-family: "Microsoft YaHei", "DengXian", sans-serif; font-size: 34px; font-weight: 900;
  letter-spacing: .14em; transform: rotate(-8deg); opacity: .88;
}
.cover-inner { position: relative; z-index: 1; min-height: 78vh; padding: 68px 68px 56px; display: grid; grid-template-rows: auto 1fr auto; }
.cover .kicker {
  color: #4B5A6A; font-family: "Microsoft YaHei", "DengXian", sans-serif;
  font-weight: 800; letter-spacing: .26em; font-size: 14px; text-transform: uppercase;
}
.cover-title { align-self: center; max-width: 700px; }
.cover h1 {
  font-family: "Microsoft YaHei", "DengXian", sans-serif;
  font-size: clamp(52px, 8.6vw, 96px); line-height: .98; margin: 0;
  letter-spacing: -.07em; font-weight: 900; color: #111B29;
}
.cover .subtitle {
  margin-top: 22px; max-width: 600px; font-size: clamp(19px, 2.6vw, 30px);
  color: #2C3440; font-family: "Source Han Serif SC", "Noto Serif SC", "SimSun", serif;
  font-weight: 700;
}
.cover-rules { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-top: 36px; max-width: 720px; }
.cover-rules span {
  border: 1px solid #A9B2BE; color: #1F2A38; border-radius: 999px;
  padding: 8px 10px; text-align: center; font-size: 13px; font-weight: 800;
  background: rgba(255,255,255,.58); font-family: "Microsoft YaHei", "DengXian", sans-serif;
}
.cover .meta {
  color: #586371; font-family: "Microsoft YaHei", "DengXian", sans-serif;
  display: flex; justify-content: space-between; gap: 18px; border-top: 2px solid rgba(22,32,46,.12); padding-top: 20px;
}
h1, h2, h3, h4 {
  font-family: "Microsoft YaHei", "DengXian", sans-serif;
  line-height: 1.22; letter-spacing: -.025em;
}
h1 {
  font-size: 42px; margin: 64px 0 26px; padding-top: 18px;
  border-top: 6px solid var(--navy);
}
h2 {
  font-size: 27px; margin: 46px 0 16px; padding-left: 16px;
  border-left: 6px solid var(--accent); position: relative;
}
h3 { font-size: 21px; margin: 34px 0 10px; color: #233249; }
p { margin: 13px 0; text-align: justify; }
blockquote {
  margin: 24px 0; padding: 18px 22px; background: linear-gradient(90deg, #FFF6DF, #FFFDF7);
  border-left: 6px solid var(--accent-2); border-radius: 14px; font-weight: 700;
}
ul { padding-left: 1.3rem; }
li { margin: 7px 0; }
hr { border: 0; border-top: 1px solid var(--line); margin: 58px 0; }
pre { background: #111B29; color: #F8FAFC; padding: 18px; border-radius: 16px; overflow: auto; font-size: 13px; line-height: 1.55; }
code { font-family: "Cascadia Code", Consolas, monospace; }
p code, li code { background: #EFE7D7; color: #344054; padding: 1px 5px; border-radius: 5px; }
.table-wrap {
  overflow-x: auto; margin: 24px 0; border: 1px solid #D8CFBF; border-radius: 18px;
  background: var(--paper); box-shadow: 0 10px 30px rgba(16,24,40,.05);
}
table { width: 100%; border-collapse: collapse; font-size: 14px; font-family: "Microsoft YaHei", "DengXian", sans-serif; }
th, td { padding: 12px 14px; border-bottom: 1px solid var(--soft-line); vertical-align: top; }
th { text-align: left; background: #F0E4CF; font-weight: 900; color: #26364A; }
td:first-child { font-weight: 800; color: #26364A; width: 22%; }
tr:last-child td { border-bottom: 0; }
.contact-panel {
  margin: 78px 0 0; padding: 40px; border: 1px solid #D8CFBF; border-radius: 30px;
  background:
    radial-gradient(circle at 90% 0%, rgba(198,106,43,.18), transparent 18rem),
    linear-gradient(140deg, #FFFDF7, #F6ECDB);
}
.contact-panel .status {
  display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 700;
  background: #F0E4CF; color: #91451C; margin-bottom: 10px; font-family: "Microsoft YaHei", "DengXian", sans-serif;
}
.contact-panel h2 { margin-top: 0; }
.contact-grid { display: grid; grid-template-columns: 1fr 210px; gap: 28px; align-items: center; }
.contact-list { display: grid; gap: 8px; margin-top: 16px; }
.contact-list div { padding: 10px 12px; background: rgba(255,255,255,.72); border-radius: 12px; font-family: "Microsoft YaHei", "DengXian", sans-serif; }
.qr-box {
  width: 210px; height: 210px; display: grid; place-items: center; text-align: center;
  border: 2px dashed #CDBB9E; border-radius: 22px; color: var(--muted); background: #FFFDF7;
}
.footer { margin-top: 72px; color: var(--muted); font-size: 13px; border-top: 1px solid var(--line); padding-top: 22px; }
.print-actions { position: fixed; right: 20px; bottom: 20px; display: flex; gap: 10px; z-index: 10; }
.print-actions button { border: 0; border-radius: 999px; background: var(--ink); color: white; padding: 10px 16px; cursor: pointer; box-shadow: 0 8px 24px rgba(16,24,40,.18); }
@media (max-width: 920px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar { position: relative; height: auto; border-right: 0; border-bottom: 1px solid var(--soft-line); }
  main { padding: 28px 18px 72px; }
  .cover { min-height: 62vh; border-radius: 24px; }
  .cover-inner { min-height: 62vh; padding: 38px 28px; }
  .cover-rules { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .cover .meta { display: block; }
  .contact-grid { grid-template-columns: 1fr; }
}
@media print {
  @page { size: A4; margin: 12mm 13mm; }
  body { background: white; font-size: 14.4px; line-height: 1.62; }
  .layout { display: block; }
  .sidebar, .print-actions { display: none; }
  main { max-width: none; padding: 0; }
  .cover { break-after: page; min-height: 258mm; border-radius: 0; box-shadow: none; }
  .cover::before { right: -30px; top: 88px; height: 68%; border-radius: 0; }
  .cover-inner { min-height: 258mm; padding: 52px 50px 42px; }
  .cover h1 { font-size: 68px; break-before: auto; border-top: 0; padding-top: 0; }
  .cover-rules { grid-template-columns: repeat(4, 1fr); }
  .contact-panel { break-before: page; }
  main > h1 { break-before: page; }
  h1 { font-size: 36px; margin: 42px 0 18px; padding-top: 12px; border-top-width: 5px; }
  h2 { font-size: 23px; margin: 30px 0 10px; padding-left: 12px; border-left-width: 5px; }
  h3 { font-size: 18px; margin: 22px 0 7px; }
  p { margin: 8px 0; orphans: 3; widows: 3; }
  ul { margin: 7px 0 12px; padding-left: 1.15rem; }
  li { margin: 3px 0; }
  hr { margin: 32px 0; }
  blockquote { margin: 14px 0; padding: 12px 16px; }
  .table-wrap { margin: 14px 0; }
  th, td { padding: 8px 10px; }
  h2, h3 { break-after: avoid; }
  table, pre, blockquote, .table-wrap, .keep-block { break-inside: avoid; page-break-inside: avoid; }
  .checklist-block { margin-top: 28px; }
  .checklist-block h2 { margin-top: 0; }
  .checklist-block ul { margin-bottom: 0; }
  .compact-tail h2 { margin-top: 24px; }
  .compact-tail p { margin: 7px 0; }
  a { color: inherit; text-decoration: none; }
}
'''


def cover_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2400" viewBox="0 0 1600 2400">
  <defs>
    <linearGradient id="paper" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#FFF8E9"/>
      <stop offset="0.55" stop-color="#FFFDF7"/>
      <stop offset="1" stop-color="#F0E0C5"/>
    </linearGradient>
    <radialGradient id="warm" cx="84%" cy="18%" r="46%">
      <stop offset="0" stop-color="#111B29" stop-opacity="0.10"/>
      <stop offset="1" stop-color="#FFFDF7" stop-opacity="0"/>
    </radialGradient>
    <pattern id="formGrid" width="108" height="108" patternUnits="userSpaceOnUse">
      <path d="M108 0H0V108" fill="none" stroke="#16202E" stroke-width="1.5" opacity="0.08"/>
    </pattern>
  </defs>
  <rect width="1600" height="2400" fill="url(#paper)"/>
  <rect width="1600" height="2400" fill="url(#warm)"/>
  <rect x="0" y="0" width="132" height="2400" fill="#A33A32"/>
  <rect x="132" y="0" width="18" height="2400" fill="#B08A54"/>
  <rect x="120" y="120" width="1360" height="2160" fill="none" stroke="#16202E" stroke-width="4" opacity="0.22"/>
  <rect x="930" y="330" width="560" height="1060" rx="34" fill="url(#formGrid)" stroke="#16202E" stroke-width="4" opacity="0.68" transform="rotate(-2 1210 860)"/>
  <line x1="1010" y1="520" x2="1440" y2="520" stroke="#16202E" stroke-width="4" opacity="0.16"/>
  <line x1="1010" y1="650" x2="1440" y2="650" stroke="#16202E" stroke-width="4" opacity="0.16"/>
  <line x1="1010" y1="780" x2="1440" y2="780" stroke="#16202E" stroke-width="4" opacity="0.16"/>
  <g transform="rotate(-9 1220 410)">
    <rect x="1045" y="350" width="350" height="108" rx="16" fill="none" stroke="#A33A32" stroke-width="8"/>
    <text x="1080" y="423" fill="#A33A32" font-family="Microsoft YaHei, DengXian, sans-serif" font-size="54" font-weight="900" letter-spacing="8">风险识别</text>
  </g>
  <text x="235" y="290" fill="#4B5A6A" font-family="Microsoft YaHei, DengXian, sans-serif" font-size="34" font-weight="900" letter-spacing="10">XINJIANG VOLUNTEER RISK HANDBOOK</text>
  <text x="235" y="575" fill="#111B29" font-family="Microsoft YaHei, DengXian, sans-serif" font-size="132" font-weight="900">别把孩子的</text>
  <text x="235" y="745" fill="#111B29" font-family="Microsoft YaHei, DengXian, sans-serif" font-size="132" font-weight="900">分数浪费在</text>
  <text x="235" y="915" fill="#111B29" font-family="Microsoft YaHei, DengXian, sans-serif" font-size="132" font-weight="900">志愿表里</text>
  <rect x="235" y="1005" width="860" height="10" fill="#111B29"/>
  <text x="235" y="1125" fill="#2C3440" font-family="SimSun, Source Han Serif SC, serif" font-size="50" font-weight="700">不是推荐学校，是先帮家长排掉不可逆错误。</text>
  <g font-family="Microsoft YaHei, DengXian, sans-serif" font-size="34" font-weight="800" fill="#1F2A38">
    <rect x="235" y="1250" width="205" height="72" rx="36" fill="#FFFDF7" stroke="#A9B2BE" stroke-width="3"/>
    <rect x="470" y="1250" width="205" height="72" rx="36" fill="#FFFDF7" stroke="#A9B2BE" stroke-width="3"/>
    <rect x="705" y="1250" width="205" height="72" rx="36" fill="#FFFDF7" stroke="#A9B2BE" stroke-width="3"/>
    <rect x="940" y="1250" width="205" height="72" rx="36" fill="#FFFDF7" stroke="#A9B2BE" stroke-width="3"/>
    <text x="287" y="1298">位次核验</text>
    <text x="522" y="1298">章程红线</text>
    <text x="757" y="1298">专业调剂</text>
    <text x="992" y="1298">专项批次</text>
  </g>
  <path d="M235 1705 L455 1705 L455 1515 L675 1515 L675 1705 L895 1705" fill="none" stroke="#A33A32" stroke-width="34" stroke-linecap="round" stroke-linejoin="round" opacity="0.86"/>
  <circle cx="235" cy="1705" r="22" fill="#111B29"/>
  <circle cx="895" cy="1705" r="22" fill="#111B29"/>
  <line x1="235" y1="2050" x2="1395" y2="2050" stroke="#16202E" stroke-width="4" opacity="0.16"/>
  <text x="235" y="2130" fill="#16202E" font-family="Microsoft YaHei, DengXian, sans-serif" font-size="48" font-weight="700">黄昊 Rex / 问路</text>
  <text x="235" y="2208" fill="#586371" font-family="Microsoft YaHei, DengXian, sans-serif" font-size="34">新疆家长高考志愿风险识别手册 · MVP 初稿 · 2026-06-25</text>
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


def relative_asset_href(asset_path: str, output_dir: Path) -> str:
    if not asset_path:
        return ""
    if re.match(r"^https?://", asset_path) or asset_path.startswith("data:"):
        return asset_path
    path = Path(asset_path)
    if not path.is_absolute():
        path = ROOT / path
    try:
        href = Path(os.path.relpath(path.resolve(), output_dir.resolve())).as_posix()
    except Exception:
        href = asset_path.replace("\\", "/")
    return urllib.parse.quote(href, safe="/:._-")


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
    qr_image = relative_asset_href(config.get("qr_image", "").strip(), DIST)
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
    qr_image = relative_asset_href(config.get("qr_image", "").strip(), ASSETS)
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
        <div class="cover-inner">
          <div class="kicker">XINJIANG VOLUNTEER RISK HANDBOOK</div>
          <div class="cover-title">
            <h1>{TITLE}</h1>
            <div class="subtitle">不是推荐学校，是先帮家长排掉不可逆错误。</div>
            <div class="cover-rules">
              <span>位次核验</span>
              <span>章程红线</span>
              <span>专业调剂</span>
              <span>专项批次</span>
            </div>
          </div>
          <div class="meta"><span>{SUBTITLE}</span><span>{AUTHOR} · {VERSION}</span></div>
        </div>
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
