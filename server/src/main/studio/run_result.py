import time


def finish(e,run):
    pending=e.db.all("SELECT id FROM images WHERE message_id=? AND kind='generated' AND file IS NULL AND deleted=0",(run['assistant_id'],))
    if pending:
        error=f'{len(pending)} image(s) could not be completed. Finished images are saved; try again for this request.'
        e.db.update('runs',run['id'],status='failed',finished=time.time(),error=error)
        e.publish(run,'run.error',{'message':error})
    else:
        e.db.update('runs',run['id'],status='done',finished=time.time())
