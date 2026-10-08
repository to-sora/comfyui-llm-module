# Local Qwen kernels / 本機核心 / 本地内核

Optional CUDA dependencies: `flash-linear-attention==0.5.2`, `fla-core==0.5.2`, `causal-conv1d==1.7.0`. Run `bash plugin/install-kernels.sh` at the repository root. The plugin venv and `plugin/.local-dep/wheels` contain all installed files.
可選 CUDA 依賴如上；根目錄執行安裝指令，檔案只留外掛私有環境及 wheel 目錄。
可选 CUDA 依赖如上；根目录执行安装命令，文件只留插件私有环境及 wheel 目录。

The build uses existing CUDA/nvcc and has a twenty-minute limit. No system packages or other ComfyUI nodes are installed. `installBuildTool.sh` is for separate administrator review and execution; agents must not run it.
使用既有 CUDA 編譯器，上限二十分鐘；不改系統或加其他節點。管理員腳本另行審閱執行，代理不可執行。
使用已有 CUDA 编译器，上限二十分钟；不改系统或添加其他节点。管理员脚本另行审阅执行，代理不可执行。

Restart through `plugin/start.sh`. Installation alone keeps reference kernels as the default. The full local-kernel trial regressed imported 9B NF4 yellow-image/tool requests; it is not generally enabled.
經啟動腳本重啟；僅安裝仍預設參考核心。全部本機核心令匯入九十億 NF4 黃圖誤叫工具，未全面啟用。
经启动脚本重启；仅安装仍默认参考内核。全部本地内核令导入九十亿 NF4 黄图误调工具，未全面启用。

For research, `diagnostic_kernels` accepts `reference`, `local`, `conv` (local convolution only) or `delta` (local delta rule only). Selection is scoped to ComfyUI's serialized inference and restored afterwards. Prefix snapshots include the kernel policy in their keys.
研究選項可選參考、全部本機、僅卷積或僅遞迴；只在原生序列推論期間套用，結束還原。前綴快照按核心策略分開。
研究选项可选参考、全部本地、仅卷积或仅递归；只在原生串行推理期间应用，结束恢复。前缀快照按内核策略分开。

`/llm/status` reports actual last-request `diagnostics.hybrid_kernels` bindings and `kernel_mode`. `working_memory` compares peak additional CUDA allocation with the requested ComfyUI workspace, after residency is arranged; it excludes initial disk loading. These are observations, not general performance guarantees.
狀態 API 記錄上一請求的實際核心及模式；記憶體比較額外峰值與原生工作空間，從模型駐留後起算，不含首次磁碟載入。觀察不代表全面效能保證。
状态 API 记录上一请求的实际内核及模式；内存比较额外峰值与原生工作空间，从模型驻留后起算，不含首次磁盘加载。观察不代表全面性能保证。

Sources / 來源 / 来源: [FLA](https://github.com/fla-org/flash-linear-attention), [causal-conv1d](https://github.com/Dao-AILab/causal-conv1d).
