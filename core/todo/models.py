from django.db import models
from django.contrib.auth import get_user_model

# getting the user model object
User = get_user_model()


class Task(models.Model):
    """
    this is a class for tasks in our todo app
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return "{} - {}".format(self.author, self.content)

    def get_snippet(self):
        return self.content[:10]
