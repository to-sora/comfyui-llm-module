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
| Runtime / 執行 / 执行 | quantization, kv_quantization, context_tokens, precision |
| Response / 回應 / 响应 | stream, n=1 |

Images use `image_url` parts: data URLs or this ComfyUI service's loopback HTTPS URLs, with a 16 MB cap. Native nodes accept IMAGE tensors.
圖片限資料網址或此 ComfyUI 的迴路 HTTPS，最大 16 MB；原生節點接收 IMAGE 張量。
图片限数据网址或此 ComfyUI 的环回 HTTPS，最大 16 MB；原生节点接收 IMAGE 张量。

Loopback image URLs on this service's port trust its project certificate.
本服務連接埠的迴路位址圖片網址會信任專案憑證。
本服务端口的环回地址图片网址会信任项目证书。

Tools are returned to the client for execution; send their results back as `role: tool` messages with the returned `tool_call_id`.
工具呼叫交由客戶端執行，再以工具訊息及對應識別碼回傳結果。
工具调用交由客户端执行，再以工具消息及对应标识码回传结果。

`stream: true` emits text during inference and structured tool calls when complete. `stream_options.include_usage` adds usage. Closing the connection cancels the native prompt. Other OpenAI features are not promised.
串流於推理中輸出文字，完成時輸出結構化工具呼叫；可附用量。關閉連線會取消原生工作。
流式输出在推理中发送文字，完成时发送结构化工具调用；可附用量。关闭连接会取消原生任务。

Errors / 錯誤 / 错误: 400 invalid request, 429 queue full, 500 execution failure.
