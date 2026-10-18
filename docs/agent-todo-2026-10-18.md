# 全自動實作 TODO（RAM 常駐、磁碟 I/O 受控）

給：在使用者本機（有 GPU、有模型）全自動執行的 coding agent。
背景與 bug 編號：`docs/review-2026-10-18.md`（本分支）。本 TODO 與該文件衝突時，以本 TODO 為準。
取得本文件：`git show origin/ccr-8b30e1be-fm3wnu:docs/agent-todo-2026-10-18.md`

---

## 0. 已實測與未實測（2026-10-18，雲端 CPU 環境，無 GPU）

已用真實檔案驗證（腳本在審查者的 scratchpad，結論如下）：

| 項目 | 結果 |
|---|---|
| 固定版本存在 | `transformers==5.18.0`、`llama-cpp-python==0.3.36`、`accelerate==1.15.0`、`kernels==0.17.2` 都能安裝 |
| transformers 5.18 的 GGUF 新路徑 | 只支援 `qwen35`、`qwen35moe`；會反轉 llama.cpp 的 5 種轉換（norm +1、`-exp(A_log)`、conv1d squeeze、value head 排列、改名），只有 `out_proj` 需要解量化，其餘保持 GGUF block（`quantizers/quantizer_gguf.py`、`integrations/gguf/gguf_conversion_mapping.py`） |
| 數值正確性 | Qwen3.5-0.8B Q4_K_M（lmstudio-community）同一組 28 token：transformers 對 llama.cpp top1 1.0、mean KL 0.0055、max KL 0.052，兩者都答 "42" |
| CPU 上的 packed 模式 | **沒有 kernel**（"no GGUF matmul kernel is published for this device"），transformers **自動改成整個模型解量化**。packed 模式只可能在 CUDA 上、且要能下載 hub kernel `ggml-org/ggml-quantization` |
| repo 的 mmproj 對照表 | 對真實 Qwen3.5-0.8B mmproj：153／153 個 vision 張量全部對上，無缺漏、無 shape 不符 |
| llama.cpp + memfd | stories15M Q4_0：從 `/proc/self/fd/N` 載入成功；第一次與重載 `read_bytes` 都是 0（只有複製進 memfd 時讀 19 MB）；權重顯示為 RssShmem 而非 RssAnon；`close()` 後 memfd 仍在；重載輸出相同。對照組（從磁碟路徑載入）讀了 19 MB，證明量測有效 |
| memfd 的 RAM 計量 | 2 GiB memfd → Shmem +2048 MiB、MemAvailable −2124 MiB，ComfyUI 的 `virtual_memory_available` 看得到 |
| `GgufHeader.from_file` | 有每個張量的 `nbytes`，可不讀權重算每層大小 |
| `MTMDChatHandler`（0.3.36） | 會用 GGUF 內的 chat template 並傳入 `tools`；但**每次請求都 `reset()` + `kv_cache_clear()`**，視覺請求沒有前綴重用 |
| `Llama.generate` 前綴重用 | 文字路徑會找最長共同前綴，但要 `llama_memory_seq_rm` 部分刪除；混合（遞迴）模型不支援時會整段重算 |
| `Llama.save_state()` | 會額外複製 `n_batch × vocab` 的 logits（Qwen 248k vocab ≈ 0.5 GB／份），前綴快照不能用它 |

未實測（必須在本機 GPU 先驗證，見 Step 7.0）：CUDA 上 hub kernel 能否取得與 packed 模式的速度與 VRAM；
memfd 載入在 CUDA 上的行為；混合模型在 llama.cpp 的實際前綴行為；所有 9B／27B 的數字。

---

## A. 不可違反的規則

| 編號 | 規則 |
|---|---|
| R1 | 模型從 GPU 卸載後必須留在 RAM。 |
| R2 | 同一次 ComfyUI 執行（啟動到結束）中，每份模型權重只從磁碟讀一次。 |
| R3 | 不修改 ComfyUI（`<repo>/../comfyui`）與 `civit_script` 的任何檔案；不 monkeypatch `comfy.*`、`execution`、`server` 的內部函式。 |
| R4 | 只透過現有接點整合 ComfyUI：`NODE_CLASS_MAPPINGS`、`PromptServer.instance.routes`、`comfy.model_management` 的 `load_models_gpu`／`unload_all_models`／`soft_empty_cache`／`get_free_memory`／`get_torch_device`／`throw_exception_if_processing_interrupted`、patcher duck-type 契約、`_comfy_cache_tensors`、ComfyUI 啟動參數。 |
| R5 | 機器 RAM 約 90 GB。開發與執行都以這個上限規劃，任何時候 `MemAvailable` 不得低於 8 GB。 |

