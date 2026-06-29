"""按阅读顺序把各章节/附录合并成 book_full.md（纯标准库）。
未产出的件用占位标出。用法： python scripts/build_full.py
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ORDER = [
    ("chapters/00_前言.md", None),
    ("chapters/01_系统总览地图.md", None),
    ("chapters/02_递归调用拆到会做.md", None),
    ("chapters/03_编译学过不等于会用.md", None),
    ("chapters/04_调试错题当bug.md", None),
    ("chapters/05_内存与缓存.md", None),
    ("chapters/06_进程调度.md", None),
    ("chapters/07_版本迭代.md", None),
    ("chapters/08_自举与元认知.md", None),
    ("chapters/09_给家长的运维手册.md", None),
    ("chapters/10_AI副驾.md", None),
    ("chapters/11_交棒.md", None),
    ("appendix/附录A_计算机概念学习动作对照总表.md", None),
    ("appendix/附录B_学习系统七环节自诊断表.md", None),
    ("appendix/附录C_递归拆解卡.md", None),
    ("appendix/附录D_编译通过判据与报错对照表.md", None),
    ("appendix/附录E_错题调试归因四分法卡.md", None),
    ("appendix/附录F_提取练习与间隔重复设计卡.md", None),
    ("appendix/附录G_注意力调度优先级表.md", None),
    ("appendix/附录H_每周学习更新日志模板.md", None),
    ("appendix/附录I_元认知三问与五阶段自测卡.md", None),
    ("appendix/附录J_家长运维对照表与例会模板.md", None),
    ("appendix/附录K_AI安全提示词对照表.md", None),
    ("appendix/附录L_产品线交棒与服务边界入口.md", None),
]

HEAD = (
    "# 别刷题，去调试\n\n"
    "副标题：把学习当成一台你能自己调试的计算机——一套平时就能用的递归学习方法\n\n"
    "作者：黄昊 Rex / 问路·问分\n\n"
    "> 全书完整稿 · 前言＋第 1–11 章＋附录 A–L。\n\n"
    "> 本书是一套平时学习方法论，方法都写在书里；提分是方法跑通的结果，不是承诺。针对你个人的持续诊断和按周陪跑，是问分提供的服务。"
)


def main():
    parts = [HEAD]
    done = stub = missing = 0
    for rel, ph in ORDER:
        parts.append("\n\n---\n")
        if rel is None:
            parts.append(ph + "\n\n（占位·待第二阶段产出）")
            missing += 1
        else:
            c = (ROOT / rel).read_text(encoding="utf-8").rstrip()
            if "占位文件 · 待" in c:
                stub += 1
            else:
                done += 1
            parts.append(c)
    out = "\n".join(parts) + "\n"
    (ROOT / "book_full.md").write_text(out, encoding="utf-8")
    cjk = len(re.findall(r"[一-鿿]", out))
    print(f"book_full.md：{len(out):,}字节 约{cjk:,}中文字；成稿{done} 占位桩{stub} 纯占位{missing}")


if __name__ == "__main__":
    main()
