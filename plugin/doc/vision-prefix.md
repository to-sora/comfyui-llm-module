# Vision prefixes / 視覺前綴 / 视觉前缀

Qwen vision reuse requires CUDA and BF16 compute. NF4 supports all four supplied Qwen profiles. FP4 requires `fp4_vision_prefix: true` in the model profile; only imported 27B and native 27B OBLITERATED are enabled. KV may be none, HQQ8 or HQQ4.
Qwen 視覺重用要求 CUDA／BF16。NF4 支援四款 Qwen；FP4 需模型設定上述旗標，只啟用匯入二百七十億及原生 OBLITERATED。KV 可選三種設定。
Qwen 视觉复用要求 CUDA／BF16。NF4 支持四款 Qwen；FP4 需模型配置上述标志，只启用导入二百七十亿及原生 OBLITERATED。KV 可选三种配置。

During multi-token prefill, MLP output projections use FP32; HQQ4 uses all MLP projections. Single-token decode retains configured compute. This also applies when `prefix_cache:false` or no static system prefix exists. ComfyUI accounts for workspace and CPU snapshots.
多 token 預填的 MLP 輸出投影用 FP32；HQQ4 則用全部 MLP 投影。單 token 解碼保留原精度；停用快取或沒有系統前綴仍用此策略，空間由 ComfyUI 計量。
多 token 预填的 MLP 输出投影用 FP32；HQQ4 则用全部 MLP 投影。单 token 解码保留原精度；停用缓存或没有系统前缀仍用此策略，空间由 ComfyUI 计量。

Other hybrid-vision combinations use full prefill. Both 9B FP4 profiles and imported 9B NF4/FP16 failed actual colour/tool-context requests, including uncached replies. Imported 9B FP4 passed the long-system matrix but failed shorter prompts. Equal full/cached answers do not prove correctness.
其他混合視覺設定完整預填。兩款九十億 FP4、匯入九十億 NF4／FP16 的顏色與工具上下文有錯，完整預填亦會失敗；匯入 FP4 長系統提示通過、短提示失敗，同答不等同答對。
其他混合视觉配置完整预填。两款九十亿 FP4、导入九十亿 NF4／FP16 的颜色与工具上下文有错，完整预填也会失败；导入 FP4 长系统提示通过、短提示失败，同答不等于答对。

Measured gains are prompt/hardware dependent. API evidence, timings and failures are in `fan-out/studio-engine`; browser UAT is in `fan-out/studio-chat`. See [diagnostics](prefix-probe.md) and [memory ownership](caching.md).
加速依提示與硬體而異；上述目錄保存 API、效能、失敗及瀏覽器證據。
加速取决于提示与硬件；上述目录保存 API、性能、失败及浏览器证据。