## B. 已預先做好的決定（全自動，不要停下來問）

1. 安全性不處理（可信任 LAN）。
2. `/free` 帶 `free_memory:true` 時，LLM 權重**保留**在 RAM（符合 R1）。唯一的明確釋放方式是新增的
   `POST /llm/release` 與 `LLMRelease` 節點。
3. LLM 常駐 RAM 預算 `llm_ram_budget_gb: 45`（寫在 `plugin/config/config.yaml`）。超過就拒絕載入新模型並回報原因，
   不自動踢掉舊模型。
4. Path B（執行時載入 GGUF）有兩個候選，由 Step 7.0 的量測規則自動決定，不問使用者：
   **B-T**＝transformers 5.18 packed GGUF（與 ComfyUI 原生 RAM 卸載完全相容，優先）；**B-L**＝llama.cpp + memfd（備案）。
   profile 名稱固定用 `-gguf-runtime` 後綴，與既有 Path A 的 `Qwen3.5-9B-gguf` 區分：
   `Qwen3.8-27B-gguf-runtime`、`Qwen3.5-9B-gguf-runtime`。
5. 不重新匯入、不刪除、不重建：`plugin/data/imported/*`、`plugin/data/quantized/*`、`/mnt/DATA9/LLM_model/**`。
6. 匯入關卡強制檢查只套用在本次之後新產生的匯入（`import.json` 有 `gate_version` 欄位者），既有匯入只警告。
7. 不改系統設定（swap、ulimit、套件）；不執行 `sudo` 或 `plugin/.local-dep/installBuildTool.sh`。
8. 不刪分支、不合併到 `main`、不開 PR；只推送自己的工作分支。
9. 文件維持 repo 慣例：英文／繁中／簡中三語，小檔案（約 80 行內）。
10. 測試以 9B 為主（讀取量約 6 GB），27B 每條路徑在整個 TODO 中只完整跑一次。

## C. 停止條件（遇到就停止、寫報告、推送已完成部分）

- `MemAvailable` < 8 GB，或測試期間 swap 使用量持續上升。
- 存放 `plugin/data` 的磁碟可用空間 < 30 GB。
- 任何一個 GPU session 的 `read_bytes` 超過該 session 的預算（§D），或任何權重的 `disk_loads` > 1。
- 同一個 step 的 CUDA OOM 出現 2 次。
- 單元測試修 3 次仍失敗。
- Step 0 的 ComfyUI 相容性檢查不通過。

報告寫到 `fan-out/agent/report.md`（gitignored，只留本機）並在最後的 commit 訊息摘要結果。

## D. 磁碟 I/O 與 RAM 預算

RAM 規劃（估算，Step 0 與 S1 實測後更新 `fan-out/agent/ram-plan.json`）：

| 項目 | RAM |
|---|---|
| OS、ComfyUI、Studio、Python | ≈ 8 GB |
| SDXL 兩個 checkpoint（ComfyUI 自己快取） | ≈ 14 GB |
| ComfyUI inactive headroom（必須保持可用，否則 ComfyUI 開始清自己的快取） | 16 GB |
| 安全餘量 | 4 GB |
| **LLM 常駐預算** | **45 GB**（90 − 8 − 14 − 16 − 4 = 48，取 45） |

LLM 實際大小（估算）：Qwen3.8-27B NF4 ≈ 18 GB；Qwen3.5-9B NF4 ≈ 6 GB。
Path B 的大小：B-L＝GGUF + mmproj（27B ≈ 17.5 GB、9B ≈ 8.3 GB，一直常駐 RAM）；
B-T＝GGUF 大小 + 解量化的 `out_proj`（Σ linear-attention 層 `hidden × linear_num_value_heads × linear_value_head_dim × dtype bytes`）
+ mmproj（BF16）。27B 用 float32 時 `out_proj` 可能多出數 GB，必須依 config 算出，超過 VRAM 就改 bfloat16 或改用 B-L。

GPU session 規則：
- 一個 session＝ComfyUI 啟動一次到停止。plugin 程式碼改了才需要重啟；同一個 step 的程式碼改完再一次重啟。
- 每次重啟的代價是重讀用到的模型與 SDXL。
- 每個 session 的讀取預算：`Σ(本 session 第一次用到的權重檔大小) × 1.05 + 3 GB`（函式庫、tokenizer、checkpoint header）。
  檔案大小用 `stat` 取得，**不可讀檔計算 hash**。
