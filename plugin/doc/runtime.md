# Runtime / 執行 / 执行

OpenAI chat requests become ComfyUI prompt graphs and execute in its existing queue.
OpenAI 對話請求轉成 ComfyUI 工作流程，於原生佇列執行。
OpenAI 对话请求转成 ComfyUI 工作流，在原生队列执行。

The LLM patcher registers with ComfyUI. Its load/unload callbacks own backend resources.
LLM patcher 向 ComfyUI 登記，由載入及卸載回呼管理後端資源。
LLM patcher 向 ComfyUI 注册，由加载和卸载回调管理后端资源。

ComfyUI owns admission and eviction; no wrapper forces swaps. Transformers is the serving engine.
ComfyUI 決定載入及回收，沒有強制切換包裝；transformers 為執行引擎。
ComfyUI 决定加载及回收，没有强制切换包装；transformers 为执行引擎。

Weights coexist when memory permits. Full unload moves weights to CPU RAM; later requests restore them without another disk load or quantization.
記憶體足夠時模型共存；完整卸載搬到 RAM，之後搬回，無需重讀或重新量化。
内存足够时模型共存；完整卸载搬到 RAM，之后搬回，无需重读或重新量化。

Partial unload returns zero. Identity clone handling removes old registrations without moving weights; full detach offloads. The runtime reference is weak.
部分卸載回傳零；同一實例重新登記時保留權重，完整 detach 才卸載；使用弱引用。
部分卸载返回零；同一实例重新注册时保留权重，完整 detach 才卸载；使用弱引用。

`/llm/status` reports GPU/CPU storage, estimated capacity, disk loads, RAM transfers and registry entries.
上述端點提供 GPU／CPU 儲存、預估容量、磁碟載入、RAM 搬移及登記數量。
上述端点提供 GPU／CPU 存储、估算容量、磁盘加载、RAM 搬移及注册数量。

`/v1/models` lists configured profiles. `/v1/chat/completions` accepts messages, tools and image URLs/data URLs.
上述端點列出模型，並接收對話、工具及圖片網址或資料網址。
上述端点列出模型，并接收对话、工具和图片网址或数据网址。

Requests share ComfyUI's queue. One websocket relays generated text as SSE. Timeout, disconnect or failure cancels unfinished prompts; history cleanup waits until execution stops.
共用原生佇列及 websocket，逐段輸出 SSE；逾時、斷線或失敗會取消工作，執行停止後清理歷史。
共享原生队列及 websocket，逐段输出 SSE；超时、断线或失败会取消任务，执行停止后清理历史。

Runtime data stays under `plugin/data`; dependencies under `plugin/.local-tool-app`.
執行資料與依賴分別保留在上述目錄，支援資料目錄符號連結。
运行数据和依赖分别保留在上述目录，支持数据目录符号链接。
