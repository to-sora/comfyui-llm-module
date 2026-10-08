import hashlib
import json
import time
import zipfile
from pathlib import Path
from PIL import Image
from marionette_driver.by import By
from browser_helpers import until
from studio_helpers import ROOT,call

DOWNLOADS=ROOT/'server/data/tmp/downloads'


def press(d,text):
    d.find_element(By.XPATH,'//button[normalize-space(.)='+json.dumps(text,ensure_ascii=False)+']').click()


def downloaded(action,suffix):
    DOWNLOADS.mkdir(exist_ok=True)
    previous=set(DOWNLOADS.iterdir())
    action()
    return until(lambda:next((p for p in set(DOWNLOADS.iterdir())-previous
        if p.suffix==suffix and p.stat().st_size and not p.with_suffix(p.suffix+'.part').exists()),None),30)


def select(d,ident):
    d.find_element(By.CSS_SELECTOR,f'.library-card:has([data-image="{ident}"]) input').click()


def upload(d,folder):
    paths=[]
    for name,color in [('a','red'),('b','blue')]:
        image=Image.new('RGBA',(96,80),(0,0,0,0))
        image.paste(color,(24,20,72,60))
        path=folder/('uat-library-'+name+'.png')
        image.save(path)
        paths.append(str(path))
    d.find_element(By.ID,'files').send_keys('\n'.join(paths))
    until(lambda:d.execute_script("return document.querySelectorAll('.attachment').length===2"),30)
    return [r for r in call('/images')['images'] if r['recipe'].get('name','').startswith('uat-library-')][:2]


def verify_downloads(png,jpg,archive,images):
    digest=hashlib.sha256(png.read_bytes()).hexdigest()
    assert digest==images[0]['sha256']
    with Image.open(jpg) as picture:
        assert picture.format=='JPEG' and picture.size==(96,80)
        assert all(v>240 for v in picture.convert('RGB').getpixel((0,0)))
    with zipfile.ZipFile(archive) as source:
        assert set(source.namelist())=={r['id']+'.png' for r in images}
        for item in images:
            assert hashlib.sha256(source.read(item['id']+'.png')).hexdigest()==item['sha256']
    return {'png_sha256':digest,'jpeg_white_alpha':True,'zip_originals':2}