- 離線重度工具（`plugin.src.importer.*` 的 parity）只能在 ComfyUI 停止時執行，且同時間只跑一個。

---

## Step 0：前置檢查（唯讀）

- [ ] 建分支：`git fetch origin && git switch -c feat/ram-resident-llm origin/feat/studio-chat-engine`
- [ ] 新增 `tools/preflight.py`（用 plugin venv 執行），輸出 `fan-out/agent/preflight.json`：
  - `/proc/meminfo` 的 MemTotal、MemAvailable、SwapTotal、SwapFree（swap 只記錄，不改）。
  - `nvidia-smi --query-gpu=name,memory.total --format=csv`；沒有 GPU 就進入「無 GPU 模式」：只做程式碼與單元測試，所有 GPU session 標記 pending。
  - `shutil.disk_usage(plugin/data)`。
  - `<repo>/../comfyui` 的 `git rev-parse HEAD`，以及下列符號存在（不存在就停止）：
    `comfy_execution/caching.py` 內的 `_comfy_cache_tensors` 與 `class RAMPressureCache`；
    `comfy/cli_args.py` 的 `--cache-ram` 為 `nargs='*'`；`comfy/model_management.py` 的 `def load_models_gpu(` 含
    `memory_required`、`def ensure_pin_budget`。
  - `civit_script/start.sh` 是否加上 `--high-ram`、`--cache-classic`、`--cache-none`（有就停止並回報，不修改它）。
  - ComfyUI venv 的 `torch.__version__`、`torch.version.cuda`、GPU compute capability（hub kernel 是否有對應版本取決於這些）。
  - Studio 瀏覽器測試需要 `~/UAT-firefox/firefox/firefox`；不存在就把所有 Studio 瀏覽器測試標記 skipped，不停止。
  - `models.yaml` 每個 profile 的 NF4 快取是否已存在（`plugin/data/quantized/*/source.txt` 對應）。不存在的 profile 不可在測試中使用（會觸發 54 GB 讀取 + 15 GB 寫入）。
- [ ] commit：`chore: add agent preflight checks / 新增代理前置檢查`

## Step 1：I/O 與記憶體量測工具

- [ ] 新增 `plugin/src/test/io_probe.py`：
  - 以 `processes.listeners(port)` 找到 ComfyUI 的 Python PID（不要用 `service.json`，那是 launcher 的子程序）。
  - 讀 `/proc/<pid>/io` 的 `read_bytes`、`write_bytes`；`/proc/meminfo` 的 MemAvailable、Shmem、Swap。
  - `Budget` context manager：進入時記錄、離開時斷言 `read_bytes` 增量 ≤ 預算，並把結果附加到 `fan-out/agent/io.jsonl`。
- [ ] `/llm/status` 每個權重項目回報 `disk_loads`（邏輯載入次數）。R2 需要兩個都成立：`disk_loads == 1` 且 `read_bytes` 在預算內
  （page cache 命中時 `read_bytes` 不增加，所以只看 `read_bytes` 會誤判通過）。
- [ ] 單元測試：對自己的 PID 讀 `/proc/self/io` 成功、預算超出時拋出 AssertionError。
- [ ] commit。

## Step 2：無 GPU 單元測試基礎（review T-0.1）

- [ ] 在兩個 venv 安裝 pytest（固定版本，寫入新的 `plugin/requirements-dev.txt`、`server/requirements-dev.txt`）：
  `plugin/.local-tool-app/venv/bin/python plugin/src/main/pip_ipv4.py install -r plugin/requirements-dev.txt`
- [ ] `plugin/src/unit/conftest.py`：ComfyUI 不可匯入時，在 `sys.modules` 放入最小的 `comfy.model_management` 假模組
  （`throw_exception_if_processing_interrupted`、`load_models_gpu`、`get_torch_device` 等 no-op）。只在單元測試用。
- [ ] 測試對象：`tool_calls.parse`、`gemma_tools.arguments`、`stream_text.VisibleText`、`model_response.parse`、
  `messages.normalize`、`plain_template.adapt`、`protocol.validate`、`request_options.validate`、`registry.options`（暫存 config 目錄）；
  server 端 `history_repair.completed`、`stream_parse.merge`、`ids.new`、`generation.source_size`、`Store`（暫存 SQLite）。
- [ ] 指令（之後每個 step 都要跑）：
  `PYTHONDONTWRITEBYTECODE=1 plugin/.local-tool-app/venv/bin/python -m pytest -q -p no:cacheprovider plugin/src/unit`
  `PYTHONDONTWRITEBYTECODE=1 server/.local-tool-app/venv/bin/python -m pytest -q -p no:cacheprovider server/src/unit`
