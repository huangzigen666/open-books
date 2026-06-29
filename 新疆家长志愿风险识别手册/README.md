# 新疆家长志愿风险识别手册

暂定书名：**别把孩子的分数浪费在志愿表里：新疆家长高考志愿风险识别手册**

定位：面向新疆考生家长的开源风险识别书。它不承诺录取结果，不替代个性化志愿方案；它只解决一个更前置的问题：家长在动手填志愿前，先知道哪些错误不能犯，哪些信息必须核验，哪些场景必须人工复核。

## 当前进度

已完成前言、第 1-10 章、附录 A、附录 B、附录 C、附录 D、附录 E 的完整 MVP 初稿。

可直接查看：

- [book_full.md](./book_full.md)：完整 Markdown 合并稿
- [dist/index.html](./dist/index.html)：网页阅读版
- [dist/book.pdf](./dist/book.pdf)：PDF 打印版
- [assets/cover.svg](./assets/cover.svg)：封面 SVG

下一阶段重点不是继续堆正文，而是把系统内证据和承接入口补到可发布级：个案成绩/位次截图、招生计划专业目录系统截图、脱敏真实案例、真实二维码或预约入口。当前已先放入 3 个合成案例、6 所高校章程样例、专项类型核验卡、系统证据留存卡、案例脱敏模板、官方证据清单和服务边界页。

当前已经归档一批官方依据和高校章程样例，详见：

- [appendix/附录A_招生章程核验表.md](./appendix/附录A_招生章程核验表.md)
- [appendix/附录B_官方证据清单.md](./appendix/附录B_官方证据清单.md)
- [appendix/附录C_联系与服务边界.md](./appendix/附录C_联系与服务边界.md)
- [appendix/附录D_专项类型核验卡.md](./appendix/附录D_专项类型核验卡.md)
- [appendix/附录E_系统证据留存与案例脱敏卡.md](./appendix/附录E_系统证据留存与案例脱敏卡.md)
- [evidence/official/README.md](./evidence/official/README.md)
- [evidence/school_charters/README.md](./evidence/school_charters/README.md)
- [evidence/system/README.md](./evidence/system/README.md)

## 为什么选这个题

这个题最适合先写：它既能公开获客，又不会把一对一服务和录播课的核心执行全部免费倒出。

- 免费价值：家长能用它避开明显坑，建立对 Rex 的专业信任。
- 商业边界：书里讲风险识别和核验框架，不代替一人一策的最终方案。
- 产品协同：风险识别结构可以直接反哺“问路工作台”的风险区、复核区和交付报告。
- 内容复用：每章都能拆成图文号、小红书、私域长文和课程脚本。

## 当前文件

- [00_创作方法抽取.md](./00_创作方法抽取.md)
- [01_选题策划.md](./01_选题策划.md)
- [02_目录设计.md](./02_目录设计.md)
- [book.md](./book.md)
- [book_full.md](./book_full.md)
- [chapters](./chapters/)
- [appendix](./appendix/)
- [cases](./cases/)
- [examples](./examples/)
- [evidence/official/README.md](./evidence/official/README.md)
- [evidence/school_charters/README.md](./evidence/school_charters/README.md)
- [research/官方依据_2026-06-25.md](./research/官方依据_2026-06-25.md)
- [templates/家长信息采集卡.md](./templates/家长信息采集卡.md)
- [templates/志愿风险体检报告模板.md](./templates/志愿风险体检报告模板.md)
- [templates/系统证据留存清单.md](./templates/系统证据留存清单.md)
- [templates/案例脱敏处理清单.md](./templates/案例脱敏处理清单.md)
- [templates/咨询入口配置表.md](./templates/咨询入口配置表.md)
- [config/consultation_entry.json](./config/consultation_entry.json)
- [scripts/validate_release.py](./scripts/validate_release.py)
- [VALIDATION_REPORT.md](./VALIDATION_REPORT.md)
- [PUBLICATION_NOTES.md](./PUBLICATION_NOTES.md)
- [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)
- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [NEXT_ACTIONS.md](./NEXT_ACTIONS.md)

## 写作规则

1. 结论先行：每章开头先告诉家长“这章要防什么错”。
2. 不写玄学：不用“玄学报考”“押中学校”这类表达。
3. 风险分层：先红线，再高风险，再中低风险。
4. 官方优先：政策、时间、选科、批次、志愿设置以新疆教育考试院等官方发布为准。
5. AI 降级：AI 只做材料整理和初筛，不做最终拍板。

## 发布校验

生成校验报告：

```powershell
python .\scripts\validate_release.py
```

当前报告：[VALIDATION_REPORT.md](./VALIDATION_REPORT.md)

校验结论为“不可大规模公开发布”时，不代表 MVP 不能内部流转；它表示真实咨询入口、系统证据、脱敏真实案例等商业发布必需材料仍未补齐。

## 版权建议

默认采用 **CC BY-NC-SA 4.0**：允许非商业传播和改编，需署名并以相同方式共享。若后续决定做真正开放商业复用，可改为 CC BY 4.0。
