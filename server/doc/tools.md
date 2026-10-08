# Five tools / 五個工具 / 五个工具

| Tool | Arguments / 參數 / 参数 |
|---|---|
| generate_images | images[{prompt,negative?}], style, aspect, seed? |
| edit_image | image, instruction, area?, strength? |
| upscale_image | image, factor:2 |
| remove_background | image |
| look_at_images | images:[numbers] |

Styles come from `config/content-config/styles.yaml`, filtered against detected compatible SDXL checkpoints.
The model sees style descriptions and aspect enums. Default: about 1 MP, random seeds, 28 steps,
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

Upscale currently uses Lanczos. Background removal currently estimates a uniform border color.
Model-based background removal belongs to the remaining polish phase.
目前放大使用 Lanczos，去背估算均勻邊界色；模型去背尚待後續階段。
目前放大使用 Lanczos，去背估计均匀边缘色；模型去背仍待后续阶段。
