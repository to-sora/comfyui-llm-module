# GGUF import / GGUF 匯入 / GGUF 导入

Use the plugin Python, with `plugin/install-gguf.sh` installed for reference tests. Sources are in `config/content-config/imports.yaml`; serving profiles stay separate.
使用 plugin Python 及 GGUF 參考測試依賴；原始來源與執行模型設定分開。
使用 plugin Python 和 GGUF 参考测试依赖；原始来源与运行模型配置分开。

Run modules from the repository root. Replace PROFILE and BASE with the import name and matching HF architecture/processor folder. Custom imports may pass `--source FILE --mmproj FILE`.
在儲存庫根目錄執行，指定名稱及相符的 HF 架構／處理器目錄；亦可指定來源檔案。
在仓库根目录执行，指定名称和匹配的 HF 架构／处理器目录；也可指定来源文件。

```bash
plugin/.local-tool-app/venv/bin/python -m plugin.src.importer.convert PROFILE --base BASE
```

The converter retains existing targets and refuses to overwrite them. It writes `plugin/data/imported/PROFILE`. Keep enough RAM and disk for dequantized FP16 weights.
匯入不覆寫既有目標；請預留解量化 FP16 權重所需 RAM 及磁碟。
导入不覆盖已有目标；请预留反量化 FP16 权重所需 RAM 和磁盘。

Before enabling a profile, run these modules in order, each with PROFILE: `token_parity`, `logit_reference`, `logit_parity`, `vision_reference`, `vision_parity` under `plugin.src.importer`. Reference/parity GPU runs require ComfyUI stopped. Restart it for `plugin.src.test.import_workflow PROFILE float16` and again with `bnb_nf4`.
啟用前依序驗證上述模組；參考／數值 GPU 測試期間停止 ComfyUI，工作流程測試則重新啟動。
启用前依次验证上述模块；参考／数值 GPU 测试期间停止 ComfyUI，工作流测试则重新启动。

All six gates must pass: strict keys/shapes; identical tokenizer IDs; identical template strings; logits within recorded thresholds and exact short greedy output; matched vision answers; text/tools/SDXL workflows in FP16 and NF4. Only then update `models.yaml` to `data/imported/PROFILE`, backend `transformers`.
六關必須全部通過才修改執行設定：張量、分詞、範本、數值、視覺及兩種精度工作流程。
六关必须全部通过才修改运行配置：张量、分词、模板、数值、视觉和两种精度工作流。
