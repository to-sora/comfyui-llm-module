import torch


class Layers:
    def __init__(self, model):
        self.values, self.rows, self.handles = {}, [], []
        self.phase = 'full'
        for name,module in model.model.language_model.layers[0].named_modules():
            self.handles.append(module.register_forward_hook(self.hook(name)))

    def hook(self, name):
        def record(module, args, output):
            if not isinstance(output, torch.Tensor):
                return
            if self.phase == 'full':
                self.values[name] = output.detach().cpu()
            elif self.phase == 'prefix':
                before = self.values[name]
                before = before[tuple(slice(0,n) for n in output.shape)]
                delta = before.float()-output.detach().cpu().float()
                self.rows.append({'module':name,'max':delta.abs().max().item(),
                                  'mean':delta.abs().mean().item()})
        return record

    def close(self):
        for handle in self.handles:
            handle.remove()
        self.values.clear()