- [ ] commit。

## Step 3：強引用權重 registry（R1、R2 的核心；review T-4.1、B-R1、B-R2、B-P1、B-C1）

- [ ] 新增 `plugin/src/main/weight_registry.py`：模組層級 `dict`（強引用），key＝
  `(resolved source path, quantization, precision, device, backend)`；value 持有 engine、單一 `LLMPatcher`、`disk_loads`、`ram_bytes`。
- [ ] `runtime.py`：`LLMRuntime` 變成輕量 handle（cfg 含 kv、context），權重與 patcher 一律向 registry 取得；
  `get_handle` 的 `WeakValueDictionary` 可保留（只是 handle），但 handle 被回收不能影響 registry。
- [ ] kv、context 改成每請求參數：`hf_generate.py`、`prefix_context.py`、`prefix_cache.py`、`kv_cache.create` 的呼叫改讀 handle 的 cfg。
  前綴快照本來就以全精度存放，restore 時依請求的 kv 模式轉換（現行邏輯可沿用）。
- [ ] `LLMRuntime._comfy_cache_tensors` 回傳 `[]`：registry 持有的東西不會因 ComfyUI 清快取而釋放，回報它們會讓 ComfyUI 誤判可釋放量。
- [ ] `LLMPatcher.model_size()` 只回報權重實際大小（拿掉 `working(...)`）。工作記憶體已經由 `runtime.chat` 以
  `memory_required` 傳給 `load_models_gpu`；原本重複計算，也會放大 ComfyUI 的 pin 預算（review §8-9）。
- [ ] B-C1：`nodes_load.py` 的 `kv_quantization`、`device`、`precision` 選單第一項改為 `"default"`；
  `context_tokens` 的 0 代表 default；`registry.options` 略過這些值；`gateway_graph.py` 不再自行塞預設值。
- [ ] 單元測試（fake engine）：只差 kv／context 的兩個 cfg 拿到同一個 registry 項目；刪除 handle 並 `gc.collect()` 後項目仍在；
  profile 設定不再被節點預設值覆蓋。
- [ ] commit（不需重啟 ComfyUI 驗證，GPU 驗證在 S1 一起做）。

## Step 4：明確釋放與 RAM 預算（review T-4.6、B-R3）

- [ ] `plugin/config/config.yaml` 新增 `llm_ram_budget_gb: 45`。
- [ ] registry 建立新項目前檢查：`Σ ram_bytes + 新模型大小 ≤ 預算`，且 `新模型大小 ≤ MemAvailable − inactive headroom − 4 GB`；
  不符就拋 `UserError`，訊息列出目前常駐模型與 `POST /llm/release`。
  Path A 的大小用 `estimate.weights(cfg)`（第一次卸載後改用實測 CPU 大小）；Path B 用 GGUF + mmproj 的檔案大小。
- [ ] `POST /llm/release`（body：`{"model": "<profile id>"}` 或 `{"model": "all"}`）：先 `detach`、從 registry 移除、
  `gc.collect()`、`soft_empty_cache()`；回報釋放的 RAM／VRAM。新增 `LLMRelease` 節點做同一件事。
- [ ] `/free free_memory:true` 不需要任何程式碼：ComfyUI 會卸載到 RAM（`detach`）並重建節點快取，registry 不受影響。
- [ ] 更新 `plugin/src/test/cache_clear_accept.py`：改為斷言 free_memory 後 `disk_loads` 不變；另加 release 後才重新讀取的案例。
- [ ] 更新 `plugin/doc/caching.md`（三語）：R1、R2、預算、release。
- [ ] 單元測試：預算超出時拒絕；release 後項目消失。
- [ ] commit。

## Step 5：GPU session S1（Path A，9B）

預算：Qwen3.5-9B NF4 快取大小 + SDXL base checkpoint 大小，× 1.05 + 3 GB。

- [ ] 啟動 ComfyUI（R3：只用 repo 自己的 launcher；**不要用 `--force`**，它會殺掉佔用連接埠的其他程序）：
  `bash plugin/start.sh --stop; nohup bash plugin/start.sh > fan-out/agent/comfy.log 2>&1 &`，
  每 5 秒 `curl -sk https://127.0.0.1:8188/llm/status`，600 秒內沒有回應就停止。連接埠被不明程序佔用就停止並回報。
