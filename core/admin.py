from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, Task, WorkLog, TaskHistory

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active', 'created_at')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_active', 'total_tasks', 'completed_tasks', 'created_at')
    list_filter = ('is_active', 'created_at', 'created_by')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assignee', 'status', 'priority', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'project', 'assignee', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('status', 'priority')

@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'task', 'hours_spent', 'date', 'created_at')
    list_filter = ('user', 'project', 'date', 'created_at')
    search_fields = ('description',)

@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'action', 'created_at')
    list_filter = ('action', 'user', 'created_at')
    readonly_fields = ('created_at',)