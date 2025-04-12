from rest_framework import serializers
from .models import Project, Task, TaskStatus

class ProjectSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Project.
    """
    class Meta:
        model = Project
        fields = '__all__'

class TaskStatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели TaskStatus.
    """
    class Meta:
        model = TaskStatus
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Task.
    """
    class Meta:
        model = Task
        fields = '__all__'
