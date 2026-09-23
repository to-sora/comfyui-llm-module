import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def checked(action):
    folder = ROOT / "fan-out"
    folder.mkdir(exist_ok=True)
    path = folder / "colab-result.json"
    report = {"result": "RUNNING / 執行中",
              "started_at": datetime.now(timezone.utc).isoformat()}
    def save():
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    save()
    try:
        report.update(action())
    except BaseException as error:
        report.update(result="FAIL / 失敗", error=str(error)[:500],
                      log="plugin/data/comfy.log")
        save()
        raise
    save()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report
