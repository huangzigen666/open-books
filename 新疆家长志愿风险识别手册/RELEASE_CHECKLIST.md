# 发布检查清单

## 机器已完成

- [x] `dist/index.html` 已生成。
- [x] `dist/contact.html` 已生成。
- [x] `assets/cover.svg` 已生成。
- [x] `assets/contact-card.svg` 已生成。
- [x] `dist/book.pdf` 已导出。
- [x] `dist/book.pdf` 已用 `--no-pdf-header-footer` 导出，无浏览器日期、URL、页码页眉页脚。
- [x] `dist/xinjiang-volunteer-risk-handbook-mvp.zip` 已重新生成。
- [x] `config/consultation_entry.json` 已改为 `active`。
- [x] 二维码已接入联系页和联系卡。
- [x] 脱敏成绩/位次证据已放入 `evidence/system/`。
- [x] 招生计划截图证据已放入 `evidence/system/`。
- [x] 1 个脱敏真实案例已放入 `cases/`。
- [x] 脱敏真实案例已进入正式书稿附录 F。
- [x] `python .\scripts\validate_release.py` 已运行。
- [x] `VALIDATION_REPORT.md` 中 `FAIL=0`。
- [x] `VALIDATION_REPORT.md` 中 `BLOCKER=0`。

## 人工发布前必须看一眼

- [ ] 打开 `dist/book.pdf`，检查封面、目录、正文、附录 F、末页咨询入口是否正常显示。
- [ ] 手机扫码测试 `assets/wechat-qr.png`。
- [ ] 手机扫码测试 `dist/contact.html` 中二维码。
- [ ] 检查 ZIP 包中没有原始未脱敏成绩截图。
- [ ] 检查对外文案不承诺录取结果。
- [ ] 检查对外文案不把脱敏案例包装成成功案例。
- [ ] 检查发布渠道是否需要单独补版权或免责声明。

## 发布边界

- [x] 公开包不包含未脱敏系统截图。
- [x] 合成案例已明确标注。
- [x] 真实案例已按脱敏口径处理。
- [x] 咨询入口引导为资料核验和风险体检。
- [x] 服务边界写明：只做风险识别、方案复核和决策辅助，不承诺录取结果。

## 不允许发布的口径

- [ ] 不说任何录取结果承诺。
- [ ] 不说内部名额。
- [ ] 不说绕过官方规则。
- [ ] 不说 AI 可以替家长拍板。
- [ ] 不把本书说成完整一分一段表或完整招生计划目录。
