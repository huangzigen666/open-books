# 发布说明

## 当前可发布资产

- `book_full.md`：完整 Markdown 合并稿。
- `dist/index.html`：网页阅读版，可直接双击打开，也可上传到静态网站。
- `dist/book.pdf`：由 Edge headless 从网页打印生成的 PDF。
- `assets/cover.svg`：封面 SVG，可继续导入设计工具精修。
- `cases/`：3 个合成案例，发布时可保留但必须明确标注“合成案例”。
- `examples/`：官方数据入口和招生章程核验框架。
- `appendix/附录A_招生章程核验表.md`：章程核验表和六个 2026 章程样例。
- `appendix/附录B_官方证据清单.md`：官方依据、已归档页面和当前证据缺口。
- `appendix/附录C_联系与服务边界.md`：咨询入口占位、服务边界和家长准备清单。
- `appendix/附录D_专项类型核验卡.md`：军队院校、公安院校、定向培养军士、中国消防救援学院、高职单招核验卡。
- `appendix/附录E_系统证据留存与案例脱敏卡.md`：系统截图留存规则和真实案例脱敏规则。
- `evidence/official/`：新疆教育考试院官方页面归档。
- `evidence/school_charters/`：高校章程页面归档。
- `evidence/system/`：系统截图和内部证据的公开边界说明。
- `templates/系统证据留存清单.md`：真实个案截图留痕模板。
- `templates/案例脱敏处理清单.md`：真实案例公开前的脱敏模板。
- `templates/咨询入口配置表.md`：正式发布前的承接入口配置说明。
- `config/consultation_entry.json`：生成联系卡和咨询入口页的配置文件。
- `scripts/validate_release.py`：一键发布校验脚本。
- `VALIDATION_REPORT.md`：当前发布校验报告。

## 当前不能宣称的事

- 不能宣称书中包含完整 2026 一分一段数据。
- 不能宣称书中包含完整招生计划专业目录。
- 不能用第三方一分一段表替代官方成绩/位次截图。
- 不能把合成案例说成真实案例。
- 不能把未脱敏系统截图放入公开仓库。
- 不能把新疆大学通知列表当完整招生章程正文；正式引用使用阳光高考审核页或后续补学校官网正文。
- 不能把正文显示 2025 的新疆医科大学学校官网页面当 2026 证据；正式引用使用阳光高考审核页。
- 不能只用中国消防救援学院考试院入口页判断个案；已归档微信原文和学院章程，个案仍需核对当年新疆招生计划目录。
- 不能在 `config/consultation_entry.json` 仍为 `draft` 时大规模获客发布。
- 不能承诺任何录取结果。

## 发布建议

第一版可以定位为“MVP 公开稿”：先发布风险识别框架、家长自查表、72 小时行动表和 AI 使用边界。

正式商业引流版需要再补三类材料：

1. 真实个案的官方成绩/位次截图。
2. 招生计划专业目录系统截图或导出证据。
3. Rex 的 3 个脱敏真实案例。
4. Rex / 问路的真实咨询入口和预约说明。
5. 中国消防救援学院在《2026 年新疆招生与考试（下卷）》中的实际专业计划截图。

## 更新命令

生成完整 Markdown、HTML 和封面：

```powershell
python .\scripts\build_publish.py
```

`build_publish.py` 会先按 `book.md`、`chapters/`、`appendix/` 的顺序重新生成 `book_full.md`，再生成网页阅读版。

运行发布校验：

```powershell
python .\scripts\validate_release.py
```

`validate_release.py` 会检查必需文件、官方证据归档、本地 Markdown 链接、敏感字段、禁用句式、咨询入口状态、脱敏真实案例和系统证据状态，并生成 `VALIDATION_REPORT.md`。

生成 PDF：

```powershell
$root = 'F:\开源书籍\新疆家长志愿风险识别手册'
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$html = Join-Path $root 'dist\index.html'
$pdf = Join-Path $root 'dist\book.pdf'
$profile = Join-Path $env:TEMP ('codex-edge-profile-' + [guid]::NewGuid().ToString('N'))
$uri = (New-Object System.Uri($html)).AbsoluteUri
& $edge --headless=new --disable-gpu --disable-extensions --no-first-run --no-default-browser-check --user-data-dir="$profile" --print-to-pdf="$pdf" $uri
if (Test-Path -Path $profile) { Remove-Item -Path $profile -Recurse -Force -ErrorAction SilentlyContinue }
```
