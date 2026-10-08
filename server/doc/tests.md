# Acceptance / 驗收 / 验收

Start both services. Use `server/.local-tool-app/venv/bin/python server/src/test/NAME.py`.
Install browser tooling with `bash server/install-test-tools.sh` if needed.
These scripts use actual local models and ComfyUI, create records and images, and close their Firefox processes.

啟動兩個服務後以上述命令執行。測試使用真實本機模型，建立紀錄及圖片，結束時關閉所啟動的 Firefox。
启动两个服务后以上述命令执行。测试使用真实本地模型，建立记录和图片，结束时关闭所启动的 Firefox。

| Script | Scope / 範圍 / 范围 |
|---|---|
| studio_generate | Browser prompt → images → actual review; default seeds/sizes / 瀏覽器生成及檢查 / 浏览器生成和检查 |
| studio_views | Viewer, Debug, Library, portrait, 200% / 檢視器及比例 / 查看器和比例 |
| studio_concurrent | Two chats, one GPU queue, separate records / 雙對話共用佇列 / 双对话共用队列 |
| studio_batch | One prompt × two, native batch, distinct seeds / 原生雙圖批次 / 原生双图批次 |
| studio_edit | 48 MP, HEIC, real brush actions, exact unmasked pixels / 上傳及遮罩像素 / 上传和遮罩像素 |

Run `studio_generate` before `studio_views`. Evidence: ignored `fan-out/studio-chat`.
Other older server tests target the replaced session API and are historical, not this release's acceptance.
Core engine evidence is in `fan-out/studio-engine`. Long memory, recovery, remaining controls and
all-profile checks for the new harness remain pending. Agent tests do not satisfy the five-task human gate.

先執行生成再驗證檢視器。舊 server 測試屬於已取代的工作階段 API，不能證明新版通過。
長記憶體、恢復、其餘操作及新版五模型測試仍待完成；代理測試不代替真人五任務關卡。
先执行生成再验证查看器。旧 server 测试属于已替换的会话 API，不能证明新版通过。
长记忆、恢复、其余操作和新版五模型测试仍待完成；代理测试不替代真人五任务关卡。
