# Models / 模型 / 模型

Profiles: `plugin/config/content-config/models.yaml`.
模型路徑、格式及量化預設值設定於上述檔案。
模型路径、格式和量化默认值配置于上述文件。

HF accepts a local model directory or Hugging Face repository ID. Remote Python code is disabled.
HF 接收本機目錄或 Hugging Face 儲存庫 ID，停用遠端 Python 程式碼。
HF 接收本地目录或 Hugging Face 仓库 ID，禁用远程 Python 代码。

Weight quantization: `bnb_nf4`, `bnb_fp4`, `bnb_int8`, `none`, `auto`.
權重量化於載入時執行；auto 沿用模型既有量化設定。
权重量化在加载时执行；auto 沿用模型已有量化配置。

HF KV: `none`, `hqq_8`, `hqq_4`. Attention caches are quantized; recurrent states retain their native precision.
HF KV 可設定不量化、8 或 4 位元。注意力快取會量化，循環狀態保留原生精度。
HF KV 可配置不量化、8 或 4 位元。注意力缓存会量化，循环状态保留原生精度。

GGUF weights use their stored quantization; KV supports `none`, `q8_0`, `q4_0`.
GGUF 沿用檔案內權重量化，KV 可設定上述精度；視覺模型需要配對 mmproj。
GGUF 沿用文件内权重量化，KV 可配置上述精度；视觉模型需要配对 mmproj。

The supplied Qwen3.8-27B folder contains an obliterated GGUF model; the HF folder identifies its architecture as qwen3_5.
指定的 Qwen3.8-27B 目錄含 obliterated GGUF；HF 目錄的架構標示為 qwen3_5。
指定的 Qwen3.8-27B 目录含 obliterated GGUF；HF 目录的架构标识为 qwen3_5。

The supplied Gemma E2B appears pretrained and has no chat template. Chat support is pending template/model clarification.
現有 Gemma E2B 顯示為預訓練版本，沒有對話範本；對話支援待確認範本或模型。
现有 Gemma E2B 显示为预训练版本，没有对话模板；对话支持待确认模板或模型。
