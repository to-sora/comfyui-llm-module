# Five tools / 五個工具 / 五个工具

| Tool | Arguments / 參數 / 参数 |
|---|---|
| generate_images | images[{prompt,negative?,checkpoint?,style?,aspect?,size?}], defaults?, seed? |
| edit_image | image, instruction, area?, strength?, checkpoint?, operation?, options? |
| upscale_image | image, factor:2 |
| remove_background | image |
| look_at_images | images:[numbers] |

Styles come from `config/content-config/styles.yaml`, filtered against detected compatible SDXL checkpoints.
The model sees style/aspect enums and detected checkpoint names. Per-image values override batch defaults. Size 512/768/1024 sets the longest edge; default 1024. Default: about 1 MP, random seeds, 28 steps,
CFG 5.5, dpmpp_2m, karras. Edit strengths low/medium/high mean .35/.5/.7 and keep source aspect.
Image numbers belong to a chat; storage IDs are ULIDs. Attach a Library image before the assistant uses it.
There is no pending-send tool or fixed alias range. No ControlNet.

繁中：樣式設定依自動偵測的相容 SDXL 模型篩選，工具提供描述及比例選項。
預設約百萬像素、隨機種子、28 步、CFG 5.5；編輯強度為 .35/.5/.7 並保留比例。
圖片編號屬於各對話，儲存使用 ULID；圖片庫內容需明確附加至對話才供助理使用。
不使用舊待送清單或固定別名範圍，不含 ControlNet。

简中：样式配置按自动检测的兼容 SDXL 模型筛选，工具提供描述和比例选项。
默认约百万像素、随机种子、28 步、CFG 5.5；编辑强度为 .35/.5/.7 并保留比例。
图片编号属于各对话，存储使用 ULID；图片库内容需明确附加到对话才供助手使用。
不使用旧待发送列表或固定别名范围，不含 ControlNet。

Upscale uses Lanczos; background removal uses U2NetP under ComfyUI. Local edits support text, crop, color and canvas operations; all images remain at most 4096 pixels per side.

逐圖設定優先於整批預設，可選實際模型及尺寸。放大用 Lanczos，去背用 ComfyUI 管理的 U2NetP；支援文字、裁切、色彩及畫布編輯，上限每邊 4096。

逐图配置优先于整批默认，可选模型与尺寸。放大使用 Lanczos，去背使用 ComfyUI 管理的 U2NetP；支持文字、裁剪、色彩及画布编辑，每边最多 4096。
