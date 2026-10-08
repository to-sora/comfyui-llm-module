# Acceptance / 驗收 / 验收

Start both HTTPS services. Run `server/.local-tool-app/venv/bin/python server/src/test/NAME.py`.
Install browser tooling with `bash server/install-test-tools.sh` if needed.
Tests use local models, actual ComfyUI and Firefox; they create records and close their browser processes.
啟動兩個服務後執行上述命令。使用真實本機模型及瀏覽器，建立紀錄並清理測試程序。
启动两个服务后执行上述命令。使用真实本地模型和浏览器，创建记录并清理测试进程。

| Scripts | Scope / 範圍 / 范围 |
|---|---|
| studio_generate, studio_profiles | Default generation, actual-pixel review, five profiles / 預設生成及五模型檢視 / 默认生成和五模型检查 |
| studio_batch, studio_concurrent, studio_cancel | Native batch, queue, cancellation / 原生批次佇列及取消 / 原生批量队列和取消 |
| studio_edit | HEIC, 48 MP, real mask actions, exact unmasked pixels / 上傳及遮罩像素 / 上传和遮罩像素 |
| studio_views, studio_a11y | Layout sizes, focus, touch targets / 比例、焦點與操作範圍 / 比例、焦点和操作范围 |
| studio_settings, studio_library, studio_basics | Languages, themes, settings, downloads, clipboard and chats / 設定下載與對話 / 设置下载和会话 |
| studio_recovery, studio_retry, studio_lifecycle | Refresh, SSE outage, restart, retry and service ownership / 斷線恢復啟停 / 断线恢复启停 |
| studio_memory, studio_migration | Rolling summaries, failed turns and real legacy records / 摘要及舊資料 / 摘要和旧数据 |
| studio_duplicates | Captured duplicate output, real model repair / 實際重複呼叫修復 / 实际重复调用修复 |

Run `studio_generate` before viewer checks; `studio_recovery` before `studio_retry`.
Recovery uses a temporary real HTTPS relay to disconnect only its own browser, with no inference mocks.
`studio_duplicates` replays the retained failure fixture in `fan-out/studio-chat`.
See `text-coverage.txt` and the portable report there for measured outcomes and limits.

先生成再驗證檢視器；先恢復測試再重試。HTTPS 測試轉送器只中斷自身瀏覽器，並未模擬推論。
重複呼叫測試重播保存的真實失敗案例。結果與限制見涵蓋紀錄及可攜報告。
先生成再验证查看器；先恢复测试再重试。HTTPS 测试转发器仅中断自身浏览器，没有模拟推理。
重复调用测试重放保存的真实失败案例。结果和限制见覆盖记录及便携报告。

Agent UAT does not satisfy the required five-task unaided human gate.
代理驗收不能代替真人獨立完成五項任務的關卡。
代理验收不能代替真人独立完成五项任务的关卡。
