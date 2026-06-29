from __future__ import annotations

import json
import re
import sys
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "VALIDATION_REPORT.md"

REQUIRED_FILES = [
    "README.md",
    "LICENSE.md",
    "book.md",
    "book_full.md",
    "PUBLICATION_NOTES.md",
    "RELEASE_CHECKLIST.md",
    "NEXT_ACTIONS.md",
    "config/consultation_entry.json",
    "scripts/build_publish.py",
    "appendix/附录A_招生章程核验表.md",
    "appendix/附录B_官方证据清单.md",
    "appendix/附录C_联系与服务边界.md",
    "appendix/附录D_专项类型核验卡.md",
    "appendix/附录E_系统证据留存与案例脱敏卡.md",
    "evidence/official/sources.json",
    "evidence/official/README.md",
    "evidence/school_charters/README.md",
    "evidence/system/README.md",
    "templates/系统证据留存清单.md",
    "templates/案例脱敏处理清单.md",
    "templates/咨询入口配置表.md",
    "assets/cover.svg",
    "assets/contact-card.svg",
    "dist/index.html",
    "dist/contact.html",
    "dist/book.pdf",
    "dist/xinjiang-volunteer-risk-handbook-mvp.zip",
]

BANNED_BALANCE_RE = re.compile(r"虽然|但是|总体而言|各有优劣|一方面|另一方面|`n")
PROMISE_RE = re.compile(r"必上|稳上|保录取|包过|一定录取|100%")
SENSITIVE_RE = re.compile(
    r"身份证号[:：]\s*[0-9Xx]{6,}|准考证号[:：]\s*\d{6,}|考生号[:：]\s*\d{6,}|手机号[:：]\s*1\d{10}|\b1\d{10}\b"
)
PLACEHOLDER_RE = re.compile(r"此处放|待填写|TODO|FIXME", re.IGNORECASE)


@dataclass
class Finding:
    level: str
    check: str
    message: str
    path: str = ""
    line: int | None = None

    def as_row(self) -> str:
        location = self.path
        if self.line is not None:
            location = f"{location}:{self.line}" if location else str(self.line)
        return f"| {self.level} | {self.check} | {escape_pipe(self.message)} | {escape_pipe(location)} |"


