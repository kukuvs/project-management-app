from django import forms
from django.contrib.auth.models import User
from .models import Project, Task, TaskStatus

class UserRegistrationForm(forms.ModelForm):
    """
    Форма регистрации пользователя.
    """
    password = forms.CharField(widget=forms.PasswordInput) # Пароль
    password_confirm = forms.CharField(widget=forms.PasswordInput) # Подтверждение пароля
    
    class Meta:
        """
        Мета-класс для формы регистрации пользователя.
        """
        model = User # Модель пользователя
        fields = ['username', 'password', 'password_confirm'] # Поля формы
    
    def clean(self):
        """
        Метод для валидации данных формы.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Пароли не совпадают.")
        return cleaned_data

class UserLoginForm(forms.Form):
    """
    Форма входа пользователя.
    """
    username = forms.CharField() # Имя пользователя
    password = forms.CharField(widget=forms.PasswordInput) # Пароль

class ProjectForm(forms.ModelForm):
    """
    Форма для создания/редактирования проекта.
    """
    class Meta:
        """
        Мета-класс для формы проекта.
        """
        model = Project # Модель проекта
        fields = ['name'] # Поля формы

class TaskForm(forms.ModelForm):
    """
    Форма для создания/редактирования задачи.
    """
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    ) # Назначенные пользователи
    
    class Meta:
        """
        Мета-класс для формы задачи.
        """
        model = Task # Модель задачи
        fields = ['title', 'description', 'status', 'assigned_users', 'deadline'] # Поля формы
    
    def __init__(self, *args, **kwargs):
        """
        Инициализатор формы задачи.
        """
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            # Ограничиваем выбор исполнителей только участниками проекта
            self.fields['assigned_users'].queryset = User.objects.filter(projectmembership__project=project)
            # Ограничиваем выбор статусов только статусами данного проекта
            self.fields['status'].queryset = TaskStatus.objects.filter(project=project).order_by('order')


class StatusForm(forms.ModelForm):
    """
    Форма для создания/редактирования статуса задачи.
    """
    class Meta:
        """
        Мета-класс для формы статуса.
        """
        model = TaskStatus # Модель статуса
        fields = ['name', 'order'] # Поля формы
