# Caching / 快取 / 缓存

ComfyUI owns model lifetime. The runtime registry is weak; native cached node outputs retain weights. CPU tensors, quantization state and prefix snapshots are exposed to its RAM-pressure cache.
ComfyUI 擁有模型生命週期；弱引用登記不保留權重，原生節點快取負責持有。CPU 權重、量化狀態及前綴快照供 RAM 壓力快取計量。
ComfyUI 管理模型生命周期；弱引用注册不保留权重，由原生节点缓存持有。CPU 权重、量化状态及前缀快照供 RAM 压力缓存计量。

The launcher passes native cache headroom from `plugin/config/config.yaml`: 10 GiB active, 16 GiB inactive. Upstream's default inactive reserve can evict every previous workflow even with abundant free RAM.
啟動器使用上述設定的原生 10／16 GiB 餘量；上游預設 inactive 餘量可能在 RAM 充足時仍清掉舊工作流。
启动器使用上述配置的原生 10／16 GiB 余量；上游默认 inactive 余量可能在 RAM 充足时仍清掉旧工作流。

`/free` with `unload_models:true` offloads to RAM. Adding `free_memory:true` clears node caches and releases the runtime; the next call reloads weights.
僅卸載模型會搬到 RAM；同時清理記憶體會釋放節點快取及執行實例，下次重載權重。
仅卸载模型会搬到 RAM；同时清理内存会释放节点缓存及运行实例，下次重新加载权重。

Two CPU prefix snapshots per runtime retain exact token IDs, attention KV and hybrid recurrent states. Each request receives a fresh copy. HQQ quantization begins after joining the remaining prefill, preserving its initial full-precision attention.
每個實例最多兩份 CPU 前綴，記錄精確 token、注意力 KV 及混合遞迴狀態；請求各自複製。剩餘預填合併後才做 HQQ，保留初次注意力精度。
每个实例最多两份 CPU 前缀，记录精确 token、注意力 KV 及混合递归状态；请求各自复制。剩余预填合并后才做 HQQ，保留初次注意力精度。

Hybrid vision requests use full prefill: split prefill changed a near-tied token in converted Qwen9 BF16. Text/tool reuse and Gemma vision reuse remain enabled. `prefix_cache:false` disables reuse; `/llm/status` reports hits, CPU bytes and bypass reasons. Equivalence tests compare actual replies and tools.
混合模型的圖片請求保留完整預填，避免匯入 Qwen9 BF16 接近分數時改變輸出。文字／工具與 Gemma 視覺仍重用；可停用前綴，狀態列出命中、CPU 用量及略過原因。
混合模型的图片请求保留完整预填，避免导入 Qwen9 BF16 接近分数时改变输出。文字／工具与 Gemma 视觉仍复用；可停用前缀，状态列出命中、CPU 用量及跳过原因。

[Transformers cache documentation](https://huggingface.co/docs/transformers/kv_cache).
[Diagnostic / 診斷 / 诊断](prefix-probe.md).
