# CPU buffer cleanup / CPU 暫存清理 / CPU 暂存清理

Before refusing RAM admission, the extension collects unreachable Python objects and asks the process allocator to return unused pages with `malloc_trim`, when available. It then checks the same RAM limits again. Live model weights, prefix state and SDXL checkpoint owners remain retained. ComfyUI still decides GPU placement; cleanup does not unload models or read weight files. `/llm/status` reports cleanup attempts and reclaimed process RSS.

拒絕 RAM 准入前，擴充會清理無引用物件，並於可用時以 `malloc_trim` 歸還未使用頁面，再以原有限制檢查。模型權重、前綴狀態與 SDXL 管理物件保留；GPU 配置仍由 ComfyUI 決定。此清理不卸載模型或讀取權重；狀態 API 記錄次數及歸還的程序 RAM。

拒绝 RAM 准入前，扩展会清理无引用对象，并在可用时用 `malloc_trim` 归还未使用页面，再按原有限制检查。模型权重、前缀状态与 SDXL 管理对象保留；GPU 配置仍由 ComfyUI 决定。此清理不卸载模型或读取权重；状态 API 记录次数及归还的进程 RAM。

For a saved NF4 cache placed entirely on CUDA, first-load CPU scratch and the later CPU offload copy occur in separate serialized phases. Admission reserves the larger phase plus the unchanged headroom. CPU/partial placement and fresh quantization still add loading scratch to retained weights. The full eventual weight size counts against the resident-model cap.

既有 NF4 全部載入 CUDA 時，初次載入暫存與稍後回存 RAM 分屬串行階段，預留較大者及原有餘量。CPU、部分載入或首次量化仍將兩者相加；模型總大小仍計入常駐上限。

已有 NF4 全部加载 CUDA 时，初次加载暂存与稍后回存 RAM 属于串行阶段，预留较大者及原有余量。CPU、部分加载或首次量化仍将两者相加；模型总大小仍计入常驻上限。
