def ensure_loaded(engine):
    from comfy import model_management as mm
    for entry in mm.current_loaded_models:
        if entry.model is engine.patcher and engine.resident:
            entry.currently_used = True
            return
    mm.load_models_gpu([engine.patcher], force_full_load=True)
