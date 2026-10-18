from .basic_edits import OPERATIONS


def fields():
    options={k:{'type':'number'} for k in ('width','height','left','top','right','bottom',
                                         'angle','amount','size','x','y','stroke')}
    options.update(text={'type':'string'},color={'type':'string','description':'CSS hex color'})
    return {'operation':{'type':'string','enum':['sdxl',*OPERATIONS],
              'description':'Default sdxl for creative changes. Use text for exact lettering; local edits avoid image-model generation.'},
            'options':{'type':'object','properties':options,'additionalProperties':False,
              'description':'Local edits only: text, size, x/y, color; width/height; crop left/top/right/bottom; amount for adjustments.'}}
