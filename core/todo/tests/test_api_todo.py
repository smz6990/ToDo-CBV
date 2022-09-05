import pytest
from django.urls import reverse
from rest_framework .test import APIClient
from todo.models import Task
from accounts.models import User


@pytest.fixture
def api_client():
    client = APIClient()
    return  client

@pytest.fixture
def create_user_obj():
    user = User.objects.create_user(email='test@test.test', password='a/1234567', is_verified=True)
    return user

@pytest.fixture
def create_author_and_task_obj(create_user_obj):
    author = create_user_obj
    task = Task.objects.create(author=author, content='test content')
    return author, task

@pytest.mark.django_db
class TestTodoApi:
    
    endpoint = reverse('todo:api-v1:task-list')
    
    def test_api_todo_get_task_list_response_200(self, api_client, create_user_obj):
        user = create_user_obj
        api_client.force_authenticate(user=user)
        response = api_client.get(self.endpoint)
        assert response.status_code == 200
        
    def test_api_todo_get_task_list_response_401_unauthorize_user(self, api_client):
        #unauthorize user
        response = api_client.get(self.endpoint)
        assert response.status_code == 401
        
    def test_api_todo_post_task_list_response_201(self, api_client, create_author_and_task_obj):
        author, task = create_author_and_task_obj
        api_client.force_authenticate(user=author)
        data = {"author":author.email, "content":task.content, "is_done":task.is_done}
        response = api_client.post(path=self.endpoint, data=data)
        assert response.status_code == 201
        
    def test_api_todo_get_task_retrieve_response_200(self, api_client, create_author_and_task_obj):
        author, task = create_author_and_task_obj
        api_client.force_authenticate(user=author)
        task_url = f'{self.endpoint}{task.id}/'
        response = api_client.get(task_url)
        assert response.status_code == 200
        
    def test_api_todo_get_task_retrieve_response_404(self, api_client, create_user_obj, create_author_and_task_obj):
        author, task = create_author_and_task_obj
        user = User.objects.create_user(email='test1@test.test', password='a/1234567', is_verified=True)
        api_client.force_authenticate(user=user)
        task_url = f'{self.endpoint}{task.id}/'
        response = api_client.get(task_url)
        assert response.status_code == 404

    def test_api_todo_put_task_response_200(self, api_client, create_author_and_task_obj):
        author, task = create_author_and_task_obj
        api_client.force_authenticate(user=author)
        task_url = f'{self.endpoint}{task.id}/'
        data = {"author":author.email, "content":"put content", "is_done":True}
        response = api_client.put(path=task_url, data=data)
        assert response.status_code == 200
    
    def test_api_todo_patch_task_response_200(self, api_client, create_author_and_task_obj):
        author, task = create_author_and_task_obj
        api_client.force_authenticate(user=author)
        task_url = f'{self.endpoint}{task.id}/'
        data = {"author":author.email, "content":"patch content"}
        response = api_client.patch(path=task_url, data=data)
        assert response.status_code == 200

    def test_api_todo_delete_task_response_204(self, api_client, create_author_and_task_obj):
        author, task = create_author_and_task_obj
        api_client.force_authenticate(user=author)
        task_url = f'{self.endpoint}{task.id}/'
        response = api_client.delete(path=task_url)
        assert response.status_code == 204
