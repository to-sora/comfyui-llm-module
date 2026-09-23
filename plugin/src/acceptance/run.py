from client import call, workflow, unload
from graphs import graph
from report import record, save


def check():
    info = call("/object_info")
    assert all(n in info for n in ("QwenLoader", "QwenGenerate", "QwenBatch"))
    initial = call("/qwen/status")
    prefixes = [p for m in initial["models"] for p in m["prefix"]]
    assert prefixes and all(p["warmed"] >= 2 and p["bytes"] > 0 for p in prefixes)
    record("Startup / 啟動", "3 nodes; 2 prefixes in RAM before first prompt")
    output = workflow(graph())
    assert output[0].strip()
    state = call("/qwen/status")
    assert any(p["hits"] > 0 for m in state["models"] for p in m["prefix"])
    before = state["cuda_allocated"]
    assert before > 1000000
    record("Text + prefix / 文字與前綴", output[0][:100])
    output = workflow(graph(image=True))
    assert output[0].strip()
    record("Vision / 視覺", output[0][:100])
    before = call("/qwen/status")["cuda_allocated"]
    state = unload()
    assert state["cuda_allocated"] < before - 1000000
    record("Native unload / 原生卸載",
           f"CUDA bytes {before} → {state['cuda_allocated']}")
    output = workflow(graph())
    assert output[0].strip()
    assert any(m["resident"] for m in call("/qwen/status")["models"])
    record("Reload / 重載", "Inference after native /free")
    unload()
    output = workflow(graph(mode="concurrent", batch=True))
    assert len(output) == 4 and all(v.strip() for v in output)
    state = call("/qwen/status")
    assert any(m["workers"] == 2 and m["resident"] for m in state["models"])
    record("Concurrent / 併發", "4 prompts completed through 2 model instances")
    unload()


try:
    check()
except BaseException as error:
    save(error)
    raise
else:
    save()
