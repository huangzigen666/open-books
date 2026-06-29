# 发布校验报告

生成时间：2026-06-26 03:37:32

结论：**不可大规模公开发布**

## 统计

- FAIL：0
- BLOCKER：4
- WARN：0
- REVIEW：11
- INFO：1

## 发现

| 等级 | 检查项 | 信息 | 位置 |
|---|---|---|---|
| REVIEW | promise-word | - 想买“保录取答案”的家长。 | 01_选题策划.md:27 |
| REVIEW | promise-word | 任何“稳上”“必录”“放心填”的 AI 结论，都要降级处理。 | book_full.md:718 |
| REVIEW | promise-word | - 轻信“内部补录”“花钱改志愿”“保录取”。 | book_full.md:1419 |
| REVIEW | promise-word | - 要求“保录取”“内部名额”“花钱改结果”。 | book_full.md:1962 |
| REVIEW | promise-word | - “保录取”“内部名额”“低分捡漏”等宣传话术。 | CONTRIBUTING.md:16 |
| REVIEW | promise-word | - [ ] 没有“保录取、包过、必上、稳上、100%”等承诺表达。 | RELEASE_CHECKLIST.md:11 |
| REVIEW | promise-word | - 要求“保录取”“内部名额”“花钱改结果”。 | appendix/附录C_联系与服务边界.md:49 |
| REVIEW | promise-word | 任何“稳上”“必录”“放心填”的 AI 结论，都要降级处理。 | chapters/05_AI能帮什么不能替你做什么.md:61 |
| REVIEW | promise-word | - 轻信“内部补录”“花钱改志愿”“保录取”。 | chapters/09_填报前72小时行动表.md:160 |
| REVIEW | promise-word | - 不用“必上”“稳上”“保录取”“100%”等表达。 | research/官方依据_2026-06-25.md:63 |
| REVIEW | promise-word | - “保录取” | templates/咨询入口配置表.md:38 |
| BLOCKER | consultation-config | 咨询入口仍为 draft，不能大规模获客发布 | config/consultation_entry.json |
| BLOCKER | consultation-config | 没有填写任何真实承接入口 | config/consultation_entry.json |
| INFO | cases | 当前合成案例数量：3 | cases |
| BLOCKER | cases | 尚无脱敏真实案例，不能宣称真实案例支撑 | cases |
| BLOCKER | system-evidence | 尚未放入真实个案成绩/位次或招生计划目录系统证据 | evidence/system |

## 判定规则

- `FAIL`：文件缺失、JSON 无法解析、断链、隐私字段等硬错误。
- `BLOCKER`：不影响内部流转，但阻止大规模公开获客发布。
- `WARN`：需要人工确认的占位或归档差异。
- `REVIEW`：承诺词命中，通常允许出现在拒绝、警惕、检查清单语境。
- `INFO`：当前状态提示。
