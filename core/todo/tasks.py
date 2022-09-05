from celery import shared_task, Celery
from celery.schedules import crontab

from todo.models import Task


app = Celery()

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1.0, delete_task_beat.s(), name='delete-task-beat')
    
@app.task
def delete_task_beat():
    if tasks := Task.objects.filter(is_done=True):
        tasks.delete()
    