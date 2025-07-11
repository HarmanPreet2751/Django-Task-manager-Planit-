from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.models import User
from .models import Group, Task
from .forms import GroupForm, TaskForm

def groups_view(request):
    return redirect('group_list')

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

@login_required
def group_list(request):
    # Get all groups where user is a member or creator
    user_groups = request.user.group_memberships.all() | request.user.created_groups.all()
    print("User groups:", user_groups)

    # Get all groups where user's email is in the allowed emails list
    allowed_email_groups = Group.objects.filter(allowed_emails__icontains=request.user.email)
    print("Allowed email groups:", allowed_email_groups)

    # Combine the querysets and ensure uniqueness
    groups = (user_groups | allowed_email_groups).distinct()
    print("Final groups:", groups)

    return render(request, 'group_list.html', {'groups': groups})

@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            group.members.add(request.user)
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'group_form.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Check if user has access (creator, member, or email in allowed_emails)
    user_email = request.user.email.lower()
    allowed_emails = group.get_allowed_emails_list()
    is_allowed = (request.user == group.creator or
                 request.user in group.members.all() or
                 user_email in allowed_emails)

    if not is_allowed:
        return redirect('group_list')

    # Automatically add user to members if they're allowed but not yet a member
    if user_email in allowed_emails and request.user not in group.members.all():
        group.members.add(request.user)

    tasks = group.tasks.all()
    if request.method == 'POST':
        if 'task_form' in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.group = group
                task.created_by = request.user
                task.save()
                return redirect('group_detail', group_id=group_id)
        elif 'complete_task' in request.POST:
            task_id = request.POST.get('task_id')
            task = get_object_or_404(Task, id=task_id)
            task.completed = not task.completed
            task.save()
            return redirect('group_detail', group_id=group_id)
        elif 'update_priority' in request.POST:
            task_id = request.POST.get('task_id')
            priority = request.POST.get('priority')
            task = get_object_or_404(Task, id=task_id)
            task.priority = priority
            task.save()
            return redirect('group_detail', group_id=group_id)
        elif 'delete_task' in request.POST:
            task_id = request.POST.get('task_id')
            task = get_object_or_404(Task, id=task_id)
            task.delete()
            return redirect('group_detail', group_id=group_id)
    else:
        task_form = TaskForm()

    return render(request, 'group_detail.html', {
        'group': group,
        'tasks': tasks,
        'task_form': task_form,
        'is_creator_or_allowed': (request.user == group.creator or user_email in allowed_emails)
    })
