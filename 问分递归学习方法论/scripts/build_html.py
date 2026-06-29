"""把 book_full.md 渲染成单页网页版（纯标准库，无外部依赖）。
用法： python scripts/build_html.py  ->  dist/index.html
PDF：用浏览器打开 dist/index.html，打印->另存为 PDF。
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book_full.md"
DIST = ROOT / "dist"

TITLE = "别刷题，去调试"
SUBTITLE = "把学习当成一台你能自己调试的计算机——一套平时就能用的递归学习方法"
AUTHOR = "黄昊 · 问分"
VERSION = "全书成稿 · 2026-06-29"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def inline(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if len(p) >= 2 and p.startswith("`") and p.endswith("`"):
            out.append("<code>" + html.escape(p[1:-1]) + "</code>")
            continue
        s = html.escape(p)
        s = IMG_RE.sub(r'<img alt="\1" src="\2">', s)
        s = LINK_RE.sub(r'<a href="\2">\1</a>', s)
        s = BOLD_RE.sub(r"<strong>\1</strong>", s)
        out.append(s)
    return "".join(out)


def split_row(line: str):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render(md: str):
    lines = md.split("\n")
    out = []
    toc = []
    h1 = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # 代码块
        if stripped.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue

        # 空行
        if stripped == "":
            i += 1
            continue

        # 分隔线
        if re.fullmatch(r"-{3,}", stripped) or re.fullmatch(r"\*{3,}", stripped):
            out.append("<hr>")
            i += 1
            continue

        # 标题
        m = re.match(r"(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            attr = ""
            if level == 1:
                h1 += 1
                sid = f"sec-{h1}"
                attr = f' id="{sid}"'
                toc.append((sid, text))
            out.append(f"<h{level}{attr}>{inline(text)}</h{level}>")
            i += 1
            continue

        # 表格
        if stripped.startswith("|") and i + 1 < n and re.fullmatch(r"\|?[\s:|-]+\|?", lines[i + 1].strip()) and "-" in lines[i + 1]:
            header = split_row(lines[i])
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            t = ["<table><thead><tr>"]
            t += [f"<th>{inline(c)}</th>" for c in header]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # 引用块
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>" + inline(" ".join(b.strip() for b in buf)) + "</blockquote>")
            continue

        # 列表（含任务清单）
        if re.match(r"\s*([-*+]|\d+\.)\s+", line):
            ordered = bool(re.match(r"\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n and re.match(r"\s*([-*+]|\d+\.)\s+", lines[i]):
                ln = lines[i]
                task = re.match(r"\s*[-*+]\s+\[( |x|X)\]\s+(.*)$", ln)
                if task:
                    checked = "checked" if task.group(1).lower() == "x" else ""
                    items.append(
                        f'<li class="task"><input type="checkbox" disabled {checked}> {inline(task.group(2))}</li>'
                    )
                else:
                    content = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", ln)
                    items.append(f"<li>{inline(content)}</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue

        # 段落
        buf = [line]
        i += 1
        while i < n and lines[i].strip() != "" and not re.match(r"\s*([-*+]|\d+\.)\s+|#{1,6}\s|>|\||```|-{3,}$", lines[i].strip()):
            buf.append(lines[i])
            i += 1
        para = " ".join(b.strip() for b in buf)
        cls = ' class="placeholder"' if "占位·待第二阶段" in para else ""
        out.append(f"<p{cls}>{inline(para)}</p>")

    toc_html = "\n".join(f'<li><a href="#{sid}">{html.escape(t)}</a></li>' for sid, t in toc)
    return "\n".join(out), toc_html


CSS = """
:root{--ink:#1f2328;--muted:#6b7280;--line:#e5e7eb;--accent:#b3541e;--bg:#fbfaf7;}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:"Noto Serif CJK SC","Source Han Serif SC","Songti SC",-apple-system,"Microsoft YaHei",serif;
 line-height:1.85;font-size:17px;}