- [ ] 新增並執行 `plugin/src/test/ram_rules_accept.py`（9B、全程包在 `Budget` 內）：
  1. 對話一次（kv none）。
  2. 對話（kv hqq_8、context 8192）→ `disk_loads` 不變。
  3. SDXL 與對話交替 5 輪 → `disk_loads` 不變。
  4. `/free unload_models:true` → 對話 → `disk_loads` 不變、`transfers` +1。
  5. `/free unload_models:true, free_memory:true` → 對話 → `disk_loads` 不變。
  6. RAM 壓力：另開子程序配置 ballast，使 MemAvailable 降到 12 GB（低於 16 GB inactive headroom、高於停止條件 8 GB；
     有 swap 時改成 14 GB，且 swap 用量增加超過 256 MB 就中止此項）。壓力期間**只送 LLM 請求**（每個節點執行完都會觸發
     ComfyUI 的 RAM 清理）→ LLM 的 `disk_loads` 不變、這段期間 `read_bytes` 增量 ≈ 0。釋放 ballast。
     ComfyUI 在壓力下清掉 SDXL 快取、之後重讀 SDXL，是 ComfyUI 原生行為（R3 不能改），另外記錄，不計入預算。
  7. `/llm/release` 9B → 確認 RAM 釋放（這是唯一允許之後重讀的情況，本 session 不再載入 9B）。
- [ ] 同一個 session 接著跑既有的 9B 驗收：`api_accept`、`stream_accept`、`fault_accept`、`concurrent_accept`、`ram_accept`
  （在步驟 7 之前跑，避免重讀）。
- [ ] 停止 ComfyUI：`bash plugin/start.sh --stop`。
- [ ] 結果寫入 `fan-out/agent/s1.json`；不通過就修正後重跑（重跑也要算進預算記錄）。
- [ ] commit。

## Step 6：正確性修正（review Phase 2）

- [ ] T-2.2：`protocol.validate` 讓 `max_tokens` 上限與 `LLMChat` 節點一致（統一成 262143）。
- [ ] T-2.3：`gateway_stream.py` 改成合併 delta 的無上限 buffer，不再使用 `maxsize=512` + `put_nowait`。
- [ ] T-2.4：Studio 送圖改用 data URL（`vision_messages.attach` 送 512 px JPEG 的 base64），不再要求 loopback `/view`。
- [ ] T-2.5：`catalog.settings` 預設 model 取 caps 第一個 profile；`catalog.image_settings` 改讀 `generation.yaml`；
  `capabilities.py`、`runtime_status.py` 依設定回報 backend、vision、kv。
- [ ] T-2.6：`gemma_tools` 捕捉 `IndexError`；`image_inputs.py` 非遮罩編輯改 resize 不加黑邊；
  `hf_generate.py` 的 seed 用 `torch.random.fork_rng` 包住；profile 新增 `tool_format` 取代 `"tools" in chat_template` 判斷。
- [ ] T-2.7：先用 `Qwen3.5-9B` 的 chat template 以 `enable_thinking=True` 渲染（只讀模板，不載入權重），generation prompt
  以 `<think>` 結尾才實作 forced-open 處理與 `reasoning_content`；否則在報告中記錄「不需要」。
- [ ] 每項附單元測試；全部完成後一次 commit（或每項一次）。

## Step 7：Path B — 執行時載入 GGUF（review T-5.0、T-5.6～T-5.9）

- [ ] 7.0 **決策 spike（先做，用 0.8B，I/O 很小）**：在 ComfyUI 停止時，用 plugin venv 跑新的
  `plugin/src/test/gguf_runtime_spike.py`。模型：lmstudio-community 的 `Qwen3.5-0.8B-Q4_K_M.gguf` 與
  `mmproj-Qwen3.5-0.8B-BF16.gguf`（共 ≈ 735 MB，下載到 `plugin/data/spike/`，之後重用不再下載），config／tokenizer 取自 `Qwen/Qwen3.5-0.8B`。
  先在 plugin venv 安裝 `kernels==0.17.2`（transformers 5.18 要求 `>=0.17.0,<0.18.0`）；B-T 被選中才寫入 `plugin/requirements.txt`。
  - B-T：先呼叫 `transformers.integrations.gguf.kernels.get_gguf_kernel()`；回傳 `False` 就判定 B-T 不可用（不要直接
    `from_pretrained`，它會靜默整個解量化）。可用時再用 `GgufConfig(dequantize=False)`、`device_map={"": "cuda:0"}`、
    `attn_implementation="sdpa"` 載入，斷言：`GgufLinear` 模組數 > 0、uint8 參數 > 0、`torch.cuda.memory_allocated` ≈ 檔案大小
    + `out_proj` 解量化量；`hf_move.move(model, "cpu", 0)` 後 CUDA 歸零、再搬回 GPU 輸出相同（R1）。
  - B-L：同一個 GGUF 用 memfd + llama-cpp-python（`n_gpu_layers=-1`）載入；斷言 `read_bytes` 只在複製時增加、
    RssAnon 不多出一份權重、Shmem 增加約檔案大小、`close()` 後重載 `read_bytes` 不變。
  - 兩者都量：logits 對 llama.cpp 的 top1／KL（同 `importer/logit_parity.py` 的門檻）、decode tok/s、512 與 4096 token 的 prefill 秒數、VRAM 峰值。
  - 確認 hub kernel 下載後，設定 `HF_HUB_OFFLINE=1` 重開程序仍能取得 kernel（否則每次啟動都要連網）。
  - **決策規則**：B-T 可用、數值通過、decode tok/s ≥ B-L 的 50%、4096 token prefill ≤ B-L 的 3 倍 → 選 B-T；否則選 B-L。
    寫入 `fan-out/agent/path-b-decision.json`，之後的步驟只實作被選中的那一個。兩者都不可用就跳過 Step 7 剩餘部分與 Step 8，在報告中說明。
