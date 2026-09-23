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
