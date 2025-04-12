from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    
    path('register/', views.register, name='register'),  # Регистрация
    path('login/', views.user_login, name='login'),  # Вход
    path('logout/', views.user_logout, name='logout'),  # Выход
    
    path('projects/', views.project_list, name='project_list'),  # Список проектов
    path('projects/join_by_code/', views.project_join_by_code, name='project_join_by_code'),  # Присоединиться к проекту по коду
    path('projects/<int:project_id>/remove_member/<int:user_id>/', views.remove_member, name='remove_member'),  # Удалить участника из проекта
    path('projects/create/', views.project_create, name='project_create'),  # Создать проект
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),  # Детали проекта
    path('projects/<int:project_id>/join/<uuid:invite_code>/', views.project_join, name='project_join'),  # Присоединиться к проекту по приглашению
    path('projects/<int:project_id>/add_member/', views.add_member, name='add_member'),  # Добавить участника в проект
    
    path('tasks/', views.task_list, name='task_list'),  # Список задач
    path('tasks/create/<int:project_id>/', views.task_create, name='task_create'),  # Создать задачу
    path('tasks/edit/<int:task_id>/', views.task_edit, name='task_edit'),  # Редактировать задачу
    path('tasks/move/<int:task_id>/<int:status_id>/', views.task_move, name='task_move'),  # Переместить задачу
    
    path('statuses/create/<int:project_id>/', views.status_create, name='status_create'),  # Создать статус
    path('statuses/edit/<int:status_id>/', views.status_edit, name='status_edit'),  # Редактировать статус
    path('statuses/delete/<int:status_id>/', views.status_delete, name='status_delete'),  # Удалить статус
]
