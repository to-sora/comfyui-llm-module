# Formats · 格式 · 格式

| Checkpoint | Backend | Dependency profile |
|---|---|---|
| Qwen2, Qwen2.5, Qwen3, Qwen3.5, Qwen3.6; dense/MoE | transformers | core |
| Qwen2-VL, Qwen2.5-VL, Qwen3-VL, Qwen3.5/3.6 vision | transformers | core |
| FP32 / FP16 / BF16 safetensors | transformers | core |
| bitsandbytes INT8 / NF4 / FP4 | transformers | bnb |
| GPTQ / AWQ checkpoints | transformers | gptq |
| HQQ / Quanto / compressed-tensors / torchao | transformers | hqq / quanto / compressed / torchao |
| FP8 / MXFP4 and other Transformers quantizers | transformers | checkpoint kernel dependencies |
| GGUF Q2–Q8, K-quants, IQ-quants | gguf | gguf |
| GGUF vision | gguf + matching mmproj | gguf |
| EXL2 text | exl2, CUDA | exl2 |

```bash
bash plugin/install-local-app-build.sh bnb
QWEN_CUDA=ON bash plugin/install-local-app-build.sh gguf
```

For prequantized tensor checkpoints select `quantization=auto`; the model's
quantization metadata selects its loader. NF4/FP4/INT8 quantize dense weights
during loading. GGUF uses its embedded chat template and llama.cpp kernels.
Architecture and accelerator support depend on the selected upstream backend.

預量化 tensor 選擇 `auto`，由模型量化資料選擇載入器。
NF4／FP4／INT8 在載入時量化。GGUF 沿用模型聊天模板及 llama.cpp 核心。
架構與加速器相容性由後端決定；驗收結果限定所選模型與格式。

预量化 tensor 选择 `auto`，由模型量化资料选择加载器。
NF4／FP4／INT8 在加载时量化。GGUF 沿用模型聊天模板及 llama.cpp 核心。
架构与加速器兼容性由后端决定；验收结果限定所选模型与格式。

Original Qwen/Qwen-VL adapters and EXL2 vision remain in `todo.txt`.
Qwen3.6-35B-A3B uses Qwen3.5 MoE architecture; its memory requirement exceeds
the default Colab acceptance model.

第一代 Qwen／Qwen-VL 與 EXL2 視覺列於待完成項目；EXL2 文字適配器待 GPU 驗收。
第一代 Qwen／Qwen-VL 与 EXL2 视觉列于待完成项目；EXL2 文字适配器待 GPU 验收。

Sources / 來源 / 来源:
[Qwen3.6](https://huggingface.co/Qwen/Qwen3.6-35B-A3B),
[Quantizers](https://huggingface.co/docs/transformers/quantization/overview),
[llama.cpp](https://github.com/ggml-org/llama.cpp).
