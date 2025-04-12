from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserLoginForm, ProjectForm, TaskForm, StatusForm
from .models import Project, ProjectMembership, TaskStatus, Task

def index(request):
    """
    Главная страница с выбором входа или регистрации.
    """
    return render(request, 'index.html')

def register(request):
    """
    Регистрация пользователя. После успешной регистрации происходит перенаправление на страницу входа.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    """
    Вход пользователя. После успешного входа перенаправляет на список проектов.
    """
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('project_list')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    """
    Выход пользователя.
    """
    logout(request)
    return redirect('login')

@login_required
def project_list(request):
    """
    Список проектов, в которых состоит текущий пользователь.
    """
    projects = Project.objects.filter(members__user=request.user).distinct()
    return render(request, 'project_list.html', {'projects': projects})


@login_required
def project_create(request):
    """
    Создание нового проекта.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user  # <-- устанавливаем владельца
            project.save()
            ProjectMembership.objects.create(project=project, user=request.user)
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form})


@login_required
def remove_member(request, project_id, user_id):
    """
    Удаление пользователя (user_id) из проекта (project_id).
    Только владелец проекта может это сделать.
    """
    project = get_object_or_404(Project, id=project_id)
    # Проверяем, является ли текущий пользователь владельцем
    if project.owner != request.user:
        return redirect('project_detail', project_id=project.id)

    # Нельзя удалить самого себя, если ты владелец (по желанию можно разрешить)
    if user_id == request.user.id:
        return redirect('project_detail', project_id=project.id)

    membership = get_object_or_404(ProjectMembership, project=project, user_id=user_id)
    membership.delete()
    return redirect('project_detail', project_id=project.id)


@login_required
def project_detail(request, project_id):
    """
    Детали проекта: отображается Kanban-доска с колонками (статусами) и задачами.
    Только участники проекта могут видеть детали.
    """
    project = get_object_or_404(Project, id=project_id)
    if not project.members.filter(user=request.user).exists():
        return redirect('project_list')
    statuses = TaskStatus.objects.filter(project=project).order_by('order')
    tasks = Task.objects.filter(project=project)
    return render(request, 'project_detail.html', {
        'project': project,
        'statuses': statuses,
        'tasks': tasks,
    })

@login_required
def project_join(request, project_id, invite_code):
    """
    Присоединение к проекту по invite_code.
    Если код совпадает с кодом проекта, то текущий пользователь добавляется в проект.
    """
    project = get_object_or_404(Project, id=project_id)
    if str(project.invite_code) == str(invite_code):
        ProjectMembership.objects.get_or_create(project=project, user=request.user)
    return redirect('project_detail', project_id=project.id)

@login_required
def add_member(request, project_id):
    """
    Добавление участника в проект по уникальному коду (в данном примере – по имени пользователя).
    """
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        unique_code = request.POST.get('unique_code')
        try:
            user = User.objects.get(username=unique_code)
            ProjectMembership.objects.get_or_create(project=project, user=user)
        except User.DoesNotExist:
            pass
    return redirect('project_detail', project_id=project.id)

@login_required
def task_list(request):
    """
    Список всех задач.
    """
    tasks = Task.objects.all()
    return render(request, 'task_list.html', {'tasks': tasks})

@login_required
def task_create(request, project_id):
    """
    Создание новой задачи в проекте.
    """
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            form.save_m2m()
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(project=project)
    return render(request, 'task_form.html', {'form': form, 'project': project})


@login_required
def task_edit(request, task_id):
    """
    Редактирование задачи.
    """
    task = get_object_or_404(Task, id=task_id)
    project = task.project
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(instance=task, project=project)
    return render(request, 'task_form.html', {'form': form, 'task': task})


@login_required
def task_move(request, task_id, status_id):
    """
    Перемещение задачи в другой статус (колонку).
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        new_status = get_object_or_404(TaskStatus, id=status_id)
        task.status = new_status
        task.save()
        return HttpResponse(status=204)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def status_create(request, project_id):
    """
    Создание нового статуса (колонки) для проекта.
    """
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = StatusForm(request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.project = project
            status.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = StatusForm()
    return render(request, 'status_form.html', {'form': form})

@login_required
def status_edit(request, status_id):
    """
    Редактирование статуса проекта.
    """
    status = get_object_or_404(TaskStatus, id=status_id)
    if request.method == 'POST':
        form = StatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            return redirect('project_detail', project_id=status.project.id)
    else:
        form = StatusForm(instance=status)
    return render(request, 'status_form.html', {'form': form, 'status': status})

@login_required
def status_delete(request, status_id):
    """
    Удаление статуса проекта.
    """
    status = get_object_or_404(TaskStatus, id=status_id)
    project_id = status.project.id
    status.delete()
    return redirect('project_detail', project_id=project_id)


@login_required
def project_join_by_code(request):
    """
    Присоединение к проекту по invite_code, введённому пользователем.
    """
    if request.method == 'POST':
        code = request.POST.get('invite_code')
        try:
            project = Project.objects.get(invite_code=code)
            ProjectMembership.objects.get_or_create(project=project, user=request.user)
            return redirect('project_detail', project_id=project.id)
        except Project.DoesNotExist:
            # Можно вывести сообщение об ошибке
            pass
    return render(request, 'join_by_code.html')