- [ ] 7.1 共同 Engine 介面：`load(device, budget)`、`offload()`、`prepare()`、`chat()`、`cache_tensors()`、`diagnostics`。
  `runtime.ensure_engine` 依 `backend` 選擇；移除 `runtime.py:20-21`、`request_options.py:14-15`、`estimate.py:13-14`、
  `token_count.py:16-17` 的 gguf 拒絕，改成依 backend 驗證。
- [ ] 7.2（選 B-T 時）`plugin/src/main/gguf_packed.py`：
  - 載入前檢查 kernel（同 7.0），並用 `GgufHeader.from_file` 依 `get_gguf_plan` 算出會被解量化的張量與大小，計入 RAM／VRAM 預算；
    不符就拒絕載入，不可讓 transformers 退回整個解量化。
  - 文字權重：`AutoModelForCausalLM.from_pretrained(<gguf 所在目錄>, gguf_file=..., quantization_config=GgufConfig(dequantize=False))`。
  - 視覺：profile 新增 `base`（HF config 與 processor 目錄，9B 用 `/mnt/DATA9/LLM_model/d/Qwen3.5-9B`，27B 用
    `/mnt/DATA9/LLM_model/d/Qwen3.8-27B-OBLITERATED`）。在 meta device 建 `AutoModelForImageTextToText`，把
    `model.language_model` 與 `lm_head` 換成 packed 的模組，vision 權重用 `importer/vision.py` 的 `convert(mmproj, torch.bfloat16)`
    以 `load_state_dict(strict=True, assign=True)` 只載入 `model.visual.*`。先比對 base config 的 text 部分與 GGUF 轉出的 config 一致才組裝。
  - 只讀一次磁碟：GGUF 與 mmproj 各讀一次；卸載用現有 `hf_move`（packed uint8 tensor 搬到 CPU RAM，R1）；registry 強引用（Step 3）。
  - packed 模型不能 `save_pretrained`（`is_serializable` 為 False），不要寫 NF4 快取。
  - `hf_precision.py`、`prefix_probe_linear.py` 只認 `Linear4bit`；packed 模型的 Qwen 視覺前綴先走完整預填（`prefix_context.supported` 回傳 False），文字前綴照常。
- [ ] 7.2'（選 B-L 時）`plugin/src/main/gguf_memfd.py` 與 `gguf_engine.py`：
  - 第一次載入把 GGUF 與 mmproj 讀進 `os.memfd_create`（64 MiB 分塊），讀完對來源 `posix_fadvise(DONTNEED)`；memfd 由 registry 持有，`disk_loads` +1。
  - 起點是 `git show ebf4ca4^:plugin/src/main/gguf_engine.py`（同 commit 的 `gguf_inputs.py`、`generation_controls.py`）。
    `model_path=f"/proc/self/fd/{fd}"`、`use_mmap=True`、`flash_attn=True`、`type_k/type_v` 對應 `none/q8_0/q4_0`；拿掉每次請求的 `reset()`。
  - 文字：GGUF 的 `tokenizer.chat_template` 經 Jinja 渲染後 `create_completion`；視覺：`MTMDChatHandler`（已確認會帶入 `tools`，但每次清 KV）。
  - 輸出 raw text 交給共同的 `model_response.parse`／`tool_calls.parse`；串流沿用 `llm.token` 與 `VisibleText`；`stopping_criteria` 呼叫 `throw_exception_if_processing_interrupted()`。
  - 前綴快照不要用 `save_state()`（會多複製 ≈ 0.5 GB logits），改用 `llama_state_seq_get_data`／`llama_state_seq_set_data`，大小計入 `ram_bytes`。
  - kv 或 context 改變時從 memfd 重建 `Llama`（不讀磁碟），記錄次數與秒數。
