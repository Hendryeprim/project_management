from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/create/', views.project_create, name='project_create'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('worklogs/', views.worklog_list, name='worklog_list'),
    path('worklogs/create/', views.worklog_create, name='worklog_create'),
    path('api/update-task-status/', views.update_task_status, name='update_task_status'),
]