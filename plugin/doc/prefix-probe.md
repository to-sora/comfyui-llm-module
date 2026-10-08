# Prefix diagnostic / 前綴診斷 / 前缀诊断

Production Qwen vision reuse supports CUDA, NF4 weights, BF16 compute and all KV settings. Other hybrid-vision modes keep full prefill. See [caching](caching.md).
正式 Qwen 視覺重用支援 CUDA／NF4／BF16及三種 KV 設定；其他混合視覺設定保留完整預填，詳見快取文件。
正式 Qwen 视觉复用支持 CUDA／NF4／BF16及三种 KV 配置；其他混合视觉配置保留完整预填，详见缓存文档。

`diagnostic_prefix` compares full/split states and full/restored/reused decoding through ComfyUI. Limits: Qwen, 64+ static prefix tokens, <=2048 input tokens and <=64 diagnostic reply tokens. The API answer still runs normal inference. Use `prefix_cache:false` for a full-prefill baseline.
上述診斷由 ComfyUI 執行並預留額外空間；限制如上。API 仍正常推論，可停用快取建立完整預填基準。
上述诊断由 ComfyUI 执行并预留额外空间；限制如上。API 仍正常推理，可停用缓存建立完整预填基准。

Modes / 模式 / 模式:

- `default`, `full_accumulation`, `math_attention`, `fixed_reduction`
- `fp32_projection`, `fp32_default_attention`: all quantized projections.
- `prefix_fp32`: saved prefix only.
- `prefill_fp32`, `prefill_fp16`: multi-token prefill only.
- `attention_fp32`, `mlp_fp32`, `mlp_down_fp32`, `mlp_gateup_fp32`: selected prefill projections.
- `head_fp32`: retain FP32 output logits.
- `dense_prefill`: dequantized dense prefill.

精度模式選擇投影及預填範圍；退出時還原掛鉤、運算旗標、精度、偏置及方法。
精度模式选择投影和预填范围；退出时恢复钩子、运算标志、精度、偏置和方法。

`/llm/status` → `diagnostics.prefix_probe.decode` records tokens, text, tool calls and timings including CPU snapshot restoration. Cold prefix construction is separate. Equal outputs alone do not establish correctness: both may call the wrong tool.
狀態含實際 token、工具及含還原的時間；首次建立另計。輸出相同不代表正確，兩者可能同樣誤用工具。
状态含实际 token、工具及含恢复的时间；首次建立另计。输出相同不代表正确，两者可能同样误用工具。

Run / 執行 / 执行:

```sh
server/.local-tool-app/venv/bin/python -m plugin.src.test.prefix_selective_benchmark
server/.local-tool-app/venv/bin/python -m plugin.src.test.prefix_vision_accept
```

Evidence / 證據 / 证据: `fan-out/studio-engine`.
[PyTorch numerics](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html)
