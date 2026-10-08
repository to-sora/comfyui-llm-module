# Images / 圖片 / 图片

Generated PNG bytes are copied once into `data/assets`, with SHA256 and WebP thumbnails.
Originals have immutable caching; PNG, JPG and selected-image ZIP downloads use local files.
Images remain available while ComfyUI is offline. Uploads accept HEIC and resize large photos
so neither dimension exceeds 4096. Every edit creates a new version linked to its source.

繁中：生成 PNG 複製一次，記錄 SHA256 及 WebP 縮圖。原圖使用不可變快取，
PNG、JPG 與多選 ZIP 下載均來自本機；ComfyUI 離線仍可查看。
支援 HEIC，大相片縮至每邊最多 4096 像素；每次編輯新增版本並連結來源。

简中：生成 PNG 复制一次，记录 SHA256 和 WebP 缩略图。原图使用不可变缓存，
PNG、JPG 和多选 ZIP 下载均来自本机；ComfyUI 离线仍可查看。
支持 HEIC，大照片缩至每边最多 4096 像素；每次编辑新增版本并链接来源。

Painted masks record their source. A mismatched source is rejected before GPU submission.
Odd sizes are padded for the VAE, then composited at the original dimensions; unmasked pixels stay exact.
Masked SDXL edits encode the source and attach a noise mask. This avoids a grey fill at low strength; the requested strength is retained.
The viewer offers versions, compare, zoom and pan. Library supports favorites and bulk actions.
Deleting a chat preserves its Library images. Deleting images removes local files while retaining lineage records.
The model's visual assessment can still be wrong; actual results remain visible for review.

繁中：遮罩記錄來源，不匹配時在送入 GPU 前拒絕。奇數尺寸先補齊再以原尺寸合成，
遮罩外像素完全保留。提供版本、比較、縮放與平移，圖片庫可收藏及批次處理。
SDXL 編輯編碼原圖並加雜訊遮罩，避免低強度留下灰塊；保留要求的強度。
刪除對話保留圖片庫內容；刪圖移除本機檔案但保留版本記錄。視覺模型的判斷仍需核對。

简中：遮罩记录来源，不匹配时在提交 GPU 前拒绝。奇数尺寸先补齐再以原尺寸合成，
遮罩外像素完全保留。提供版本、比较、缩放和平移，图片库可收藏和批量处理。
SDXL 编辑编码原图并加噪声遮罩，避免低强度留下灰块；保留要求的强度。
删除对话保留图片库内容；删图移除本地文件但保留版本记录。视觉模型的判断仍需核对。
