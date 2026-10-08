# Prefix diagnostic / 前綴診斷 / 前缀诊断

Optimization 8 remains partial. Production Qwen vision uses full prefill after split prefill added an unrelated tool call. Text/tool and Gemma vision prefix reuse remain enabled.
最佳化第八項仍部分完成；Qwen 視覺分段預填曾產生無關工具呼叫，因此正式路徑保留完整預填。文字、工具及 Gemma 視覺仍重用前綴。
优化第八项仍部分完成；Qwen 视觉分段预填曾产生无关工具调用，因此正式路径保留完整预填。文字、工具及 Gemma 视觉仍复用前缀。

Development modes / 開發模式 / 开发模式 (`diagnostic_prefix`):

- `default`, `full_accumulation`, `math_attention`, `fixed_reduction`
- `fp32_projection`: FP32 quantized projections with math attention.
- `fp32_default_attention`: FP32 projections with normal attention.
- `prefix_fp32`: FP32 only while preparing the saved prefix.
- `prefill_fp32`: FP32 prefill; normal single-token decoding.
- `dense_prefill`: dense prefill; normal token decoding.

FP32 模式調整注意力與前綴／預填精度。
FP32 模式调整注意力与前缀／预填精度。

ComfyUI compares full/split states and full/restored/reused decoding. Limits: Qwen, at least 64 prefix tokens, at most 2048 input tokens and 64 diagnostic reply tokens. Extra workspace is reserved through ComfyUI. The API answer still uses normal inference. Hooks, math flags, projection precision and bias dtype are restored on exit.
ComfyUI 管理模型、工作記憶體及完整／還原／重用比較；限制如上。API 仍回傳一般推論結果；離開時還原掛鉤、運算旗標、投影精度及偏置型別。
ComfyUI 管理模型、工作内存及完整／还原／复用比较；限制如上。API 仍返回正常推理结果；退出时恢复钩子、运算标志、投影精度及偏置类型。

Read `/llm/status` → `diagnostics.prefix_probe.decode`: tokens, text, tool calls and timings. `timing_includes_cache_setup` identifies timings including CPU snapshot restoration. Equal outputs alone do not prove correctness: two paths can make the same wrong tool call.
狀態 API 記錄 token、文字、工具及時間；上述旗標標示包含 CPU 快照還原。輸出一致不代表正確，兩條路徑可能同樣誤用工具。
状态 API 记录 token、文字、工具及时间；上述标志表示包含 CPU 快照恢复。输出一致不代表正确，两条路径可能同样误用工具。

Run from the repo / 於儲存庫執行 / 在仓库执行：

```sh
server/.local-tool-app/venv/bin/python -m plugin.src.test.prefix_decode_research Qwen3.5-9B-gguf
server/.local-tool-app/venv/bin/python -m plugin.src.test.prefix_studio_research
```

Evidence / 證據 / 证据: `fan-out/studio-engine`.
[PyTorch numerics](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html) · [HF caching](https://huggingface.co/docs/transformers/cache_explanation)