- [ ] 7.3 Patcher 對應：
  - B-T：與 Path A 相同（`hf_move` 卸載／恢復），`model_size` 只回報權重。
  - B-L：用 `GgufHeader.from_file`（讀 memfd 路徑，只讀 header）算每層大小與 `n_gpu_layers`；`detach` 呼叫 `close()`、memfd 保留；
    `loaded_size` 用載入前後 `torch.cuda.mem_get_info` 差值；`partially_unload` 一律回傳 0（只釋放 context 要用 llama-cpp-python 內部 API，不做）。
  - 兩者的 `_comfy_cache_tensors` 都回傳 `[]`（registry 持有）。
- [ ] 7.4 Profiles：新增 `Qwen3.5-9B-gguf-runtime`、`Qwen3.8-27B-gguf-runtime`（`backend: gguf`，`model`／`mmproj` 指向 `imports.yaml`，
  B-T 另加 `base`）。Studio `catalog.settings` 依 backend 驗證 kv（B-T：`none/hqq_8/hqq_4`；B-L：`none/q8_0/q4_0`）；刪除未使用的 `discovery.llm_settings`。
- [ ] 7.5 前綴：B-T 沿用現有文字前綴快照；B-L 量測第二輪 prefill token 數，必要時用 7.2' 的 seq state 快照保存 system 前綴。
  B-L 的視覺請求（`MTMDChatHandler` 每次清 KV）接受完整預填，在報告中記錄耗時。
- [ ] 7.6 單元測試：backend 選擇、profile 驗證、kernel 不可用時拒絕載入、預算計算；B-L 另測 memfd 讀寫（小暫存檔）；
  vision 對照表測試沿用 0.8B mmproj 的 header（只讀 header，不讀權重）。
- [ ] commit。

## Step 8：GPU session S2（Path B 與 A/B 對照）

預算：9B GGUF + 9B mmproj + 27B GGUF + 27B mmproj + Qwen3.8-27B NF4 快取 + SDXL base，× 1.05 + 3 GB。
RAM 順序（不超過 45 GB 預算）：9B runtime 先跑完並 release，再跑 27B 兩條路徑。

- [ ] 啟動 ComfyUI（同 Step 5 的方式）。
- [ ] `Qwen3.5-9B-gguf-runtime`：文字、工具、視覺、與 SDXL 交替 5 輪、`/free unload_models` 後重載 → `disk_loads == 1`、重載時 `read_bytes` 不增加；
  量測 tok/s、首 token、VRAM、常駐 RAM。完成後 `/llm/release`。
- [ ] 27B 載入前先依 config 算出 VRAM 需求（B-T 含 `out_proj` 解量化量）；超過 24 GB 減去 2 GB 工作空間就改 bfloat16（B-T）或部分 layer 放 CPU（B-L），仍不符就跳過並記錄。
- [ ] `Qwen3.8-27B-gguf-runtime` 與 `Qwen3.8-27B`（Path A）：同一組請求各跑一次並輸出差異（review T-5.10），
  與 SDXL 交替 10 輪不 OOM；兩者 `disk_loads` 各為 1（review T-5.1）。
- [ ] 停止 ComfyUI；結果寫入 `fan-out/agent/s2.json`。
- [ ] commit。

## Step 9：Path A 改善（review T-4.2、T-5.2～T-5.5）

- [ ] NF4 快取 key：加 `fingerprint.json`（來源每個檔的 size、mtime，`model.safetensors.index.json` 的 hash，transformers、bitsandbytes 版本）。
  **既有快取要就地補寫 fingerprint，不可讓它失效重建**（重建＝讀 54 GB + 寫 15 GB）。`location()` 改用 hash 命名避免碰撞，舊目錄名保留相容。
- [ ] 不做獨立預熱行程；快取寫入維持在第一次載入後。
- [ ] 匯入器：預設 bfloat16；`--nf4-only`（逐張量解量化後直接產生 NF4 快取，不留 BF16/FP16 中間檔）；
  `vision.py` 未知 leaf 給明確錯誤；比對 mmproj metadata 與 `--base`；複製 `generation_config.json`；
  開始前清空 `.partial`；純文字匯入；thread 數與 `max_memory` 依 `psutil` 計算（`cpu` 上限 = MemAvailable − 8 GB）。
