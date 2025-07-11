from django.contrib import admin
from .models import Task
# Register your models here.


class TaskAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ['title', 'task', 'date', 'priority', 'completed', 'created_at', 'updated_at', 'id']
    
    # Fields to filter by in the sidebar
    list_filter = ('priority', 'completed', 'date', 'created_at', 'updated_at')
    
    # Fields to search through
    search_fields = ('title', 'task')
    
    # Enable date hierarchy for easier navigation
    date_hierarchy = 'date'
    
    # Make some fields read-only in the detail view
    readonly_fields = ('created_at', 'updated_at')
    
    # Order the tasks by priority and date by default
    ordering = ('-priority', 'date')
    
    # Customize the form layout (optional)
    fieldsets = (
        (None, {
            'fields': ('title', 'task', 'date')
        }),
        ('Status', {
            'fields': ('priority', 'completed')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
    
    # Add pagination to the list view
    list_per_page = 20

# Register the Task model with the custom admin class
admin.site.register(Task, TaskAdmin)


