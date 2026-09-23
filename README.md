# ComfyUI Qwen

English · 繁體中文 · 简体中文

ComfyUI nodes for Qwen text and vision inference, tensor/GGUF loading,
RAM prefix caches, single/concurrent execution, and native model unloading.

ComfyUI 節點提供 Qwen 文字與視覺推理、tensor／GGUF 載入、RAM 前綴快取、
單發／併發執行，以及原生模型卸載。

ComfyUI 节点提供 Qwen 文字与视觉推理、tensor／GGUF 加载、RAM 前缀缓存、
单发／并发执行，以及原生模型卸载。

```bash
bash install-local-build.sh
bash plugin/install-app-dep.sh
bash plugin/start.sh
# stop / 停止
bash plugin/start.sh --stop
```

Port: `https://127.0.0.1:8188`; bind: `0.0.0.0`; self-signed certificate:
`plugin/data/tls/cert.pem`. Browser certificate trust requires human action.

連接埠使用 IPv4 HTTPS；瀏覽器須手動信任自簽憑證。
连接端口使用 IPv4 HTTPS；浏览器须手动信任自签证书。

Python follows [Useful_shell_script](https://github.com/to-sora/Useful_shell_script).
`QWEN_PYTHON=python3-11` selects that installation. Colab uses its Python and
CUDA PyTorch through an application venv. System build dependencies belong
to the administrator-run `install-build-tool-ubuntu-headless.sh`.

Python 沿用現有環境；系統建置套件由管理員執行安裝腳本。
Python 沿用现有环境；系统构建套件由管理员执行安装脚本。

`QwenLoader → QwenGenerate` accepts an optional ComfyUI IMAGE batch.
`QwenBatch` accepts a JSON array of prompts. `mode=concurrent` loads one
model instance per worker. Model memory grows with worker count.

併發模式按 worker 數配置模型副本；GPU 用量隨副本數增加。
并发模式按 worker 数配置模型副本；GPU 用量随副本数增加。

Colab acceptance: [colab.ipynb](plugin/doc/colab.ipynb).
Runtime data stays under `plugin/data`, including symlinked data directories.
Weights and dependencies exceed the 1GB storage target.

Colab 驗收 notebook 包含安裝、模型下載、推理與 GPU 卸載。
模型與依賴所需容量超過 1GB；資料集中於 `plugin/data`，支援符號連結。

Colab 验收 notebook 包含安装、模型下载、推理与 GPU 卸载。
模型与依赖所需容量超过 1GB；数据集中于 `plugin/data`，支持符号链接。

[Formats / 格式](plugin/doc/formats.md) ·
[Configuration / 設定 / 设置](plugin/doc/configuration.md) ·
[Pending / 待完成](todo.txt)