- [ ] Parity 擴充（全詞表 tokenizer、NF4 KL、≥ 4k token 長上下文）只寫程式與單元測試；
  **不要對既有的 27B 匯入重跑**。若要實測，只在 ComfyUI 停止時對 9B 跑一次，並記錄 `read_bytes`。
- [ ] 載入時的關卡檢查只強制 `gate_version` 存在的新匯入（決定 6）。
- [ ] 單元測試用 gguf-py 產生的小型假 GGUF／mmproj。
- [ ] commit。

## Step 10：Plugin 效能（review T-4.3～T-4.5）

- [ ] T-4.3：每對話保留一份「上一輪完整 prompt」前綴快照（Path A），LRU 上限以 bytes 計，計入 registry `ram_bytes` 與預算。
- [ ] T-4.4：sliding 層 HQQ 改成 residual buffer，達門檻才量化新增部分；CPU 單元測試證明解量化誤差不隨步數成長。
- [ ] T-4.5：pinned memory 自己 `cudaHostRegister`（不交給 ComfyUI dynamic pin）；kernel 模式量測腳本。
  量測放在下一個 GPU session，不另外重啟。
- [ ] commit。

## Step 11：Studio I/O（review Phase 3，次要）

- [ ] T-3.1：delta 先進記憶體 buffer 直接推 SSE，每 250 ms 或 2 KB 合併寫 DB；`message.done` 強制 flush；`PRAGMA synchronous=NORMAL`。
- [ ] T-3.2：`check()` 只 `SELECT cancelled` 並以記憶體旗標為主；`Store.update` 加 `fetch=False`。
- [ ] T-3.3：trace 瘦身（request body 存 hash 與 token 數；`/llm/status` 只存該模型一列）；翻頁 SQL 不選 `trace_json`。
- [ ] T-3.4：影像處理全部 `asyncio.to_thread`；設定啟動時讀一次。
- [ ] T-3.5：run 結束後刪除該 run 的 `message.delta`、`image.progress` 事件。ComfyUI input/output 的副本保留。
- [ ] T-3.6：`/info` 改遞迴 CTE、budget 的圖片 token 快取、JPEG 快取原子寫入、`fail()` 清 previews、vision JPEG 不重複上傳。
- [ ] 單元測試用暫存 SQLite；量測：以 Step 1 的工具對 Studio PID 記錄一則回覆的 `write_bytes` 與 commit 次數，前後對照。
- [ ] commit。

## Step 12：清理（review B-E1～B-E6）

- [ ] `ipv4.enable` 只在 `family == 0` 時改成 IPv4；`settings.environment` 只設定 plugin 需要的變數。
- [ ] `requests` 加入 `plugin/requirements.txt`（或改用 httpx）。
- [ ] 刪除 `server/src/main/graph.py` 的 `graph()`（保留 `node()`）。
- [ ] `models.yaml`／`imports.yaml` 支援 `${LLM_MODEL_ROOT}`，預設值維持現有路徑。
- [ ] commit。

## Step 13：GPU session S3（最終回歸）

預算：Qwen3.5-9B NF4 快取 + 兩個 SDXL checkpoint，× 1.05 + 3 GB。

- [ ] 啟動 ComfyUI 與 Studio（`bash server/start.sh`）。
- [ ] 依序跑：`ram_rules_accept`、`api_accept`、`stream_accept`、Studio 的 `studio_generate`、`studio_edit`、`studio_recovery`、`studio_retry`、
  `studio_memory`（全部用 9B），以及 T-4.5 的量測。
- [ ] 最後才跑會重啟服務的 `lifecycle_accept`（它的重讀不計入本 session 預算，另外記錄）。
- [ ] 停止所有服務；結果寫入 `fan-out/agent/s3.json`。
- [ ] 更新 `text-coverage.txt`、`todo.txt`、相關 `plugin/doc/*.md`（三語），內容只寫實測結果。
- [ ] 最後 commit 並推送：`git push -u origin feat/ram-resident-llm`（網路錯誤時依 2、4、8、16 秒重試）。

## E. 完成定義

- 單元測試全綠。
- S1、S2、S3 的 `read_bytes` 都在預算內，所有權重 `disk_loads == 1`（release 後的情況除外）。
- `/free`（含 `free_memory`）、RAM 壓力、kv／context 變更、LLM／SDXL 交替都不造成重讀。
- 兩條路徑都能服務 Qwen3.8-27B，A/B 差異報告存在。
- `fan-out/agent/report.md` 列出每個 step 的結果、量測數字、未完成項目與原因。
