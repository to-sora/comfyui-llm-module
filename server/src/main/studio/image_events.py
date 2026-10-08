import time


def callback(e,run,tasks):
    async def receive(value):
        data,kind = value.get('data',{}),value['type']
        if kind=='preview':
            ident=tasks[0]['id']
            e.previews[ident]=(data['bytes'],data.get('image_type','image/jpeg'))
            e.publish(run,'image.preview',{'image_id':ident,'url':f'/api/previews/{ident}?t={time.time_ns()}'})
        elif kind=='progress':
            for task in tasks:
                e.publish(run,'image.progress',{'image_id':task['id'],'step':data['value'],'total':data['max'],
                    'message':f'Drawing · {data["value"]} of {data["max"]}'})
        elif kind=='execution_start':
            for task in tasks:
                e.publish(run,'image.progress',{'image_id':task['id'],'message':'Getting the image model ready'})
    return receive
