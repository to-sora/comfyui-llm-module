# Qwen ComfyUI

Development extension. Root exports custom nodes; application code is in `plugin`.
開發中擴充套件。根目錄匯出節點，應用程式位於 `plugin`。
开发中扩展。根目录导出节点，应用程序位于 `plugin`。

## Setup / 建置 / 构建

```bash
bash install-local-build.sh
bash plugin/install-app-dep.sh
bash plugin/start.sh
```

Administrator build prerequisites: `install-build-tool-ubuntu-headless.sh`.
管理員建置前置作業：上述腳本透過 sudo apt 安裝系統套件。
管理员构建前置作业：上述脚本通过 sudo apt 安装系统包。

Python uses the existing environment; Useful_shell_script supports `py13`.
Python 沿用既有環境；Useful_shell_script 提供 `py13`。
Python 沿用现有环境；Useful_shell_script 提供 `py13`。

HTTPS: `https://127.0.0.1:8188`. Self-signed keys: `plugin/data/tls`.
自簽憑證需手動信任。預設 public IPv4、停用白名單。
自签证书需手动信任。默认 public IPv4、停用白名单。
`plugin/start.sh --stop` stops the process tree; `--force` replaces port owners.
`--stop` 停止程序樹；`--force` 終止連接埠佔用程序。
`--stop` 停止进程树；`--force` 终止端口占用进程。

## Nodes / 節點 / 节点

`QwenModel → QwenGenerate/QwenBatch → QwenUnload`

Batch input is a JSON string array. Concurrent mode uses isolated model replicas.
批次輸入為 JSON 字串陣列。併發模式使用獨立模型副本，增加 VRAM 用量。
批次输入为 JSON 字符串数组。并发模式使用独立模型副本，增加 VRAM 用量。

## Acceptance / 驗收 / 验收

Upload `plugin/colab/qwen-colab.ipynb` to Colab; select GPU and run its cells.
上載 notebook 至 Colab，選擇 GPU 並執行儲存格。
上传 notebook 至 Colab，选择 GPU 并执行单元格。
Results: `fan-out/colab-result.json`; logs: `plugin/data/comfy.log`.
結果與紀錄位於上述路徑。GPU 實測狀態見 `todo.txt`。
结果与记录位于上述路径。GPU 实测状态见 `todo.txt`。

Model weights and dependencies exceed 1GB. `plugin/data` supports symlinks.
模型權重及依賴超過 1GB；`plugin/data` 支援符號連結。
模型权重及依赖超过 1GB；`plugin/data` 支持符号链接。

Details / 詳情 / 详情: [runtime](plugin/doc/runtime.md), [formats](plugin/doc/formats.md).
