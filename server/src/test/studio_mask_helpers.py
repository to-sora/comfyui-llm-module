import json
from marionette_driver.by import By
from marionette_driver.marionette import ActionSequence
from browser_helpers import until
from studio_helpers import call,record


def press(d,text):
    d.find_element(By.XPATH,'//button[normalize-space(.)='+json.dumps(text)+']').click()


def paint(d):
    def pixels():
        return d.execute_script("const c=document.querySelector('.picture-plane canvas');const a=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return a.filter((v,i)=>i%4===3&&v>0).length")
    x,y=d.execute_script("const r=document.querySelector('canvas').getBoundingClientRect();return [Math.round(r.x+r.width/2),Math.round(r.y+r.height/2)]")
    def stroke(a,b):
        ActionSequence(d,'pointer','mask',{'pointerType':'mouse'}).pointer_move(a,y).pointer_down().pointer_move(b,y,250).pointer_up().perform()
    stroke(x-35,x+35)
    count=pixels();assert count>0
    press(d,'Erase');stroke(x,x+1)
    assert pixels()<count
    press(d,'Undo');until(lambda:pixels()==count,10)
    press(d,'Clear');assert pixels()==0
    press(d,'Brush');stroke(x-35,x+35)
    return {'painted_pixels':pixels(),'erase':True,'undo':True,'clear':True}


def wait(d,chat,previous=None):
    def done():
        value=call('/chats/'+chat+'/messages')
        runs=[r for r in value['runs'].values() if r['id']!=previous]
        return (value,runs[-1]) if runs and runs[-1]['status'] not in ('running','queued') else None
    value,run=until(done,300)
    record('edit-run',call('/debug/runs/'+run['id']))
    assert run['status']=='done',run.get('error')
    until(lambda:d.execute_script("return document.getElementById('stop').hidden"),30)
    return value,run