def escape_pipe(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def text_files() -> list[Path]:
    exts = {".md", ".html", ".py", ".svg", ".txt", ".json"}
    return [
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and p.suffix.lower() in exts
        and "__pycache__" not in p.parts
        and ".git" not in p.parts
    ]


def public_text_files() -> list[Path]:
    return [
        p
        for p in text_files()
        if "evidence" not in p.parts
        and "dist" not in p.parts
        and "scripts" not in p.parts
    ]


def line_hits(path: Path, pattern: re.Pattern[str]) -> list[tuple[int, str]]:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except UnicodeDecodeError:
        return []
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(content.splitlines(), 1):
        if pattern.search(line):
            hits.append((i, line.strip()))
    return hits


def check_required_files(findings: list[Finding]) -> None:
    for item in REQUIRED_FILES:
        path = ROOT / item
        if not path.exists():
            findings.append(Finding("FAIL", "required-file", "缺少必需文件", item))
        elif path.is_file() and path.stat().st_size == 0:
            findings.append(Finding("FAIL", "required-file", "文件为空", item))


def check_sources_json(findings: list[Finding]) -> None:
    source_path = ROOT / "evidence/official/sources.json"
    try:
        data = json.loads(source_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        findings.append(Finding("FAIL", "sources-json", f"sources.json 无法解析：{exc}", rel(source_path)))
        return
    if not isinstance(data, list):
        findings.append(Finding("FAIL", "sources-json", "sources.json 顶层必须是数组", rel(source_path)))
        return
    names: set[str] = set()
    for idx, item in enumerate(data):
        name = str(item.get("name", ""))
        if not name:
            findings.append(Finding("FAIL", "sources-json", f"第 {idx + 1} 条缺少 name", rel(source_path)))
            continue
        if name in names:
            findings.append(Finding("FAIL", "sources-json", f"重复 name：{name}", rel(source_path)))
        names.add(name)
        local = str(item.get("local", ""))
        if not local:
            findings.append(Finding("FAIL", "sources-json", f"{name} 缺少 local", rel(source_path)))
            continue
        local_path = Path(local)
        if not local_path.exists():
            findings.append(Finding("FAIL", "sources-json", f"{name} 的本地归档不存在", local))
            continue
        expected = item.get("bytes")
        if isinstance(expected, int) and local_path.stat().st_size != expected:
            findings.append(
                Finding(
                    "WARN",
                    "sources-json",
                    f"{name} bytes 不一致：json={expected}, actual={local_path.stat().st_size}",
                    local,
                )
            )


def check_local_markdown_links(findings: list[Finding]) -> None:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        if "evidence" in path.parts:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for match in pattern.finditer(content):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            target = urllib.parse.unquote(target)
            candidate = (path.parent / target).resolve()
            if not candidate.exists():
                line = content.count("\n", 0, match.start()) + 1
                findings.append(Finding("FAIL", "local-links", f"本地链接不存在：{target}", rel(path), line))


def check_text_patterns(findings: list[Finding]) -> None:
    for path in public_text_files():
        if path.name in {"validate_release.py", "VALIDATION_REPORT.md"}:
            continue
        for line_no, line in line_hits(path, BANNED_BALANCE_RE):
            findings.append(Finding("FAIL", "banned-style", line, rel(path), line_no))
        for line_no, line in line_hits(path, SENSITIVE_RE):
            findings.append(Finding("FAIL", "privacy", line, rel(path), line_no))
        for line_no, line in line_hits(path, PLACEHOLDER_RE):
            if "draft" in line.lower():
                level = "WARN"
            else:
                level = "WARN"
            findings.append(Finding(level, "placeholder", line, rel(path), line_no))
        for line_no, line in line_hits(path, PROMISE_RE):
            findings.append(Finding("REVIEW", "promise-word", line, rel(path), line_no))


def check_consultation_config(findings: list[Finding]) -> None:
    path = ROOT / "config/consultation_entry.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        findings.append(Finding("FAIL", "consultation-config", f"配置无法解析：{exc}", rel(path)))
        return
    status = config.get("status")
    contact_fields = ["wechat_id", "public_account", "video_account", "booking_url", "workbench_url", "qr_image"]
    filled = [field for field in contact_fields if str(config.get(field, "")).strip()]
    if status != "active":
        findings.append(Finding("BLOCKER", "consultation-config", "咨询入口仍为 draft，不能大规模获客发布", rel(path)))
    if not filled:
        findings.append(Finding("BLOCKER", "consultation-config", "没有填写任何真实承接入口", rel(path)))
    qr_image = str(config.get("qr_image", "")).strip()
    if qr_image:
        qr_path = (ROOT / qr_image).resolve()
        if not qr_path.exists():
            findings.append(Finding("FAIL", "consultation-config", f"二维码图片不存在：{qr_image}", rel(path)))


def check_case_status(findings: list[Finding]) -> None:
    cases_dir = ROOT / "cases"
    synthetic = list(cases_dir.glob("*_合成.md"))
    anonymized = list(cases_dir.glob("*_脱敏.md"))
    if synthetic:
        findings.append(Finding("INFO", "cases", f"当前合成案例数量：{len(synthetic)}", "cases"))
    if not anonymized:
        findings.append(Finding("BLOCKER", "cases", "尚无脱敏真实案例，不能宣称真实案例支撑", "cases"))


def check_system_evidence_status(findings: list[Finding]) -> None:
    system_dir = ROOT / "evidence/system"
    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
    evidence_files = [
        p
        for p in system_dir.rglob("*")
        if p.is_file() and p.name.lower() != "readme.md" and p.suffix.lower() in image_exts | {".md"}
    ]
    if not evidence_files:
        findings.append(Finding("BLOCKER", "system-evidence", "尚未放入真实个案成绩/位次或招生计划目录系统证据", rel(system_dir)))


def make_report(findings: list[Finding]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    counts: dict[str, int] = {}
    for item in findings:
        counts[item.level] = counts.get(item.level, 0) + 1
    release_ready = counts.get("FAIL", 0) == 0 and counts.get("BLOCKER", 0) == 0
    status = "可公开发布" if release_ready else "不可大规模公开发布"
    lines = [
        "# 发布校验报告",
        "",
        f"生成时间：{now}",
        "",
        f"结论：**{status}**",
        "",
        "## 统计",
        "",
        f"- FAIL：{counts.get('FAIL', 0)}",
        f"- BLOCKER：{counts.get('BLOCKER', 0)}",
        f"- WARN：{counts.get('WARN', 0)}",
        f"- REVIEW：{counts.get('REVIEW', 0)}",
        f"- INFO：{counts.get('INFO', 0)}",
        "",
        "## 发现",
        "",
        "| 等级 | 检查项 | 信息 | 位置 |",
        "|---|---|---|---|",
    ]
    if findings:
        lines.extend(item.as_row() for item in findings)
    else:
        lines.append("| OK | all | 未发现问题 |  |")
    lines.extend(
        [
            "",
            "## 判定规则",
            "",
            "- `FAIL`：文件缺失、JSON 无法解析、断链、隐私字段等硬错误。",
            "- `BLOCKER`：不影响内部流转，但阻止大规模公开获客发布。",
            "- `WARN`：需要人工确认的占位或归档差异。",
            "- `REVIEW`：承诺词命中，通常允许出现在拒绝、警惕、检查清单语境。",
            "- `INFO`：当前状态提示。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    findings: list[Finding] = []
    check_required_files(findings)
    check_sources_json(findings)
    check_local_markdown_links(findings)
    check_text_patterns(findings)
    check_consultation_config(findings)
    check_case_status(findings)
    check_system_evidence_status(findings)

    REPORT.write_text(make_report(findings), encoding="utf-8")
    fail_count = sum(1 for item in findings if item.level == "FAIL")
    print(REPORT)
    print(f"FAIL={fail_count}")
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
