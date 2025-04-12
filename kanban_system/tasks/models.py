from django.contrib.auth.models import User
from django.db import models
import uuid

class Project(models.Model):
    name = models.CharField(max_length=255) # Название проекта
    created_at = models.DateTimeField(auto_now_add=True) # Дата создания
    invite_code = models.UUIDField(default=uuid.uuid4, unique=True) # Код для приглашения
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects", null=True) # Владелец проекта

    def __str__(self):
        return self.name

class ProjectMembership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members") # Проект
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Пользователь
    
    class Meta:
        unique_together = ('project', 'user')
    
    def __str__(self):
        return f"{self.user.username} in {self.project.name}"

class TaskStatus(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="statuses") # Проект
    name = models.CharField(max_length=100) # Название статуса
    order = models.PositiveIntegerField() # Порядок сортировки
    
    class Meta:
        unique_together = ('project', 'name')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} ({self.project.name})"

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks") # Проект
    title = models.CharField(max_length=255) # Название задачи
    description = models.TextField(blank=True, null=True) # Описание задачи
    status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, related_name="tasks") # Статус задачи
    assigned_users = models.ManyToManyField(User, related_name="tasks", blank=True) # Назначенные пользователи
    deadline = models.DateTimeField(null=True, blank=True) # Срок выполнения
    created_at = models.DateTimeField(auto_now_add=True) # Дата создания
    
    def __str__(self):
        return self.title
