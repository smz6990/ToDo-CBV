import pytest
from django.urls import reverse
from rest_framework .test import APIClient
from todo.models import Task
from accounts.models import User


@pytest.fixture
def api_client():
    return  APIClient

@pytest.mark.django_db
class TestTodoApi():
    
    endpoint = reverse('todo:api-v1:task-list')
    
    def create_user_obj(self, num=1):
        return User.objects.create_user(email=f'test{num}@test.com', password='a/1234567', is_verified=True)
    
    def create_author_and_task_obj(self):
        author = self.create_user_obj()
        task = Task.objects.create(author=author, content='content')
        return author, task
    
    def test_api_todo_get_task_list_response_200(self, api_client):
        client = api_client()
        user = self.create_user_obj()
        client.force_authenticate(user=user)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        
    def test_api_todo_get_task_list_response_401(self, api_client):
        client = api_client()
        response = client.get(self.endpoint)
        assert response.status_code == 401
        
    def test_api_todo_post_task_list_response_201(self, api_client):
        client = api_client()
        author, task = self.create_author_and_task_obj()
        client.force_authenticate(user=author)
        data = {"author":author.email, "content":task.content, "is_done":task.is_done}
        response = client.post(path=self.endpoint, data=data)
        assert response.status_code == 201
        
    def test_api_todo_get_task_retrieve_response_200(self, api_client):
        client = api_client()
        author, task = self.create_author_and_task_obj()
        client.force_authenticate(user=author)
        task_url = f'{self.endpoint}{task.id}/'
        response = client.get(task_url)
        assert response.status_code == 200
        
    def test_api_todo_get_task_retrieve_response_404(self, api_client):
        client = api_client()
        author, task = self.create_author_and_task_obj()
        user = self.create_user_obj(2)
        client.force_authenticate(user=user)
        task_url = f'{self.endpoint}{task.id}/'
        response = client.get(task_url)
        assert response.status_code == 404

    def test_api_todo_put_task_response_200(self, api_client):
        client = api_client()
        author, task = self.create_author_and_task_obj()
        client.force_authenticate(user=author)
        task_url = f'{self.endpoint}{task.id}/'
        data = {"author":author.email, "content":"put content", "is_done":True}
        response = client.put(path=task_url, data=data)
        assert response.status_code == 200
    
    def test_api_todo_patch_task_response_200(self, api_client):
        client = api_client()
        author, task = self.create_author_and_task_obj()
        client.force_authenticate(user=author)
        task_url = f'{self.endpoint}{task.id}/'
        data = {"author":author.email, "content":"patch content"}
        response = client.patch(path=task_url, data=data)
        assert response.status_code == 200

    def test_api_todo_delete_task_response_204(self, api_client):
        client = api_client()
        author, task = self.create_author_and_task_obj()
        client.force_authenticate(user=author)
        task_url = f'{self.endpoint}{task.id}/'
        response = client.delete(path=task_url)
        assert response.status_code == 204
