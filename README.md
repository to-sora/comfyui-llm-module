# ComfyUI LLM

HF/GGUF language and vision models run through ComfyUI's queue and memory manager.
HF/GGUF 語言及視覺模型透過 ComfyUI 佇列與記憶體管理執行。
HF/GGUF 语言及视觉模型通过 ComfyUI 队列与内存管理执行。

## Setup / 安裝 / 安装

Use this workspace's sibling `comfyui` and `civit_script` directories.
只使用工作區同層的上述目錄；不安裝其他擴充套件。
只使用工作区同层的上述目录；不安装其他扩展。

```bash
bash install-local-build.sh
bash plugin/install-app-dep.sh
bash plugin/install-gguf.sh
bash plugin/start.sh
```

Existing Python: `COMFY_BOOTSTRAP_PYTHON` may select its executable.
使用既有 Python，可透過上述環境變數指定執行檔。
使用现有 Python，可通过上述环境变量指定执行文件。

HTTPS: https://127.0.0.1:8188; trust the project's self-signed certificate manually.
HTTPS 自簽憑證位於 `plugin/data/tls`，瀏覽器需手動信任。
HTTPS 自签证书位于上述目录，浏览器需手动信任。
Public IPv4; no authentication or whitelist by default.
預設公開 IPv4，不設登入或白名單。
默认公开 IPv4，不设登录或白名单。

`plugin/start.sh --stop` stops this service; `--force` replaces port owners.
上述參數停止本服務或取代佔用連接埠的程序。
上述参数停止本服务或替换占用端口的进程。

## Usage / 使用 / 使用

Nodes: `LLMModel → LLMChat`; optional `LoadImage → images`.
節點可接收圖片及工具定義，輸出文字與回應 JSON。
节点可接收图片及工具定义，输出文本和响应 JSON。

```bash
curl -k https://127.0.0.1:8188/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen3.5-9B","messages":[{"role":"user","content":"What is 17+25?"}]}'
```

See [runtime](plugin/doc/runtime.md), [models](plugin/doc/formats.md), [tests](plugin/doc/tests.md).
詳細設定、模型限制及驗證狀態見上述文件。
详细配置、模型限制和验证状态见上述文档。
Model downloads and dependency caches can exceed 1 GB; model weights may stay in external directories.
模型下載與依賴快取可超過 1 GB；既有權重可保留在外部目錄。
模型下载与依赖缓存可超过 1 GB；现有权重可保留在外部目录。
