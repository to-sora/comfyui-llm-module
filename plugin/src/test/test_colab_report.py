import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from plugin.colab import report
from plugin.src.main.settings import APP, environment


class ColabReportTests(unittest.TestCase):
    def test_failed_rerun_replaces_previous_pass(self):
        environment()
        with tempfile.TemporaryDirectory(dir=APP / "data/tmp") as folder:
            root = Path(folder)
            with patch.object(report, "ROOT", root):
                report.checked(lambda: {"result": "PASS", "inference": "red"})
                def failed():
                    current = json.loads((root / "fan-out/colab-result.json").read_text())
                    self.assertTrue(current["result"].startswith("RUNNING"))
                    raise RuntimeError("CUDA out of memory")
                with self.assertRaisesRegex(RuntimeError, "CUDA out of memory"):
                    report.checked(failed)
            saved = json.loads((root / "fan-out/colab-result.json").read_text())
            self.assertTrue(saved["result"].startswith("FAIL"))
            self.assertNotIn("inference", saved)
            self.assertEqual(saved["error"], "CUDA out of memory")
