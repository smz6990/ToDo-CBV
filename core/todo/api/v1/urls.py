from email.mime import base
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('task', views.TaskModelViewSet, basename='task')

app_name = 'api-v1'
urlpatterns = router.urls