# ComfyUI LLM

Language and vision models use transformers through ComfyUI's queue and native memory manager. GGUF is an offline import format.
語言及視覺模型透過 transformers、ComfyUI 原生佇列與記憶體管理執行；GGUF 先離線匯入。
语言和视觉模型通过 transformers、ComfyUI 原生队列与内存管理运行；GGUF 先离线导入。

Converted 9B/27B models passed six parity gates. The pretrained Gemma profile is replaced by a local instruction model. The chat UI rebuild remains in progress; see `todo.txt` and `text-coverage.txt`.
匯入模型通過六關，Gemma 改用本機指令模型；聊天介面重建仍在進行，詳見待辦及驗證紀錄。
导入模型通过六关，Gemma 改用本地指令模型；聊天界面重建仍在进行，详见待办和验证记录。

## Setup / 安裝 / 安装

Use this workspace's sibling `comfyui` and `civit_script` directories.
只使用工作區同層的上述目錄；不安裝其他擴充套件。
只使用工作区同层的上述目录；不安装其他扩展。

```bash
bash install-local-build.sh
bash plugin/install-app-dep.sh
bash plugin/start.sh
```

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

See [API](plugin/doc/api.md), [runtime](plugin/doc/runtime.md), [models](plugin/doc/formats.md), [Gemma](plugin/doc/gemma.md), [tests](plugin/doc/tests.md).
詳細設定、模型限制及驗證狀態見上述文件。
详细配置、模型限制和验证状态见上述文档。
Model downloads and dependency caches can exceed 1 GB; model weights may stay in external directories.
模型下載與依賴快取可超過 1 GB；既有權重可保留在外部目錄。
模型下载与依赖缓存可超过 1 GB；现有权重可保留在外部目录。

[Image Studio / 圖片工作台 / 图片工作台](server/doc/start.md): HTTPS :8189.
Manual editing and LLM tools.
支援手動編輯與 LLM 工具。
支持手动编辑与 LLM 工具。
