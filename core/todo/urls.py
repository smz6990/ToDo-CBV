from django.urls import path,include
from . import views

app_name = 'todo'


urlpatterns = [
    path('',views.TaskListView.as_view(),name='index'),
    path('add/',views.TaskCreateView.as_view(),name='add'),
    path('<int:pk>/done/',views.TaskDoneUpdateView.as_view(),name='done'),
    path('<int:pk>/delete/',views.TaskDeleteView.as_view(),name='delete'),
    path('<int:pk>/edit/',views.TaskEditView.as_view(),name='edit'),
    path('api/v1/',include("todo.api.v1.urls")),
    
]
