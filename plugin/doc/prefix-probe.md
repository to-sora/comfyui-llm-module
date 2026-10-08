# Prefix diagnostic / 前綴診斷 / 前缀诊断

Optimization 8 remains partial. Qwen image requests use full prefill because split prefill changed a near-tied token and caused an unrelated tool call. Text/tool prefix reuse and Gemma vision reuse remain enabled.
最佳化第八項仍部分完成。Qwen 圖片請求維持完整預填，因分段運算改變接近分數的 token 並造成無關工具呼叫；文字、工具及 Gemma 視覺仍重用前綴。
优化第八项仍部分完成。Qwen 图片请求保持完整预填，因分段运算改变接近分数的 token 并造成无关工具调用；文字、工具及 Gemma 视觉仍复用前缀。

For development, add `diagnostic_prefix` to a completion request: `default`, `full_accumulation`, `math_attention`, or `fixed_reduction`. It compares full/split prefill inside the ComfyUI-owned engine; results appear under `/llm/status` → `diagnostics.prefix_probe`. It adds several forward passes, requires Qwen, a 64-token system prefix and at most 1024 input tokens. The returned answer still uses normal inference.
開發時可加入上述診斷選項；ComfyUI 管理的引擎執行完整／分段比較，結果見狀態 API。額外執行數次前向運算，限 Qwen、至少 64-token 系統前綴及最多 1024 輸入 token；回覆仍走一般推論。
开发时可加入上述诊断选项；ComfyUI 管理的引擎执行完整／分段比较，结果见状态 API。额外执行数次前向运算，限 Qwen、至少 64-token 系统前缀及最多 1024 输入 token；回复仍走正常推理。

Run `server/.local-tool-app/venv/bin/python -m plugin.src.test.prefix_diagnostic Qwen3.5-9B-gguf`, or use `Qwen3.5-9B`. Evidence goes to `fan-out/studio-engine`. Native/imported NF4 BF16 both diverged before snapshot restoration; stricter math did not eliminate the difference. Probe hooks and backend settings are restored on exit.
以上命令重現原生／匯入 NF4 BF16 差異；快照還原前已不同，較嚴格數學設定亦未消除。離開診斷時清理掛鉤並還原設定。
以上命令重现原生／导入 NF4 BF16 差异；快照恢复前已不同，更严格的数学设置也未消除。退出诊断时清理钩子并恢复设置。

[PyTorch numerical accuracy](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html) explains why sliced and full floating-point operations need not be bit-identical.
PyTorch 說明切片與完整浮點運算不保證逐位相同。
PyTorch 说明切片与完整浮点运算不保证逐位相同。
