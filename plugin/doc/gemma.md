# Gemma instructions / Gemma 指令 / Gemma 指令

The product uses `/mnt/DATA9/LLM_model/d/gemma-3-12b-it` with its native instruction and image template. It replaces the supplied pretrained E2B profile.
產品使用上述既有本機指令模型及原生圖片範本，取代預訓練 E2B。
产品使用上述已有本地指令模型和原生图片模板，取代预训练 E2B。

For instruction models whose template has no tool syntax, the adapter adds the actual tool schemas and a JSON calling format to the system instruction. Tool results become user turns, preserving Gemma's alternating roles.
範本沒有工具語法時，轉接器加入實際工具結構及 JSON 格式；工具結果轉為使用者回合，保持角色交替。
模板没有工具语法时，适配器加入实际工具结构和 JSON 格式；工具结果转为用户回合，保持角色交替。

A malformed call returns its parse error. The harness permits one repair round. There are no hard-coded object, color or background review questions.
格式錯誤會回傳原因，由 harness 修復一次；圖片評估沒有固定物件、顏色或背景問題。
格式错误会返回原因，由 harness 修复一次；图片评估没有固定物体、颜色或背景问题。

NF4 plus HQQ 8-bit KV passed real text, image, tool-result and SDXL workflows. A naturally malformed call also passed the single repair path. Evidence: `fan-out/studio-engine/gemma-instruction-workflow.json`.
真實 NF4／8 位元 KV 文字、圖片、工具結果及 SDXL 流程通過，亦驗證一次自然格式錯誤的修復。
真实 NF4／8 位元 KV 文字、图片、工具结果和 SDXL 流程通过，也验证一次自然格式错误的修复。
