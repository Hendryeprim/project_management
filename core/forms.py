from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q   # clean import for queries

from .models import User, Project, Task, WorkLog


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'members')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4}),
            'members': forms.CheckboxSelectMultiple(attrs={'class': 'space-y-2'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'project', 'assignee',
                  'status', 'priority', 'due_date')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4}),
            'project': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'assignee': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }


class WorkLogForm(forms.ModelForm):
    class Meta:
        model = WorkLog
        fields = ('project', 'task', 'description', 'hours_spent', 'date')
        widgets = {
            'project': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'task': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4}),
            'hours_spent': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.1'}),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md '
                         'focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Filter projects to only those the user is a member of or created
            self.fields['project'].queryset = Project.objects.filter(
                Q(members=user) | Q(created_by=user)
            ).distinct()

        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
