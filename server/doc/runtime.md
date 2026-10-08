# Runtime / 執行流程 / 执行流程

The harness stores ULID chats, messages, runs and image versions in `data/studio.sqlite`.
Each chat has its own URL and event cursor. One worker admits GPU turns in order.
The old `workbench.sqlite` is read without modification; remote images are copied locally,
including a retry after the engine reconnects. Old attachments and failed turns remain saved.

繁中：新資料庫保存 ULID 對話、訊息、工作及圖片版本。各對話有獨立網址及事件游標，
單一工作器循序執行 GPU 工作。舊資料庫保留唯讀，圖片複製至本機；重新連線可補回未匯入圖片。
保留舊附件及失敗回合。

简中：新数据库保存 ULID 对话、消息、任务及图片版本。各对话有独立网址和事件游标，
单一工作器顺序执行 GPU 任务。旧数据库保留只读，图片复制到本机；重连可补回未导入图片。
保留旧附件和失败回合。

LLM → all image calls → final pixels → LLM review. Independent SDXL jobs are submitted
together; identical prompts share one native batch with separate seeds. Dependent edits wait.
ComfyUI alone loads and offloads GPU models. Pillow handles CPU edits; the harness imports no torch.
Token and progress events use SSE. History keeps the complete current turn and summarizes older turns
within the token budget. Long-context acceptance and prefix reuse are still pending.

繁中：LLM 完成請求後才生成圖片，整批完成後才以真實像素檢查。相同提示共用原生批次，
每張有獨立種子；相依編輯等待來源完成。GPU 模型由 ComfyUI 載入及卸載。
SSE 傳送文字與進度，保留整個當前回合；長上下文驗收及前綴快取仍待完成。

简中：LLM 完成请求后才生成图片，整批完成后才以真实像素检查。相同提示共用原生批次，
每张有独立种子；依赖编辑等待来源完成。GPU 模型由 ComfyUI 加载和卸载。
SSE 传送文字和进度，保留整个当前回合；长上下文验收和前缀缓存仍待完成。
