# RAM ownership / RAM 管理 / RAM 管理

The ComfyUI process owns each LLM weight representation strongly. Context, KV and sampling changes use the same owner and patcher. GPU placement and offload run through ComfyUI's model manager; offloaded weights remain in CPU RAM. A process-lifetime source ledger refuses a second weight read, including conversion attempts. Failed reads are not silently retried.

ComfyUI 程序持有權重；上下文、KV、取樣共用同一管理物件。GPU 載入與卸載由 ComfyUI 決定，卸載後留在 RAM。來源帳本拒絕同次執行重讀，包含轉換與失敗重試。

ComfyUI 进程持有权重；上下文、KV、采样共用同一管理对象。GPU 加载与卸载由 ComfyUI 决定，卸载后保留在 RAM。来源账本拒绝同次运行重复读取，包括转换和失败重试。

Admission uses an 80 GB planning ceiling, a 35 GB LLM reservation, 14 GB for SDXL, and a 1 GB auxiliary-model cap. Normal free headroom is 20 GiB; the hard floor is 8 GiB. Admission includes loading/conversion staging and GPU weights that may return to RAM. External memory pressure can refuse work; existing weights are retained. `/llm/status` reports reservations and source reads.

規劃上限 80 GB，LLM 35 GB、SDXL 14 GB、輔助模型 1 GB；正常保留 20 GiB，最低 8 GiB。先計入載入、轉換暫存及 GPU 回存需求，不足就拒絕新增工作，保留既有模型。

规划上限 80 GB，LLM 35 GB、SDXL 14 GB、辅助模型 1 GB；正常保留 20 GiB，最低 8 GiB。预先计入加载、转换暂存及 GPU 回存需求，不足就拒绝新增工作，保留已有模型。

Studio uses `LLMManagedCheckpoint` to retain SDXL outputs. Use this loader in custom workflows too. The launcher reuses the existing civit installation and flags, skips its upstream link-writing stage, and disables disk-backed dynamic loading, mmap and pinned copies. No upstream files or ComfyUI functions are patched. Offline GGUF conversion refuses to run during an active managed ComfyUI process; existing imported profiles remain usable.

Studio 使用常駐 checkpoint 節點；自訂流程亦應使用此節點。啟動器沿用 civit 設定、略過上游連結寫入，禁止磁碟卸載及 mmap，不修改上游或內部函式。執行中的 ComfyUI 禁止離線轉換。

Studio 使用常驻 checkpoint 节点；自定义流程也应使用此节点。启动器沿用 civit 设置、跳过上游链接写入，禁止磁盘卸载和 mmap，不修改上游或内部函数。运行中的 ComfyUI 禁止离线转换。
