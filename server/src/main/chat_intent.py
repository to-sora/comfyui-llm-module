def apply(payload, job):
    if job.get("intent") == "inspect":
        payload.update(tools=[], tool_choice="none")
        payload["messages"][0]["content"] = "Inspect the actual attached images against the user's requirements. Report visible matches and problems."
    return payload
