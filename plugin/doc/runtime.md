# Runtime / 執行 / 执行

OpenAI chat requests become ComfyUI prompt graphs and execute in its existing queue.
OpenAI 對話請求轉成 ComfyUI 工作流程，於原生佇列執行。
OpenAI 对话请求转成 ComfyUI 工作流，在原生队列执行。

The LLM patcher registers with ComfyUI. Its load/unload callbacks own backend resources.
LLM patcher 向 ComfyUI 登記，由載入及卸載回呼管理後端資源。
LLM patcher 向 ComfyUI 注册，由加载和卸载回调管理后端资源。

The extension wraps ComfyUI's model-loading entrypoint to evict the previous workload through its native unload API.
擴充套件在 ComfyUI 載入模型時，透過原生卸載 API 釋放上一種工作負載。
扩展在 ComfyUI 加载模型时，通过原生卸载 API 释放上一种工作负载。

LLMs stay loaded between requests. Switching to diffusion releases them; a later LLM request reloads them.
連續請求保留 LLM；切换至擴散模型時釋放，後續 LLM 請求再載入。
连续请求保留 LLM；切换至扩散模型时释放，后续 LLM 请求再加载。

`/llm/status` reports model states, CUDA memory and transition measurements.
上述端點提供模型狀態、CUDA 記憶體及切換量測。
上述端点提供模型状态、CUDA 内存和切换测量。

`/v1/models` lists configured profiles. `/v1/chat/completions` accepts messages, tools and image URLs/data URLs.
上述端點列出模型，並接收對話、工具及圖片網址或資料網址。
上述端点列出模型，并接收对话、工具和图片网址或数据网址。

Concurrent requests are serialized with SDXL in ComfyUI's queue. Streaming currently sends a buffered final delta.
並行請求與 SDXL 共用 ComfyUI 佇列；串流目前在完成後傳送整段結果。
并发请求与 SDXL 共用 ComfyUI 队列；流式响应目前在完成后发送整段结果。

Runtime data stays under `plugin/data`; dependencies under `plugin/.local-tool-app`.
執行資料與依賴分別保留在上述目錄，支援資料目錄符號連結。
运行数据和依赖分别保留在上述目录，支持数据目录符号链接。
