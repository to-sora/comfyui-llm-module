# Verification / 驗證 / 验证

Run against the project's active HTTPS service:
針對專案正在執行的 HTTPS 服務測試：
针对项目正在运行的 HTTPS 服务测试：

```bash
plugin/.local-tool-app/venv/bin/python -m plugin.src.test.sdxl_smoke
plugin/.local-tool-app/venv/bin/python -m plugin.src.test.swap_accept
```

Tests use actual SDXL and Qwen weights on CUDA, without mocked generation.
測試使用真實 SDXL 與 Qwen 權重於 CUDA 執行，不模擬模型輸出。
测试使用真实 SDXL 和 Qwen 权重在 CUDA 执行，不模拟模型输出。

The swap test checks repeated LLM serving, SDXL output, measured memory release and correct LLM output after reload.
切換測試驗證連續 LLM 服務、SDXL 出圖、實測記憶體釋放及重新載入後的正確回答。
切换测试验证连续 LLM 服务、SDXL 出图、实测内存释放和重新加载后的正确回答。

Evidence is saved in `fan-out`; detailed scope is in `text-coverage.txt`.
證據保留於上述目錄；已驗證及待驗證範圍見涵蓋紀錄與 todo.txt。
证据保留于上述目录；已验证和待验证范围见覆盖记录及 todo.txt。
