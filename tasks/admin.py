from django.contrib import admin
from .models import Task, TaskSwap


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'assigned_to_user', 'assigned_to_group', 'created_by', 'deadline', 'created_at']
    list_filter = ['priority', 'status', 'created_at', 'deadline']
    search_fields = ['title', 'description', 'created_by__user_id', 'assigned_to_user__user_id']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'priority', 'status', 'deadline')
        }),
        ('Assignment', {
            'fields': ('assigned_to_user', 'assigned_to_group', 'group', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskSwap)
class TaskSwapAdmin(admin.ModelAdmin):
    list_display = ['task', 'requester', 'target_user', 'status', 'admin_approved', 'user_approved', 'created_at']
    list_filter = ['status', 'admin_approved', 'user_approved', 'created_at']
    search_fields = ['task__title', 'requester__user_id', 'target_user__user_id']
    readonly_fields = ['created_at', 'updated_at', 'admin_approved_at', 'user_approved_at']
