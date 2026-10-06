# Tools / 工具 / 工具

EN: Buttons and assistant calls use `POST /api/session/{sid}/tool` with
`name`, `arguments` and an optional retry-stable `request_id`.
`GET /api/tools` returns detected enums and schemas. `image_gen_sdxl_text`,
`image_gen_sdxl_image`, `image_gen_sdxl_inpaint` and `image_edit_*` enqueue jobs.
`sent_all_pending` (alias `pending_sent`) snapshots and executes the pending batch.
Earlier job IDs can be image inputs. `check_current_pending`, `job_status`,
`cancel_job`, `view_images` and `list_models` inspect or manage work.
After listing models, `image_settings` selects detected model/sampling enums.

繁中：按鈕與助理共用 `POST /api/session/{sid}/tool`，欄位為 `name`、
`arguments` 及可選的重試固定 `request_id`。`GET /api/tools` 回傳自動偵測
選項與格式。`image_gen_sdxl_*`、`image_edit_*` 先加入待處理；
`sent_all_pending`（別名 `pending_sent`）一次送出清單。可用較早工作 ID
作為圖片來源。查詢工具包括 `check_current_pending`、`job_status`、
`cancel_job`、`view_images`、`list_models`；列出模型後可用 `image_settings` 選擇模型。

简中：按钮与助手共用 `POST /api/session/{sid}/tool`，字段为 `name`、
`arguments` 及可选的重试固定 `request_id`。`GET /api/tools` 返回自动检测
选项与格式。`image_gen_sdxl_*`、`image_edit_*` 先加入待处理；
`sent_all_pending`（别名 `pending_sent`）一次提交列表。可用较早工作 ID
作为图片来源。查询工具包括 `check_current_pending`、`job_status`、
`cancel_job`、`view_images`、`list_models`；列出模型后可用 `image_settings` 选择模型。

EN: Tool results include a short `id`, status and relevant references.
Native IDs are 0–10000; read-only shared aliases are 10001–20000.
IDs never recycle. Create another session when a range is exhausted.
Expanded edit schemas expose 20 operations; chat uses a compact dispatcher.
All outputs are PNG, at most 4096 pixels on either axis. No ControlNet.

繁中：結果含整數 `id`、狀態及相關參照。本地 ID 為 0–10000；共享唯讀
別名為 10001–20000，不循環再用，耗盡時另開階段。完整格式列出 20 種編輯；
聊天用精簡分派工具。輸出 PNG，每邊最多 4096 像素，不含 ControlNet。

简中：结果含整数 `id`、状态及相关引用。本地 ID 为 0–10000；共享只读
别名为 10001–20000，不循环使用，耗尽时新建阶段。完整格式列出 20 种编辑；
聊天用精简分派工具。输出 PNG，每边最多 4096 像素，不含 ControlNet。
