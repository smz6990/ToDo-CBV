from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .paginations import CustomPagination
from todo.models import Task
from .serializers import TaskSerializer
from .permissions import IsVerified


class TaskModelViewSet(viewsets.ModelViewSet):
    """
    A simple ModelViewSet to perform CRUD functions on todo Task.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsVerified]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_done"]
    search_fields = ["content"]
    ordering_fields = ["created_date"]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        This view should return a list of all the tasks
        for the currently authenticated user.
        """
        user = self.request.user
        return Task.objects.filter(author=user)
