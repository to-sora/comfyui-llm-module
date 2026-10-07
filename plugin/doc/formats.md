# Models / 模型 / 模型

All five profiles in `config/content-config/models.yaml` run on transformers.
五個設定模型均透過 transformers 執行。
五个配置模型均通过 transformers 运行。

HF accepts local folders or repository IDs; remote Python code is disabled.
HF 接收本機目錄或儲存庫 ID，停用遠端 Python 程式碼。
HF 接收本地目录或仓库 ID，禁用远程 Python 代码。

Weights: `bnb_nf4`, `bnb_fp4`, `bnb_int8`, `none`, `auto`. Compute precision: `bfloat16` or `float16`. NF4 is saved once under `data/quantized`; aliases reuse the same source cache.
權重量化及計算精度可分別設定；NF4 保存在上述目錄，相同來源的別名共用快取。
权重量化和计算精度可分别设置；NF4 保存在上述目录，相同来源的别名共享缓存。

KV: `none`, `hqq_8`, `hqq_4`. Attention caches are quantized; recurrent states retain their native precision.
注意力 KV 可不量化、8 或 4 位元；循環狀態保留原生精度。
注意力 KV 可不量化、8 或 4 位元；循环状态保留原生精度。

GGUF is an offline import format. See [import instructions](import.md). Original GGUF and mmproj files remain untouched. llama.cpp is used only as a parity reference, never for serving.
GGUF 先離線匯入；原始模型及投影器保持不變，llama.cpp 僅作一致性參考。
GGUF 先离线导入；原始模型和投影器保持不变，llama.cpp 仅作一致性参考。

The converted 9B/27B profiles passed strict tensors, tokenizer, template, logits, vision and FP16/NF4 tool–SDXL workflows before switching. Imported repos live in `data/imported` and exceed the 1 GB storage target.
9B／27B 通過張量、分詞、範本、數值、視覺及兩種精度工作流程後才切換；匯入權重超過 1 GB 目標。
9B／27B 通过张量、分词、模板、数值、视觉和两种精度工作流后才切换；导入权重超过 1 GB 目标。

The supplied 27B GGUF identifies itself as obliterated; the profile name does not change its weights. The pretrained Gemma profile was replaced by the existing local `gemma-3-12b-it` instruction model.
指定 27B GGUF 本身為 obliterated，名稱不改變權重；Gemma 改用本機既有指令模型。
指定 27B GGUF 本身为 obliterated，名称不改变权重；Gemma 改用本地已有指令模型。
