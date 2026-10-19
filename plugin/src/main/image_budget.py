"""Per-image processor limits without mutating a shared processor."""
from .errors import UserError


def options(processor, request):
    limit = request.get('max_image_tokens', 16000)
    image = getattr(processor, 'image_processor', None)
    if image is None or not hasattr(image, 'merge_size'):
        return {}
    factor = image.patch_size * image.merge_size
    maximum = limit * factor**2
    minimum = min(image.size.get('shortest_edge', factor**2), maximum)
    return {'images_kwargs':{'size':{'shortest_edge':minimum,'longest_edge':maximum}}}


def counts(processor, inputs, request):
    grid = inputs.get('image_grid_thw')
    if grid is not None:
        merge = processor.image_processor.merge_size**2
        values = [int(row.prod())//merge for row in grid]
    elif 'pixel_values' in inputs and getattr(processor,'image_seq_length',None):
        values = [processor.image_seq_length]*len(inputs['pixel_values'])
    else:
        values = []
    if any(n > request.get('max_image_tokens', 16000) for n in values):
        raise UserError(f'This image processor needs {max(values)} tokens per image; increase max_image_tokens')
    return values


def reply(request, count, context):
    requested = request.get('max_completion_tokens', request.get('max_tokens',256))
    available = context-count
    if available < 1:
        raise UserError(f'Actual prompt uses {count} tokens; context capacity is {context}')
    effective = min(requested, available)
    value = {**request, 'max_tokens':effective}
    if 'max_completion_tokens' in value:
        value['max_completion_tokens'] = effective
    return value, {'requested_output_tokens':requested, 'effective_output_tokens':effective,
                   'prompt_tokens':count, 'context_tokens':context}
