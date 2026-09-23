# Formats / 格式 / 格式

Backend dispatch uses checkpoint configuration, including Qwen3.5/3.6 dense and MoE.
後端依模型設定辨識架構，涵蓋 Qwen3.5／3.6 dense 與 MoE 的載入路徑。
后端依模型配置识别架构，涵盖 Qwen3.5／3.6 dense 与 MoE 的加载路径。

| Format / 格式 | Route / 路徑 / 路径 |
|---|---|
| Safetensors, PyTorch | Transformers auto classes |
| NF4, FP4, INT8 | `install-quant.sh bnb`; `bnb_nf4/bnb_fp4/bnb_int8` |
| AWQ, GPTQ | `install-quant.sh awq/gptq`; `auto` |
| HQQ, Quanto | `install-quant.sh hqq/quanto`; `auto` or live quantization |
| Compressed tensors | `install-quant.sh compressed`; `auto` |
| FP8, MXFP4, other HF quantizers | checkpoint metadata; backend/hardware dependencies |
| GGUF Q/K/IQ | `install-gguf.sh`; llama.cpp |

Commands above are under `plugin`. Prequantized checkpoints use `auto`.
上述指令位於 `plugin`。預量化模型選擇 `auto`，由原生後端讀取量化設定。
上述命令位于 `plugin`。预量化模型选择 `auto`，由原生后端读取量化配置。

GGUF model input: local file or `owner/repo::filename.gguf`; vision also requires mmproj.
GGUF 接受本機檔案或上述下載格式；視覺模型須配置對應 mmproj。
GGUF 接受本地文件或上述下载格式；视觉模型须配置对应 mmproj。

Model/hardware combinations require acceptance. Coverage gaps are in `todo.txt`.
模型與硬體組合仍需驗收，涵蓋缺口列於待辦。
模型与硬件组合仍需验收，覆盖缺口列于待办。

Sources / 來源 / 来源:
- https://huggingface.co/Qwen/Qwen3.5-0.8B
- https://huggingface.co/Qwen/Qwen3.6-35B-A3B
- https://github.com/huggingface/transformers/tree/v5.17.0
- https://github.com/abetlen/llama-cpp-python/tree/v0.3.35
- https://github.com/googlecolab/backend-info
