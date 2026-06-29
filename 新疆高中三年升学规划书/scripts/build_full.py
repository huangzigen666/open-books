"""按正式阅读顺序把各章节/附录合并成 book_full.md（纯标准库）。
未产出的件用占位标出。用法： python scripts/build_full.py
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (相对路径 或 None, 占位标题)
ORDER = [
    ("chapters/00_前言.md", None),
    ("chapters/01_三年时间轴与里程碑总览.md", None),
    ("chapters/02_信息系统.md", None),
    ("chapters/03_家庭沟通与分工.md", None),
    ("chapters/04_初升高暑假.md", None),
    ("chapters/05_高一上选科预研.md", None),
    ("chapters/06_高一下选科定科.md", None),
    ("chapters/07_身体条件与资格早筛.md", None),
    ("chapters/08_高二方向分流.md", None),
    ("chapters/09_高三上收口.md", None),
    ("chapters/10_预算与资源.md", None),
    ("chapters/11_PlanB复读与转轨.md", None),
    ("chapters/12_亲子心态与节奏.md", None),
    ("chapters/13_交棒志愿季.md", None),
    ("appendix/附录A_三年关键窗口时间轴总表.md", None),
    ("appendix/附录B_三年决策里程碑日历.md", None),
    ("appendix/附录C_选科专业限制对照法.md", None),
    ("appendix/附录D_身体条件与资格早筛清单.md", None),
    ("appendix/附录E_特殊招生路线早筛分流卡.md", None),
    ("appendix/附录F_信息台账与三级信源标注模板.md", None),
    ("appendix/附录G_家庭升学例会与父母分工表.md", None),
    ("appendix/附录H_三年成绩与位次档案模板.md", None),
    ("appendix/附录I_升学预算与资源规划表.md", None),
    ("appendix/附录J_PlanB触发清单.md", None),
    ("appendix/附录K_路径分流自测与信息采集卡.md", None),
    ("appendix/附录L_交棒清单.md", None),
    ("appendix/附录M_服务边界与咨询入口.md", None),
]

HEAD = (
    "# 别等出分才开始\n\n"
    "副标题：新疆高中家庭三年升学规划手册（初升高—高三 · 3+1+2）\n\n"
    "作者：黄昊 Rex / 问路\n\n"
    "> 合并阅读稿 · 波次 1+2 快照。本稿仅含已成稿与占位章节，标「（占位·待第二阶段产出）」者为未完成。正式发布稿以各源文件为准。\n\n"
    "> 免责声明：本书为通用三年升学规划手册，不构成个性化升学/选科/志愿方案，不承诺任何录取结果。政策、时间、选科要求、批次、体检限报、户籍学籍年限、特殊招生资格等，以新疆教育考试院、招生高校和当年官方发布为准。"
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
    print(f"book_full.md 重建：{len(out):,} 字节，约 {cjk:,} 中文字；成稿 {done} · 占位桩 {stub} · 纯占位 {missing}")


if __name__ == "__main__":
    main()