.wrap{max-width:860px;margin:0 auto;padding:48px 24px 120px;}
.cover{text-align:center;padding:64px 0 28px;border-bottom:2px solid var(--accent);margin-bottom:8px;}
.cover h1{font-size:40px;margin:0 0 14px;letter-spacing:1px;}
.cover .sub{font-size:18px;color:var(--muted);margin:0 0 18px;}
.cover .meta{font-size:14px;color:var(--muted);margin-top:6px;}.cover-art{display:block;width:64%;max-width:330px;margin:0 auto;border:1px solid var(--line);border-radius:10px;}
.toc{background:#fff;border:1px solid var(--line);border-radius:10px;padding:20px 26px;margin:28px 0 8px;}
.toc h2{margin:0 0 10px;font-size:16px;color:var(--accent);border:none;padding:0;}
.toc ul{columns:2;column-gap:30px;margin:0;padding-left:18px;font-size:14.5px;}
.toc li{margin:4px 0;break-inside:avoid;}
.toc a{color:var(--ink);text-decoration:none;}
.toc a:hover{color:var(--accent);text-decoration:underline;}
h1{font-size:27px;margin:54px 0 18px;padding-top:14px;border-top:1px solid var(--line);}
h2{font-size:21px;margin:34px 0 12px;color:#1a1d21;}
h3{font-size:18px;margin:24px 0 10px;color:var(--accent);}
p{margin:14px 0;}
p.placeholder{color:#9aa0a6;font-style:italic;background:#f3f1ec;padding:8px 12px;border-radius:6px;}
strong{color:#16181b;}
a{color:var(--accent);}
blockquote{margin:18px 0;padding:12px 18px;background:#f5f2ec;border-left:4px solid var(--accent);
 color:#4b5159;font-size:15px;border-radius:0 6px 6px 0;}
table{border-collapse:collapse;width:100%;margin:18px 0;font-size:15px;background:#fff;}
th,td{border:1px solid var(--line);padding:9px 12px;text-align:left;vertical-align:top;}
th{background:#f3ede4;font-weight:600;}
tr:nth-child(even) td{background:#fbfaf8;}
ul,ol{padding-left:26px;margin:14px 0;}
li{margin:6px 0;}
li.task{list-style:none;margin-left:-20px;}
li.task input{margin-right:8px;}
code{background:#efece6;padding:1px 6px;border-radius:4px;font-size:14px;
 font-family:"SFMono-Regular",Consolas,monospace;}
pre{background:#2b2b2b;color:#f5f5f5;padding:16px 18px;border-radius:8px;overflow:auto;}
pre code{background:none;color:inherit;padding:0;}
hr{border:none;border-top:1px dashed #d6d3cc;margin:36px 0;}
img{max-width:240px;display:block;margin:14px 0;border:1px solid var(--line);border-radius:8px;}
@media print{body{background:#fff;font-size:12pt;}.wrap{max-width:none;padding:0;}
 .toc{break-after:page;}h1{break-before:page;}a{color:var(--ink);text-decoration:none;}}
@media(max-width:680px){.toc ul{columns:1;}.cover h1{font-size:30px;}}
"""


def main():
    md = BOOK.read_text(encoding="utf-8")
    # 去掉合并稿顶部的标题/副标题/作者（封面已单独渲染），保留免责声明等引用块
    lines = md.split("\n")
    idx = next((k for k, l in enumerate(lines) if l.strip() == "---"), 0)
    front_keep = [l for l in lines[:idx] if l.strip().startswith(">") or l.strip() == ""]
    body_md = "\n".join(front_keep + lines[idx:])
    body, toc = render(body_md)
    DIST.mkdir(exist_ok=True)
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(TITLE)} — {html.escape(SUBTITLE)}</title>
<style>{CSS}</style></head>
<body><div class="wrap">
<div class="cover">
<img class="cover-art" src="cover.svg" alt="《别刷题，去调试》封面">

<div class="meta">{html.escape(AUTHOR)} · {html.escape(VERSION)}</div>
</div>
<nav class="toc"><h2>目录</h2><ul>{toc}</ul></nav>
{body}
</div></body></html>"""
    (DIST / "index.html").write_text(page, encoding="utf-8")
    cjk = len(re.findall(r"[一-鿿]", md))
    print(f"dist/index.html 已生成：{len(page):,} 字节；正文约 {cjk:,} 中文字")


if __name__ == "__main__":
    main()
