# Images / 圖片 / 图片

EN: Each edit creates an immutable image version with parents, operation,
parameters, actual SDXL settings and assistant provenance. Mark a final version
or branch again. The lineage view links ancestors and descendants.
Inpainting pads odd sizes for the VAE, then composites at original dimensions;
pixels outside the mask remain byte-identical. CPU background removal estimates
border color or uses a chosen color; tolerance and softness control transparency.
It is a simple color algorithm and can remove similar foreground colors.

繁中：每次編輯新增不可變圖片版本，記錄父圖、操作、參數、實際 SDXL 設定
及助理來源。可標為最終版或繼續分支，版本介面連結祖先與後續版本。
局部重繪先補齊 VAE 尺寸，再以原尺寸合成；遮罩外像素完全相同。
CPU 去背估算邊界色或使用指定色，以容差及柔化控制透明度；相近前景色亦可能被移除。

简中：每次编辑新增不可变图片版本，记录父图、操作、参数、实际 SDXL 设置
及助手来源。可标为最终版或继续分支，版本界面链接祖先与后续版本。
局部重绘先补齐 VAE 尺寸，再以原尺寸合成；遮罩外像素完全相同。
CPU 去背估计边界色或使用指定色，以容差及柔化控制透明度；相近前景色也可能被移除。

EN: Multi-select sharing exposes only chosen images to every session, with
read-only aliases. Revoke each image independently. Private parents, prompts,
chat and settings are not shared. Editing a shared source creates a local copy;
revocation cannot recall copies or downloads already made.
Delete removes local image files/thumbnails and revokes sharing, retaining lineage.
ComfyUI originals stay in its output folder. ZIP export includes selected PNGs
and their metadata. Storage totals are shown; retained images can exceed 1 GB.

繁中：可多選圖片分享給所有階段，使用唯讀別名；每張均可獨立撤回。
未分享的父圖、提示、聊天及設定不會公開。修改共享來源會產生本地副本；
撤回無法收回既有副本或下載。刪除清除本地圖片與縮圖、撤回分享並保留版本紀錄；
ComfyUI 原檔仍在其輸出目錄。ZIP 匯出含選定 PNG 與資料，介面顯示用量，保留圖片可超過 1 GB。

简中：可多选图片分享给所有阶段，使用只读别名；每张均可独立撤回。
未分享的父图、提示、聊天及设置不会公开。编辑共享来源会产生本地副本；
撤回无法收回已有副本或下载。删除清除本地图片与缩略图、撤回分享并保留版本记录；
ComfyUI 原文件仍在其输出目录。ZIP 导出含选定 PNG 与数据，界面显示用量，保留图片可超过 1 GB。
