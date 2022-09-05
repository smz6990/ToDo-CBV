from celery import Celery
from celery.schedules import crontab

from todo.models import Task


app = Celery()

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/10'), custom_delete_task.s())
    
@app.task
def custom_delete_task():
    if tasks := Task.objects.filter(is_done=True):
        tasks.delete()
        print('deleted successfully')
    print('there is no task to delete')
        
    