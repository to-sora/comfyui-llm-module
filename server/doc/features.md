# Studio features / 工作台功能 / 工作台功能

Start with `bash server/start.sh`; Studio uses HTTPS port 8189 and the ComfyUI gateway on 8188. Chat creates and reviews SDXL pictures. The assistant tools remain generate, edit, upscale, remove background and inspect. Finished images retain their recipe and parent links. Every output is at most 4096 pixels per dimension.

以啟動腳本開啟 HTTPS 8189，ComfyUI 閘道為 8188。聊天可生圖、編輯、放大、模型去背及檢視；保留設定與來源關係，每邊最多 4096 像素。

用启动脚本开启 HTTPS 8189，ComfyUI 网关为 8188。聊天可生成、编辑、放大、模型去背和检查；保留设置及来源关系，每边最多 4096 像素。

Twenty local edits, including crop, text, color and transparency, work from the viewer or the assistant’s edit tool. Expand canvas creates a source and mask for the assistant. Masked edits crop around the painted region for SDXL and composite back onto the original. Unpainted pixels stay unchanged. Background removal uses local CPU U2NetP inside a ComfyUI node. Install its small model with `bash plugin/install-image-tools.sh` from the repository root. [Model source](https://github.com/danielgatis/rembg/blob/main/rembg/sessions/u2netp.py).

檢視器提供二十種本機編輯、文字及透明度；擴圖建立來源與遮罩。遮罩區裁切處理後合回原圖，未塗區不變。去背由 ComfyUI 節點執行本機 CPU 模型，使用專案安裝腳本下載。

查看器提供二十种本地编辑、文字和透明度；扩图创建来源和遮罩。遮罩区裁切处理后合回原图，未涂区域不变。去背由 ComfyUI 节点运行本地 CPU 模型，用项目安装脚本下载。

Chat options include pin, archive, Markdown/ZIP export and deletion. Messages support edit-and-branch, regenerate, version selection, feedback and Continue. Continue reuses completed images and processes unfinished work. Search covers chat text and image prompts. Drafts persist in this browser. Settings include custom instructions, model/context/quantization, language, theme, image blur and completion notifications. Shortcuts: Ctrl/Cmd+K search, Ctrl/Cmd+Shift+O new chat, Ctrl/Cmd+. stop.

支援釘選、封存、搜尋匯出、分支重產、版本、回饋、續作與草稿。設定含個人指示、模型、上下文、量化、語言、主題、圖片模糊及通知；鍵盤快捷鍵如上。

支持置顶、归档、搜索导出、分支重生成、版本、反馈、继续和草稿。设置包含个人指令、模型、上下文、量化、语言、主题、图片模糊和通知；键盘快捷键如上。
