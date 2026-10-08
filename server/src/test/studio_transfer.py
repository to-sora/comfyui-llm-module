from browser_helpers import until


def insert(d,source,kind):
    result=d.execute_async_script('''const done=arguments[arguments.length-1];
      const kind=arguments[1];
      fetch('/api/images/'+arguments[0]).then(r=>r.blob()).then(blob=>{
        const file=new File([blob],'uat-'+kind+'.png',{type:'image/png'});
        let event;
        if(kind==='paste'){
          event=new ClipboardEvent('paste',{bubbles:true,cancelable:true});
          event.clipboardData.items.add(file);
        }else{
          const transfer=new DataTransfer();transfer.items.add(file);
          event=new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true});
        }
        document.querySelector('#prompt').dispatchEvent(event);done(true);
      }).catch(error=>done(error.message));''',script_args=[source,kind],sandbox=None)
    assert result is True,result
