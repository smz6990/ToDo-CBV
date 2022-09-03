from locust import HttpUser, task
import random
class RandomTestUser(HttpUser):

    def on_start(self):
        response = self.client.post(
            url='/accounts/api/v1/jwt/create/',
            data={
                "email": "admin@admin.com",
                "password": "a/1234567"
                }
            ).json()
        self.client.headers = {"Authorization": f"Bearer {response.get('access', None)}"}
    
    # def on_stop(self):
    #     self.client.post("/login", json={"username":"foo", "password":"bar"})
    
    @task(3)
    def index_page(self):
        self.client.get('/api/v1/task/')
    
    @task(1)
    def create_task(self):
        data = {
            "author": {
                "email": "admin@admin.com"
            },
            "content": "content from locust",
            "is_done": random.choice([True, False])
            }
        self.client.post('/api/v1/task/',data=data)
            
    # @task(3)
    # def task_done(self):
    #     for item_id in range(10):
    #         self.client.get(f"/item?id={item_id}", name="/item")
    #         time.sleep(1)
            
            
    # @task(3)
    # def delete_task(self):
    #     for item_id in range(10):
    #         self.client.get(f"/item?id={item_id}", name="/item")
    #         time.sleep(1)