# Configuration · 設定 · 设置

`plugin/config/config.yaml`: startup device, dtype, workers, context size,
RAM cache budget, remote-code policy, and preloaded models.
`prefix_cache_mb` is shared across workers. `startup_models` contains loader
arguments, for example `[{model: Qwen/Qwen3.5-0.8B, mode: single}]`.

啟動設定涵蓋裝置、dtype、workers、context、RAM 快取容量及預載模型。
快取容量由 workers 共用；預載模型在 ComfyUI 啟動階段計算前綴 KV。

启动设置涵盖设备、dtype、workers、context、RAM 缓存容量及预载模型。
缓存容量由 workers 共用；预载模型在 ComfyUI 启动阶段计算前缀 KV。

`plugin/config/content-config/prefixes.yaml`: named system prefixes.
The node's prefix field accepts a configured name or literal system text.
Only configured prefixes receive startup warming. Tensor caches hold detached
CPU copies, including recurrent states. Each request receives a private copy.
Vision requests use full prefill; image-prefix KV reuse remains pending.

前綴欄位接受名稱或文字；已設定前綴在啟動時預熱，KV 與循環狀態儲存於 RAM。
各請求取得獨立副本。視覺輸入採完整 prefill；影像前綴重用列為待完成。

前缀字段接受名称或文字；已设置前缀在启动时预热，KV 与循环状态存储于 RAM。
各请求取得独立副本。视觉输入采用完整 prefill；图像前缀复用列为待完成。

`plugin/config/port-config.yaml`: local binds 127.0.0.1; standard binds IPv4
addresses on wg*/tails* interfaces; public binds 0.0.0.0. Development uses
public with `enable_whitelist: false`. Every listener uses a self-signed
certificate. `--force` terminates the port owner; `--stop` stops the service group.

開發預設 public、關閉白名單；服務使用 IPv4 自簽 HTTPS。
`--force` 終止佔用連接埠的程序；`--stop` 終止服務程序群組。

开发默认 public、关闭白名单；服务使用 IPv4 自签 HTTPS。
`--force` 终止占用端口的进程；`--stop` 终止服务进程组。

ComfyUI native `/free` unloads weights through the model-management protocol.
Dense tensors move to CPU; quantized/GGUF backends release their model objects.
The next request reloads weights. RAM prefixes survive dense tensor offload.

原生卸載將 dense 權重移至 CPU，釋放量化／GGUF 物件；下一請求重載。
原生卸载将 dense 权重移至 CPU，释放量化／GGUF 对象；下一请求重载。
