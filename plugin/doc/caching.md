# Caching / 快取 / 缓存

ComfyUI owns model lifetime. The runtime registry is weak; native cached node outputs retain weights. CPU tensors, quantization state and prefix snapshots are exposed to its RAM-pressure cache.
ComfyUI 擁有模型生命週期；弱引用登記不保留權重，原生節點快取負責持有。CPU 權重、量化狀態及前綴快照供 RAM 壓力快取計量。
ComfyUI 管理模型生命周期；弱引用注册不保留权重，由原生节点缓存持有。CPU 权重、量化状态及前缀快照供 RAM 压力缓存计量。

The launcher reserves 10/16 GiB active/inactive RAM via `plugin/config/config.yaml`.
啟動器依上述設定預留原生 RAM 餘量 10／16 GiB。
启动器依上述配置预留原生 RAM 余量 10／16 GiB。

`/free` with `unload_models:true` offloads to RAM. Adding `free_memory:true` clears node caches and releases the runtime; the next call reloads weights.
僅卸載模型會搬到 RAM；同時清理記憶體會釋放節點快取及執行實例，下次重載權重。
仅卸载模型会搬到 RAM；同时清理内存会释放节点缓存及运行实例，下次重新加载权重。

Two CPU snapshots retain token IDs, math policy, attention KV and recurrent state. Each request restores a copy. HQQ starts after joining the suffix.
兩份 CPU 快照記錄 token、精度、KV 及遞迴狀態；每次還原副本，合併後才做 HQQ。
两份 CPU 快照记录 token、精度、KV 及递归状态；每次恢复副本，合并后才做 HQQ。

Qwen vision uses NF4/BF16 on CUDA with any KV setting. Prefill MLP output projections use FP32; HQQ4 uses all MLP projections. Text/vision snapshots have separate math keys. ComfyUI reserves scratch space. Other hybrid-vision settings keep full prefill. Text/tool and Gemma vision reuse remain enabled.
Qwen 視覺支援 CUDA／NF4／BF16 及三種 KV 設定；預填的 MLP 輸出投影用 FP32，HQQ4 則用全部投影。文字視覺快照分開，空間由 ComfyUI 預留；其他混合視覺設定完整預填。
Qwen 视觉支持 CUDA／NF4／BF16 和三种 KV 配置；预填的 MLP 输出投影用 FP32，HQQ4 则用全部投影。文本视觉快照分开，空间由 ComfyUI 预留；其他混合视觉配置完整预填。

`prefix_cache:false` disables reuse, retaining vision prefill precision. `/llm/status` reports hits, CPU bytes, math policy and bypass reasons. Tested speedups depend on the prompt and hardware; model answers are not universally exact.
停用前綴仍保留視覺預填精度；狀態列出命中、CPU 用量、精度及略過原因。加速依提示與硬體而異，不保證模型永遠正確。
停用前缀仍保留视觉预填精度；状态列出命中、CPU 用量、精度及跳过原因。加速取决于提示和硬件，不保证模型永远正确。

[Transformers cache documentation](https://huggingface.co/docs/transformers/kv_cache).
[Diagnostic / 診斷 / 诊断](prefix-probe.md).
