from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import User, Project, Task, WorkLog, TaskHistory
from .forms import CustomUserCreationForm, ProjectForm, TaskForm, WorkLogForm
import json
from django.http import JsonResponse

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    
    # Get user's projects
    if user.is_super_admin:
        projects = Project.objects.filter(is_active=True)
        tasks = Task.objects.all()
        work_logs = WorkLog.objects.all()
    else:
        projects = Project.objects.filter(
            Q(members=user) | Q(created_by=user),
            is_active=True
        ).distinct()
        tasks = Task.objects.filter(Q(assignee=user) | Q(project__in=projects))
        work_logs = WorkLog.objects.filter(user=user)
    
    # Get recent tasks
    recent_tasks = tasks.order_by('-updated_at')[:5]
    
    # Get today's work logs
    today_logs = work_logs.filter(date=timezone.now().date())
    
    # Get task statistics
    task_stats = {
        'total': tasks.count(),
        'todo': tasks.filter(status='todo').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'done': tasks.filter(status='done').count(),
    }
    
    # Get overdue tasks
    overdue_tasks = tasks.filter(
        due_date__lt=timezone.now().date(),
        status__in=['todo', 'in_progress']
    )[:5]
    
    context = {
        'projects': projects[:5],  # Show only 5 recent projects
        'recent_tasks': recent_tasks,
        'today_logs': today_logs,
        'task_stats': task_stats,
        'overdue_tasks': overdue_tasks,
        'total_projects': projects.count(),
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def project_list(request):
    user = request.user
    
    if user.is_super_admin:
        projects = Project.objects.filter(is_active=True)
    else:
        projects = Project.objects.filter(
            Q(members=user) | Q(created_by=user),
            is_active=True
        ).distinct()
    
    return render(request, 'core/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if not request.user.is_super_admin:
        if request.user not in project.members.all() and project.created_by != request.user:
            messages.error(request, 'You do not have access to this project.')
            return redirect('project_list')
    
    tasks = project.tasks.all()
    recent_logs = project.work_logs.all()[:10]
    
    context = {
        'project': project,
        'tasks': tasks,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'core/project_detail.html', context)

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Project created successfully!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'core/project_form.html', {'form': form, 'title': 'Create Project'})

@login_required
def task_list(request):
    user = request.user
    
    if user.is_super_admin:
        tasks = Task.objects.all()
    else:
        user_projects = Project.objects.filter(
            Q(members=user) | Q(created_by=user)
        ).distinct()
        tasks = Task.objects.filter(
            Q(assignee=user) | Q(project__in=user_projects)
        )
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)
    
    # Filter by project if provided
    project_id = request.GET.get('project')
    if project_id:
        tasks = tasks.filter(project_id=project_id)
    
    return render(request, 'core/task_list.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            
            # Create task history
            TaskHistory.objects.create(
                task=task,
                user=request.user,
                action='created',
                description=f'Task "{task.title}" was created'
            )
            
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm()
    
    return render(request, 'core/task_form.html', {'form': form, 'title': 'Create Task'})

@login_required
def worklog_list(request):
    user = request.user
    
    if user.is_super_admin:
        work_logs = WorkLog.objects.all()
    else:
        work_logs = WorkLog.objects.filter(user=user)
    
    # Filter by date if provided
    date = request.GET.get('date')
    if date:
        work_logs = work_logs.filter(date=date)
    
    return render(request, 'core/worklog_list.html', {'work_logs': work_logs})

@login_required
def worklog_create(request):
    if request.method == 'POST':
        form = WorkLogForm(request.POST, user=request.user)
        if form.is_valid():
            work_log = form.save(commit=False)
            work_log.user = request.user
            work_log.save()
            messages.success(request, 'Work log created successfully!')
            return redirect('worklog_list')
    else:
        form = WorkLogForm(user=request.user)
    
    return render(request, 'core/worklog_form.html', {'form': form, 'title': 'Create Work Log'})

@login_required
def update_task_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('status')
        
        try:
            task = Task.objects.get(pk=task_id)
            
            # Check if user has permission to update this task
            if not request.user.is_super_admin and task.assignee != request.user:
                return JsonResponse({'success': False, 'error': 'Permission denied'})
            
            old_status = task.status
            task.status = new_status
            task.save()
            
            # Create task history
            TaskHistory.objects.create(
                task=task,
                user=request.user,
                action='status_changed',
                old_value=old_status,
                new_value=new_status,
                description=f'Task status changed from {old_status} to {new_status}'
            )
            
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})