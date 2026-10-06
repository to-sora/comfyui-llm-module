from marionette_driver.marionette import ActionSequence
from browser_helpers import click


def pixels(driver):
    return driver.execute_script('''const c=document.getElementById('mask-canvas');
      const data=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
      let n=0;for(let i=3;i<data.length;i+=4)if(data[i])n++;return n;''')


def test(driver):
    click(driver, "mask-enabled")
    driver.execute_script("document.getElementById('viewport').scrollIntoView({block:'center'})")
    x, y = driver.execute_script('''const r=document.getElementById('mask-canvas').getBoundingClientRect();
      return [Math.round(r.x+r.width/2),Math.round(r.y+r.height/2)];''')
    ActionSequence(driver, "pointer", "brush", {"pointerType": "mouse"}).pointer_move(x-50,y).pointer_down().pointer_move(x+50,y,300).pointer_up().perform()
    painted = pixels(driver)
    assert painted > 0
    click(driver, "mask-erase")
    ActionSequence(driver, "pointer", "brush", {"pointerType": "mouse"}).pointer_move(x,y).pointer_down().pointer_up().perform()
    erased = pixels(driver)
    assert erased < painted
    click(driver, "mask-undo")
    assert pixels(driver) == painted
    click(driver, "mask-clear")
    assert pixels(driver) == 0
    click(driver, "mask-enabled")
    return {"painted_pixels": painted, "after_erase": erased, "undo_restored": True, "clear": True}
