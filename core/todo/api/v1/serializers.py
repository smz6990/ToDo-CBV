from todo.models import Task
from accounts.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "id"]


class TaskSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    snippet = serializers.ReadOnlyField(source="get_snippet")
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "author",
            "id",
            "content",
            "snippet",
            "url",
            "is_done",
            "created_date",
            "updated_date",
        ]

    def create(self, validated_data):
        """
        create a new Task without getting author field by user
        """
        validated_data["author"] = self.context.get("request").user
        return super().create(validated_data)

    def get_url(self, obj):
        """
        Getting absolute url for task
        """
        request = self.context.get("request")
        abs_url = obj.pk
        return request.build_absolute_uri(abs_url)

    def to_representation(self, instance):
        """
        Modifying the representation of serializer
        """
        rep = super().to_representation(instance)
        request = self.context.get("request")
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("snippet", None)
            rep.pop("url", None)
        else:
            rep.pop("content", None)
        return rep
