# Gemma E2B / Gemma E2B / Gemma E2B

The supplied directory contains pretrained weights without a chat template. Applying the instruction-tuned model's template caused repetition and failed vision/tool checks, even without quantization.
指定目錄是沒有對話範本的預訓練權重。套用指令微調版範本會重複文字，未量化時仍未通過視覺與工具測試。
指定目录是没有对话模板的预训练权重。套用指令微调版模板会重复文本，未量化时仍未通过视觉与工具测试。

`gemma-base.jinja` provides question/answer demonstrations and JSON tool syntax. Images precede text; generation stops at the next conversation label. The model weights are unchanged. Other Gemma checkpoints retain their native chat template.
上述範本提供問答示例及 JSON 工具格式，圖片置於文字前，遇下一個對話標記便停止。模型權重不變；其他 Gemma 模型沿用原生範本。
上述模板提供问答示例及 JSON 工具格式，图片置于文本前，遇下一个对话标记便停止。模型权重不变；其他 Gemma 模型沿用原生模板。

Use `tool_choice: "required"` or a named function when a tool call is mandatory. This prefills the tool delimiter; the model still generates the function name and arguments. With `auto`, the model can answer directly.
必須呼叫工具時，使用上述設定或指定函式。模組預填工具分隔標記，函式名稱與參數仍由模型生成；auto 可直接回答。
必须调用工具时，使用上述配置或指定函数。模块预填工具分隔标记，函数名称与参数仍由模型生成；auto 可直接回答。

Verified: actual NF4 weights, HQQ 4/8-bit KV, colors, arithmetic, weather/multiply tools, tool results, an 816-token document, native Firefox nodes, and SDXL eviction/reload. These bounded checks do not guarantee every model answer.
已實測 NF4、4／8 位元 KV、辨色、算術、天氣／乘法工具、工具結果、816 token 文件、Firefox 節點及 SDXL 卸載重載。驗證案例不代表所有回答均正確。
已实测 NF4、4／8 位元 KV、辨色、算术、天气／乘法工具、工具结果、816 token 文档、Firefox 节点及 SDXL 卸载重载。验证案例不代表所有回答均正确。
