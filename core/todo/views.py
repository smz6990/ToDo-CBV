from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from .forms import TaskForm


class TaskListView(LoginRequiredMixin, ListView):
    """
    This is a view class that show the task created by each user that logged in
    """
    allow_empty = True
    template_name = 'todo/index.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        tasks = Task.objects.filter(author = self.request.user)
        return tasks
    

class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    This is a view that create new task for user
    """
    template_name = reverse_lazy("todo:index")
    form_class  = TaskForm
    field = ['content']
    success_url = reverse_lazy("todo:index")
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
   
 
class TaskDoneUpdateView(LoginRequiredMixin, UpdateView):
    """
    This is a view that change the status (is_done) of task to True
    """
    model = Task
    template_name = reverse_lazy("todo:index")
    
    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        if task.author == self.request.user:
            task.is_done = True
            task.save()
        return redirect(reverse_lazy("todo:index"))
    
    
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """
    This a is class that delete a task
    """
    success_url = reverse_lazy('todo:index')
    def get_queryset(self):
        tasks = Task.objects.filter(author = self.request.user)
        return tasks
    
    
class TaskEditView(LoginRequiredMixin, UpdateView):
    """
    This is a class that edit a task content
    """
    form_class = TaskForm
    success_url = reverse_lazy('todo:index')
    template_name = 'todo/task_edit.html'
    
    def get_queryset(self):
        tasks = Task.objects.filter(author = self.request.user)
        return tasks