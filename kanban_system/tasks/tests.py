from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from tasks.models import Project, Task

class ProjectTaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.project = Project.objects.create(name="Test Project")
        self.task = Task.objects.create(title="Test Task", project=self.project)

    def test_login(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 200)

    def test_project_list(self):
        response = self.client.get(reverse('project_list'))
        self.assertContains(response, 'Test Project')

    def test_project_detail(self):
        response = self.client.get(reverse('project_detail', args=[self.project.id]))
        self.assertContains(response, 'Test Project')

    def test_task_create(self):
        response = self.client.post(reverse('task_create', args=[self.project.id]), {'title': 'New Task'})
        self.assertEqual(response.status_code, 302)

    def test_task_edit(self):
        response = self.client.post(reverse('task_edit', args=[self.task.id]), {'title': 'Updated Task'})
        self.assertEqual(response.status_code, 302)
