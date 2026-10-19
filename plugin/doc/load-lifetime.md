# Load lifetime / 載入生命週期 / 加载生命周期

New model loads own a reservation token. If loading fails, the extension drops partial model references and tracking callbacks, clears tensor references from unwound traceback frames, reclaims unused allocations and releases that token. The failed source-read receipt remains; retrying cannot reread it. Releasing accounting does not itself prove how many physical bytes were reclaimed. Existing models and their reservations survive a failed GPU restore. SDXL and background-model loads use the same transaction.

新模型持有獨立預留憑證。載入失敗會清理部分模型、追蹤回呼及已退出堆疊中的張量引用，回收未用配置，再撤銷該憑證。失敗讀取紀錄保留，重試不得重讀；撤銷額度本身不代表實體 RAM 釋放量。既有模型恢復失敗時，權重與額度保留。SDXL 及去背模型共用此交易。

新模型持有独立预留凭证。加载失败会清理部分模型、跟踪回调及已退出堆栈中的张量引用，回收未用配置，再撤销该凭证。失败读取记录保留，重试不得重读；撤销额度本身不代表物理 RAM 释放量。已有模型恢复失败时，权重与额度保留。SDXL 及去背模型共用此事务。

`auto` resolves through ComfyUI before forming a runtime key. When it resolves to `cuda:0`, both names select the same owner. Generated NF4 caches retain their original source identity, including cache-marker chains. The ledger checks both physical sources and logical weight representations, so writing a new cache cannot permit a second read of the same representation. Context, KV and sampling remain request-local.

建立管理物件前先由 ComfyUI 解析 `auto`；若為 `cuda:0`，兩者共用物件。NF4 快取沿用原始權重身分，包括連鎖來源標記。帳本同時檢查實體來源與邏輯權重，新增快取不能放行第二次讀取。上下文、KV 與取樣仍屬各請求設定。

创建管理对象前先由 ComfyUI 解析 `auto`；若为 `cuda:0`，两者共用对象。NF4 缓存沿用原始权重身份，包括连续来源标记。账本同时检查物理来源与逻辑权重，新增缓存不能放行第二次读取。上下文、KV 与采样仍属各请求设置。
