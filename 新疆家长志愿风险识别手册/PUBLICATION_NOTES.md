# 发布说明

## 当前发布判断

当前版本可以作为 MVP 公开发布。

校验状态：

- `FAIL=0`
- `BLOCKER=0`
- `WARN=0`
- `REVIEW=11`

`REVIEW` 项均为反承诺、拒绝承诺、检查清单或风险提示语境，不构成录取承诺。

## 当前可发布资产

- `book_full.md`：完整 Markdown 合并稿。
- `dist/index.html`：网页阅读版，可直接双击打开，也可上传到静态网站。
- `dist/book.pdf`：PDF 发布版。
- `dist/contact.html`：咨询入口页。
- `dist/xinjiang-volunteer-risk-handbook-mvp.zip`：当前发布包。
- `assets/cover.svg`：封面 SVG。
- `assets/contact-card.svg`：咨询联系卡。
- `appendix/附录F_脱敏真实案例.md`：已进入正式书稿的脱敏真实案例。
- `cases/`：3 个合成案例 + 1 个脱敏真实案例。
- `evidence/official/`：新疆教育考试院等官方页面归档。
- `evidence/school_charters/`：高校章程页面归档。
- `evidence/system/`：脱敏成绩/位次证据和招生计划截图。
- `config/consultation_entry.json`：真实咨询入口配置，状态为 `active`。
- `scripts/validate_release.py`：一键发布校验脚本。
- `VALIDATION_REPORT.md`：当前发布校验报告。

## 当前不能宣称的事

- 不能宣称任何录取结果。
- 不能说“保录取、包过、必上、稳上、100%”。
- 不能把合成案例说成真实案例。
- 不能把脱敏案例包装成成功案例。
- 不能公开未脱敏系统截图。
- 不能把本书说成完整一分一段表或完整招生计划目录。
- 不能替代当年官方系统核验。

## 推荐发布定位

第一版定位：新疆家长高考志愿风险识别手册。

核心卖点不是“给答案”，而是帮家长识别四类风险：

1. 分数和位次风险。
2. 招生章程硬门槛风险。
3. 专业调剂风险。
4. 专项批次误判风险。

## 发布前人工复核

机器校验已经通过，人工发布前只保留 3 个动作：

1. 打开 `dist/book.pdf`，快速检查封面、目录、附录 F、末页咨询入口是否正常显示。
2. 手机扫码测试 `assets/wechat-qr.png` 和 `dist/contact.html` 中的二维码。
3. 发布文案不用承诺结果，只引导“风险体检”和“资料核验”。

## 常用命令

生成完整 Markdown、HTML、封面和咨询页：

```powershell
python .\scripts\build_publish.py
```

运行发布校验：

```powershell
python .\scripts\validate_release.py
```

导出无浏览器页眉页脚的 PDF：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\export_pdf.ps1
```

当前版本已经执行过构建、PDF 导出、ZIP 打包和发布校验。
