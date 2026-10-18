from .settings import APP


def arguments(comfy):
    upstream=comfy/'custom_nodes/comfyui-llm-module'
    if upstream.is_dir() and upstream.resolve()==APP.parent:
        return []
    root=APP/'data/custom_nodes'
    root.mkdir(parents=True,exist_ok=True)
    link=root/'comfyui-llm-module'
    if not link.exists():
        link.symlink_to(APP.parent,target_is_directory=True)
    if link.resolve()!=APP.parent:
        raise RuntimeError('The project-local custom node link points to another repository')
    import yaml
    path=APP/'data/node-paths.yaml'
    path.write_text(yaml.safe_dump({'llm_extension':{'custom_nodes':str(root)}}))
    return ['--extra-model-paths-config',str(path)]
