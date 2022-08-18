from django.contrib import admin
from todo.models import Task

@admin.register(Task)
class PostAdmin(admin.ModelAdmin):
    """
    creating class to modify the admin panel
    """
    date_hierarchy = 'created_date'
    list_display = ['author', 'content', 'is_done']
    list_filter = ['author', 'is_done']
    search_fields = ['author', 'content']
    
