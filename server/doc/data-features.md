# Data and installation / 資料與安裝 / 数据与安装

Upload images, PDF or UTF-8 text through the attachment button, paste or drop. Documents are limited to 10 MiB, 100 PDF pages and 120,000 extracted characters. Parsing runs in a subprocess with bounded memory and time. A long document may be represented by a labeled excerpt within the selected context capacity. Scanned PDFs require OCR before upload.

可附加圖片、PDF 或 UTF-8 文字。文件上限 10 MiB、100 頁、十二萬字元；解析子程序限制記憶體與時間。長文件按上下文提供標示的摘錄；掃描 PDF 須先 OCR。

可添加图片、PDF 或 UTF-8 文本。文档上限 10 MiB、100 页、十二万字符；解析子进程限制内存和时间。长文档按上下文提供标明的摘录；扫描 PDF 需要先 OCR。

Storage shows local usage and offers selection-based cleanup of old, nonfavorite images. Backup exports chats, recipes, images, documents and preferences in an unencrypted ZIP. Restore merges missing records and files, keeping existing data. Finish active replies first. Restore accepts at most 20 GiB and requires free staging space; metadata is limited to 64 MiB. Model weights, TLS keys and dependencies are excluded.

儲存頁顯示用量，可選擇刪除舊且未收藏的圖片。未加密 ZIP 備份含對話、圖片、文件與偏好；還原僅新增缺少項目，保留現有資料。須先完成工作；上限 20 GiB，模型與金鑰不包含在內。

存储页显示用量，可选择删除旧且未收藏的图片。未加密 ZIP 备份包含对话、图片、文档及偏好；恢复只添加缺少项目，保留现有数据。需要先完成任务；上限 20 GiB，不包含模型和密钥。

The mobile layout includes a PWA manifest and offline application shell. Installation and notifications depend on browser support and a trusted HTTPS certificate. API responses and private image bytes are not placed in the service-worker cache. Image blur hides all pictures until explicitly revealed; it is a conservative display setting, not a content classifier. The default per-IP write limit is 60 requests/minute (`requests_per_minute` in server config).

手機版提供 PWA 與離線外殼；安裝、通知依瀏覽器及 HTTPS 信任而定。服務工作者不快取 API 與私人圖片。模糊模式需主動顯示全部圖片；並非內容分類器。預設每 IP 每分鐘六十次寫入。

手机版提供 PWA 和离线外壳；安装、通知取决于浏览器及 HTTPS 信任。服务工作者不缓存 API 和私人图片。模糊模式需要主动显示全部图片，并非内容分类器。默认每 IP 每分钟六十次写入。
