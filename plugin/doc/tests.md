# Verification / 驗證 / 验证

Run against the project's active HTTPS service:
針對專案正在執行的 HTTPS 服務測試：
针对项目正在运行的 HTTPS 服务测试：

```bash
plugin/.local-tool-app/venv/bin/python -m plugin.src.test.sdxl_smoke
plugin/.local-tool-app/venv/bin/python -m plugin.src.test.swap_accept
plugin/.local-tool-app/venv/bin/python -m plugin.src.test.model_accept Qwen3.5-9B hqq_4
plugin/.local-tool-app/venv/bin/python -m plugin.src.test.concurrent_accept
plugin/.local-tool-app/venv/bin/python -m plugin.src.test.api_accept
```

Tests use actual SDXL and Qwen weights on CUDA, without mocked generation.
測試使用真實 SDXL 與 Qwen 權重於 CUDA 執行，不模擬模型輸出。
测试使用真实 SDXL 和 Qwen 权重在 CUDA 执行，不模拟模型输出。

Images and tool results are controlled fixtures, including a client-provided 28°C weather result.
圖片及工具結果為固定測試輸入，包括客戶端提供的 28°C 天氣結果。
图片及工具结果为固定测试输入，包括客户端提供的 28°C 天气结果。

The swap test checks repeated LLM serving, SDXL output, measured memory release and correct LLM output after reload.
切換測試驗證連續 LLM 服務、SDXL 出圖、實測記憶體釋放及重新載入後的正確回答。
切换测试验证连续 LLM 服务、SDXL 出图、实测内存释放和重新加载后的正确回答。

Evidence is saved in `fan-out`; detailed scope is in `text-coverage.txt`.
證據保留於上述目錄；已驗證及待驗證範圍見涵蓋紀錄與 todo.txt。
证据保留于上述目录；已验证和待验证范围见覆盖记录及 todo.txt。

Firefox: install `plugin/install-test-tools.sh`, then run `plugin.src.test.browser_accept` using the same Python. Requires `~/UAT-firefox/firefox/firefox`.
Firefox 驗收透過 Run 按鈕執行節點，檢查三種畫面尺寸，並清理測試瀏覽器程序。
Firefox 验收通过 Run 按钮执行节点，检查三种画面尺寸，并清理测试浏览器进程。

`plugin.src.test.lifecycle_accept` stops this service, checks port conflicts and `--force`, then stops its test service.
生命週期測試會停止本服務，驗證連接埠衝突與強制啟動；結束後需重新啟動服務。
生命周期测试会停止本服务，验证端口冲突与强制启动；结束后需重新启动服务。
