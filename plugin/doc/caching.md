# Caching / 快取 / 缓存

One LLM stays resident. Only another LLM selection can release it. SDXL, node-cache clearing and GPU offload retain its weights. ComfyUI decides GPU placement. Context, KV and sampling changes reuse the owner. R2 receipts survive replacement: returning to retired A after A→B requires restarting ComfyUI; a second disk read is refused.

同時常駐一個 LLM，只有另一 LLM 才可替換。SDXL、清節點快取與 GPU 卸載保留權重；GPU 由 ComfyUI 管理。上下文、KV 與取樣共用物件。R2 帳本不清除，切回已釋放模型須重啟。

同时常驻一个 LLM，仅另一 LLM 可替换。SDXL、清节点缓存及 GPU 卸载保留权重；GPU 由 ComfyUI 管理。上下文、KV 与采样共用对象。保留 R2 账本，切回已释放模型须重启。

The launcher uses native `--cache-lru 1`. `LLMManagedCheckpoint` returns native model/CLIP/VAE objects and their owner. Active turns retain shared references: `PUT /llm/turns/{token}` with `checkpoints:[names]`; `DELETE` releases only that turn. Another turn keeps the same objects alive. Idle SDXL entries can be evicted natively and reread in later turns. LLM reads remain once per process.

採原生 LRU 1；當輪租約保留 SDXL，其他請求可共用。刪除單一租約不影響其他請求。閒置 SDXL 可由原生快取淘汰，下輪可重讀；LLM 仍每次程序只讀一次。

使用原生 LRU 1；当轮保留 SDXL，其他请求可共享。删除一个租约不影响其他请求。闲置 SDXL 可由原生缓存淘汰，下轮可重读；LLM 仍每个进程只读一次。

Two CPU prefix snapshots retain tokens, attention KV and recurrent state. Each request restores a copy before suffix processing and HQQ. Qwen vision uses BF16/CUDA with selective FP32 prefill and separate math keys. `prefix_cache:false` disables reuse. Status reports hits, storage and bypass reasons. See [vision settings](vision-prefix.md).

兩份 CPU 前綴快照保存 token、KV 與遞迴狀態，還原副本後處理後綴及 HQQ；視覺精度與限制見連結。狀態提供命中、用量與略過原因。

两份 CPU 前缀快照保存 token、KV 和递归状态，恢复副本后处理后缀及 HQQ；视觉精度与限制见链接。状态提供命中、用量与跳过原因。
