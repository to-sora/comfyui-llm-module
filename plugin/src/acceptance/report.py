import html
import json
from client import ROOT

RESULTS = []


def record(name, proof):
    RESULTS.append({"check": name, "status": "PASS", "evidence": proof})
    print("PASS", name, proof)


def save(error=None):
    folder = ROOT / "fan-out"
    folder.mkdir(exist_ok=True)
    status = "FAIL" if error else "PASS"
    report = {"status": status, "checks": RESULTS, "error": str(error) if error else None}
    (folder / "acceptance.json").write_text(json.dumps(report, ensure_ascii=False,
                                                     indent=2), encoding="utf-8")
    rows = "".join("<tr><td>" + "</td><td>".join(html.escape(str(v)) for v in
        (r["check"], r["status"], r["evidence"])) + "</td></tr>" for r in RESULTS)
    page = f"""<!doctype html><meta charset="utf-8"><title>Qwen acceptance</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto}}
td,th{{text-align:left;padding:12px;border-bottom:1px solid #ddd}}
h1{{color:{'#b91c1c' if error else '#166534'}}}</style>
<h1>{status} · ComfyUI Qwen 驗收</h1>
<p>Evidence: HTTPS workflows, RAM prefixes, GPU allocation and native unload.</p>
<p>證據：HTTPS 工作流、RAM 前綴、GPU 記憶體與原生卸載。</p>
<table><tr><th>Check / 項目</th><th>Result / 結果</th><th>Evidence / 證據</th></tr>{rows}</table>
<p>{html.escape(str(error)) if error else 'Acceptance model only / 驗收範圍為所選模型'}</p>"""
    (folder / "acceptance.html").write_text(page, encoding="utf-8")
