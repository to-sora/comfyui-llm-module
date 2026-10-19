# Flow comparison / 流程比對 / 流程对比

Requested: 9B/27B × HF/GGUF origin, 25 rounds each. Every round uses three real thinking/tool responses and 2/1/2 SDXL images. The LLM chooses its pair each round; later messages receive actual pixels. The matrix is running; partial results do not establish completion.

| Requirement | Implementation |
|---|---|
| Four profiles | Qwen3.5-9B, Qwen3.5-9B-gguf, Qwen3.8-27B-OBLITERATED (HF), Qwen3.8-27B (GGUF import). Existing NF4 caches; no reconversion. |
| One LLM | Only another LLM selection retires it; SDXL preserves it. One ComfyUI PID for the matrix. |
| R2 | Source and representation receipts survive retirement. LLM sources read once. Retired A cannot reload after A→B without restarting. |
| SDXL pair | Detected enums and per-image selection; active-turn leases retain native outputs across requests. Idle entries use native LRU eviction. |
| Limits | Thinking, 35000 context, 12000 maximum output, 16000 maximum tokens per image, NF4/BF16/HQQ8. Actual input plus output must fit context; maxima need not be filled. |
| Basic flow | 512×512, 28 steps; 500 images plus four independent shared-retention requests. |
| RAM | 80 GB plan, 35 GB LLM cap, 16 GB SDXL cap, 20 GiB usual headroom, 8 GiB hard floor. Test cancels below 12 GiB planned availability. |

Run `server/.local-tool-app/venv/bin/python -B -m server.src.test.flow_api_matrix`. Evidence: `fan-out/studio-chat/flow-api-progress.json` and compressed per-round records. Repairs are counted separately. Settings are checked in three Firefox layouts. No mocked inference. Do not restart ComfyUI within a claimed run.

繁中：三個明確訊息對應六步流程，LLM 每輪選兩模型並查看真實圖片。四組各 25 輪仍執行中，未宣稱完成。單一 LLM 常駐，只有替換 LLM 可釋放，讀取帳本保留。各 token 上限可同時設定，實際總量須符合上下文。基本圖 512；記錄 RAM、參數及工具修復。

简中：三个明确消息对应六步流程，LLM 每轮选两个模型并看实际图片。四组各 25 轮仍在运行，未宣称完成。单一 LLM 常驻，仅更换 LLM 可释放，保留读取记录。各 token 上限可同时配置，实际总量须符合上下文。基本图片 512；记录 RAM、参数及工具修复。
