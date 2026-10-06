# Runtime / 執行流程 / 执行流程

EN: The harness finishes each LLM request before running its tools. Enqueued
SDXL jobs share one submitted batch; the assistant resumes after it finishes.
A global worker serializes browser/chat GPU requests. Native ComfyUI loaders
and eviction control both LLM and SDXL residency. CPU edits use Pillow/NumPy.
Nothing in this application imports torch or creates a GPU inference server.
Batch records retain ComfyUI memory snapshots before and after each image job.

繁中：每次 LLM 請求結束後才執行工具；SDXL 待處理工作一次送出成批，
完成後才恢復助理。全域工作器循序執行瀏覽器與聊天 GPU 請求。
LLM 與 SDXL 載入、釋放由 ComfyUI 控制，CPU 編輯使用 Pillow／NumPy。
此應用不匯入 torch 或建立 GPU 推理服務，批次紀錄保存前後記憶體快照。

简中：每次 LLM 请求结束后才执行工具；SDXL 待处理工作一次提交成批，
完成后才恢复助手。全局工作器顺序执行浏览器与聊天 GPU 请求。
LLM 与 SDXL 加载、释放由 ComfyUI 控制，CPU 编辑使用 Pillow／NumPy。
此应用不导入 torch 或建立 GPU 推理服务，批次记录保存前后内存快照。

EN: A browser refresh reloads persisted conversation, jobs, lineage and settings.
After a server restart, unfinished work is marked interrupted and its known
ComfyUI prompt is cancelled; completed images remain in ComfyUI history.
Reuse settings to retry. Cancellation targets only the selected prompt ID.
Chat uses short tool results and bounded context; the full transcript stays in
SQLite. Maximum rounds and revision batches are configured in config.yaml.
Visual reviews are model observations for human review, not a quality guarantee.

繁中：頁面重整會還原對話、工作、版本及設定。服務重啟後，未完工作標示
中斷並取消已知 ComfyUI prompt；已完成原圖仍在 ComfyUI 歷史，可重用設定重試。
取消僅影響選定 prompt ID。聊天使用精簡上下文，完整紀錄保留於 SQLite。
回合與修訂批次上限設定於 config.yaml。視覺回覆供使用者審閱，不能保證模型判斷正確。

简中：页面刷新会还原对话、工作、版本及设置。服务重启后，未完成工作标记
中断并取消已知 ComfyUI prompt；已完成原图仍在 ComfyUI 历史，可复用设置重试。
取消仅影响选定 prompt ID。聊天使用精简上下文，完整记录保留于 SQLite。
回合与修订批次上限设置于 config.yaml。视觉回复供用户审阅，不能保证模型判断正确。
