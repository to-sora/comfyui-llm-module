# Flow comparison / 流程比對 / 流程对比

Requested: four runs (9B/27B × HF/GGUF-origin), 25 rounds each. Each round has three LLM calls and five images, with two SDXL checkpoints chosen by the LLM at runtime. That is 100 rounds, 300 LLM calls and 500 images, excluding repairs or extra final reviews. This matrix has **not passed**; the completed short regression is separate.

| Requirement | Current state |
|---|---|
| Four formats | Profiles exist: Qwen3.5-9B, Qwen3.5-9B-gguf, Qwen3.8-27B-OBLITERATED (HF), Qwen3.8-27B (GGUF import). No new conversion needed for existing NF4 caches. |
| Thinking plus tools | Gateway accepts thinking; Studio forces it off. Missing Studio control and thinking/tool acceptance. |
| LLM selects two checkpoints each round | Tools expose styles, not the full checkpoint enum. Missing per-call selection and pair reuse. |
| SDXL retained during the round and other use | Current strong lifetime cache has a 14 GB cap. Arbitrary rotation will be refused. Needs native-cache integration with active-use retention; lifetime retention is not a rotating cache. |
| 35k context, 12k output | Numeric settings accept 35000/12000. This combination was not exercised by the short test. A maximum is not a requirement to generate 12000 tokens. |
| 16k image tokens | No explicit token budget; Studio currently sends 512-pixel previews. Need an aggregate image budget and actual processor-token accounting. |
| LLM read once/offload | Short multi-message cycle passed; failure rollback and auto/cuda:0 reuse passed. Not 25-round evidence. |

If 16k means **per image**, two maximum-size image inputs plus 12k output need at least 44k tokens before text/tools: they cannot fit a 35k context. Use a combined 16k image budget per request, or change those limits. Exact token counts must be reported.

Four cached NF4 representations total approximately 51.6 GB before overhead, exceeding the 35 GB LLM cap. Four separate processes can test one profile each; no restart is allowed within a 25-round run. Do not enlarge the RAM budget to fit the matrix.

繁中：新增流程尚未通過。缺少 Studio thinking、逐工具 checkpoint 選擇、跨輪 SDXL 快取輪替及圖片 token 預算。現有短測試只證明跨訊息保留、原生卸載恢復、失敗額度回收及裝置別名共用。四組應分開執行，每組 25 輪內不得重啟；全部四份常駐超過額度。兩圖各 16k 加輸出 12k 無法放入 35k；需以每次請求合計圖片預算規劃。

简中：新增流程尚未通过。缺少 thinking、工具选模型、SDXL 跨轮缓存和图片 token 预算。短测不能代替四组各 25 轮。每组进程内禁止重启重读；四份权重超出额度。两图各 16k 加 12k 输出超过 35k 上下文。
