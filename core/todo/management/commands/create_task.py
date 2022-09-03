from django.core.management.base import BaseCommand
from faker import Faker
from random import choice

from todo.models import Task
from accounts.models import User


class Command(BaseCommand):
    help = "Creating task for todo list (default: 5)"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.fake = Faker()

    def add_arguments(self, parser):

        parser.add_argument(
            "-n", "--number", type=int, help="number of tasks to create"
        )

    def handle(self, *args, **options):
        task_number = options["number"] or 5

        user = User.objects.create_user(
            email=self.fake.email(), password="a/1234567", is_verified=True
        )

        for _ in range(task_number):
            task = Task.objects.create(
                author=user,
                content=self.fake.sentence(),
                is_done=choice([True, False]),
            )
            task.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully create {task_number} tasks for user: {user}"
            )
        )
