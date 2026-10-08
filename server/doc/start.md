# Image Studio / 圖片工作台 / 图片工作台

EN: Install the ComfyUI extension and its gateway first. Start it through
`bash plugin/start.sh` (which uses civit_script). Run
`bash server/install-app-dep.sh`, then `bash server/start.sh`.
Open https://127.0.0.1:8189 and accept the self-signed certificate.
Configure the remote HTTPS gateway in `server/config/config.yaml`.
No GPU libraries or models are loaded by this independent application.

繁中：先安裝擴充與 gateway，以 `bash plugin/start.sh` 透過 civit_script
啟動 ComfyUI。執行 `bash server/install-app-dep.sh`，再執行
`bash server/start.sh`。瀏覽 https://127.0.0.1:8189 並接受自簽憑證。
遠端 gateway 位址設定於 `server/config/config.yaml`。此獨立應用不載入 GPU 模型。

简中：先安装扩展与 gateway，以 `bash plugin/start.sh` 通过 civit_script
启动 ComfyUI。执行 `bash server/install-app-dep.sh`，再执行
`bash server/start.sh`。浏览 https://127.0.0.1:8189 并接受自签证书。
远程 gateway 地址设置于 `server/config/config.yaml`。此独立应用不加载 GPU 模型。

EN: `server/start.sh --stop` stops its process tree. Port conflicts show
PID and process name; `--force` replaces the listener. Default: IPv4
0.0.0.0:8189, no authentication or whitelist. TLS files, SQLite, images,
thumbnails and logs stay in `server/data`, which may be a symlink.
Each chat has its own URL. Multiple tabs share one GPU queue.

繁中：`--stop` 停止應用的程序樹；連接埠衝突顯示 PID 與程序名，
`--force` 可取代佔用者。預設 IPv4 0.0.0.0:8189，無登入或白名單。
憑證、資料庫、圖片、縮圖及日誌置於可設符號連結的 `server/data`。
各對話具有獨立網址，多個分頁共用一個 GPU 佇列。

简中：`--stop` 停止应用的进程树；端口冲突显示 PID 与进程名，
`--force` 可替换占用者。默认 IPv4 0.0.0.0:8189，无登录或白名单。
证书、数据库、图片、缩略图及日志位于可设符号链接的 `server/data`。
各对话具有独立网址，多个标签页共用一个 GPU 队列。
