# Runtime / 執行 / 运行

Startup settings: `plugin/config/config.yaml`.
啟動設定：上述檔案。`workers` 控制併發副本數；`cache_mib` 為全部副本的 RAM 快取上限。
启动设置：上述文件。`workers` 控制并发副本数；`cache_mib` 为全部副本的 RAM 缓存上限。

Content prefixes: `plugin/config/content-config/prefixes.yaml`.
內容 prefix 儲存在上述檔案；節點接受名稱或自訂系統提示。
内容 prefix 存储在上述文件；节点接受名称或自定义系统提示。

```yaml
startup_models:
  - model: Qwen/Qwen3.5-0.8B
    mode: single
```

This startup list loads weights and prefills configured prefixes into RAM.
此啟動清單會載入權重並預填 prefix 至 RAM。空清單改於模型節點載入時預填。
此启动列表会加载权重并预填 prefix 至 RAM。空列表改于模型节点加载时预填。

Text requests reuse exact token prefixes. Each request receives a cache copy.
文字請求重用相同 token prefix，請求各自取得快取副本；混合注意力狀態隨副本保存。
文本请求复用相同 token prefix，请求各自取得缓存副本；混合注意力状态随副本保存。

Image requests use full prefill; image-dependent positions require separate state.
圖片請求使用完整預填，以隔離圖片相關的位置與狀態。
图片请求使用完整预填，以隔离图片相关的位置与状态。

Native ComfyUI unload, `/free`, and QwenUnload release engines and caches.
ComfyUI 原生卸載、`/free` 與 QwenUnload 釋放引擎及快取；後續推理重載磁碟權重。
ComfyUI 原生卸载、`/free` 与 QwenUnload 释放引擎及缓存；后续推理重载磁盘权重。
Offload means complete eviction. Layerwise CPU offload remains in `todo.txt`.
此 offload 為完整釋放；逐層 CPU offload 列於待辦。
此 offload 为完整释放；逐层 CPU offload 列于待办。

Public policy binds 0.0.0.0; local binds 127.0.0.1; standard binds wg*/tails* IPv4.
連接埠與可選白名單位於 `port-config.yaml`，開發預設 public。
端口与可选白名单位于 `port-config.yaml`，开发默认 public。
