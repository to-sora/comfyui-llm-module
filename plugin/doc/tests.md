# Tests / 測試 / 测试

```bash
bash plugin/install-test-assets.sh
plugin/venv/bin/python -m unittest discover -s plugin/src/test -p 'test_*.py' -v
```

CPU tensor tests use real Qwen3.5 code, its official processor, and small random weights.
CPU 張量測試採用真實 Qwen3.5 程式、官方 processor 與小型隨機權重。
CPU 张量测试采用真实 Qwen3.5 程序、官方 processor 与小型随机权重。

These tests cover cache consistency and text/image state isolation. Trained-model quality and CUDA require the Colab notebook.
上述測試涵蓋快取一致性及文字／圖片狀態隔離。訓練模型品質與 CUDA 驗收使用 Colab notebook。
上述测试涵盖缓存一致性及文字／图片状态隔离。训练模型质量与 CUDA 验收使用 Colab notebook。

Missing processor assets produce an explicit tensor-suite skip; the asset installer enables those tests.
缺少 processor 素材時，張量測試會顯示跳過；安裝上述素材後啟用。
缺少 processor 素材时，张量测试会显示跳过；安装上述素材后启用。

```bash
plugin/venv/bin/python -m plugin.src.test.native_accept
plugin/venv/bin/python -m plugin.src.test.service_accept
```

The installed ComfyUI provides native lifecycle and HTTPS API checks on CPU, with random Qwen3.5 weights and real inference code.
已安裝的 ComfyUI 提供 CPU 原生生命週期與 HTTPS API 測試，採用 Qwen3.5 隨機權重及真實推理程式。
已安装的 ComfyUI 提供 CPU 原生生命周期与 HTTPS API 测试，采用 Qwen3.5 随机权重及真实推理程序。

Service proof: `fan-out/cpu-service-result.json`; log: `plugin/data/comfy-test.log`.
服務證據及紀錄位於上述路徑；測試結束會停止服務並還原啟動設定。
服务证据及记录位于上述路径；测试结束会停止服务并还原启动配置。
