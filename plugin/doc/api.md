# Gateway / 閘道 / 网关

POST `/v1/chat/completions` submits a real ComfyUI prompt and waits for its history result.
此端點提交真實 ComfyUI 工作流程，再等候執行結果。
此端点提交真实 ComfyUI 工作流，再等候执行结果。

Required / 必填 / 必填: `model`, `messages`.

Supported options / 支援選項 / 支持选项:

| Group / 類別 / 类别 | Fields / 欄位 / 字段 |
| --- | --- |
| Generation / 生成 / 生成 | max_tokens, max_completion_tokens, temperature, top_p, seed |
| Tools / 工具 / 工具 | tools, tool_choice, parallel_tool_calls |
| HF reasoning / HF 推理 / HF 推理 | enable_thinking |
| Runtime / 執行 / 执行 | quantization, kv_quantization, context_tokens, backend, mmproj |
| Response / 回應 / 响应 | stream, n=1 |

Images use OpenAI `image_url` content parts with an HTTPS URL or data URL. Native nodes also accept ComfyUI IMAGE tensors.
圖片使用上述內容格式，支援 HTTPS 或資料網址；原生節點也接收 IMAGE 張量。
图片使用上述内容格式，支持 HTTPS 或数据网址；原生节点也接收 IMAGE 张量。

Loopback image URLs on this service's port trust its project certificate.
本服務連接埠的迴路位址圖片網址會信任專案憑證。
本服务端口的环回地址图片网址会信任项目证书。

Tools are returned to the client for execution; send their results back as `role: tool` messages with the returned `tool_call_id`.
工具呼叫交由客戶端執行，再以工具訊息及對應識別碼回傳結果。
工具调用交由客户端执行，再以工具消息及对应标识码回传结果。

Streaming buffers generation and emits final SSE chunks; it does not stream tokens during inference. Unsupported OpenAI features are not promised.
串流會先完成生成，再輸出 SSE 結果；目前不提供即時逐 token 串流，亦不承諾其他 OpenAI 功能。
流式响应先完成生成，再输出 SSE 结果；目前不提供实时逐 token 流，亦不承诺其他 OpenAI 功能。

Errors / 錯誤 / 错误: 400 invalid request, 429 queue full, 500 execution failure.
