# Acceptance / 驗收 / 验收

EN: Start ComfyUI and the workbench, then run `bash server/install-test-tools.sh`.
Run scripts with `server/.local-tool-app/venv/bin/python server/src/test/NAME.py`.
The tests use the real local HTTPS gateway, original model weights and SDXL.
They create named sessions and real output files. No inference is mocked.

繁中：啟動 ComfyUI 與工作台後執行 `bash server/install-test-tools.sh`。
以 `server/.local-tool-app/venv/bin/python server/src/test/NAME.py` 執行測試。
使用真實 HTTPS gateway、原模型與 SDXL，建立具名工作階段及實際圖片，不模擬推理。

简中：启动 ComfyUI 与工作台后执行 `bash server/install-test-tools.sh`。
用 `server/.local-tool-app/venv/bin/python server/src/test/NAME.py` 运行测试。
使用真实 HTTPS gateway、原模型与 SDXL，建立命名工作阶段及实际图片，不模拟推理。

| Script | Scope / 範圍 / 范围 |
|---|---|
| smoke | SDXL batch / SDXL 批次 |
| cpu_accept | 20 edits, text, 4K / 編輯、文字、4K / 编辑、文字、4K |
| workflow_accept | img2img, exact unmasked pixels / 圖生圖、遮罩外像素 / 图生图、遮罩外像素 |
| sharing_accept | isolation, aliases, revoke / 隔離、別名、撤回 / 隔离、别名、撤回 |
| jobs_accept | retry, progress, cancel / 重試、進度、取消 / 重试、进度、取消 |
| failure_accept | failures, export, delete / 失敗、匯出、刪除 / 失败、导出、删除 |
| chat_accept MODEL | real model tool loop / 真實模型工具流程 / 真实模型工具流程 |
| browser_accept | generate → inspect → edit / 生成 → 檢查 → 編輯 / 生成 → 检查 → 编辑 |
| browser_extra | share, upload, final / 分享、上傳、最終版 / 分享、上传、最终版 |
| browser_layout | layout and 200% zoom / 版面與縮放 / 版面与缩放 |
| browser_models | model/context/KV and revise / 模型、上下文、KV 與修訂 / 模型、上下文、KV 与修订 |
| lifecycle_accept | stop, force, restart / 啟停與重啟 / 启停与重启 |
| evidence | recorded CUDA transitions / 實測 CUDA 交接 / 实测 CUDA 交接 |

EN: Run tests sequentially: there is one active session. Firefox uses a disposable
profile and is always terminated in cleanup. Browser scripts depend on the
browser_accept report. Lifecycle tests leave the workbench stopped; start it again.
Evidence is stored in ignored `fan-out/workbench`.

繁中：單一使用中階段，測試須循序執行。Firefox 使用暫存設定並於結束清除。
後續瀏覽器測試依賴 browser_accept 報告；生命週期測試後須重啟工作台。
證據位於不提交的 `fan-out/workbench`。

简中：单一使用中阶段，测试须顺序执行。Firefox 使用临时配置并在结束清理。
后续浏览器测试依赖 browser_accept 报告；生命周期测试后须重新启动工作台。
证据位于不提交的 `fan-out/workbench`。
