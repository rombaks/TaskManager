from rest_framework import serializers
from .models import tags, user, task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user.User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_of_birth",
            "phone",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = tags.Tag
        fields = ("title",)


class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = task.Task
        fields = (
            "id",
            "title",
            "description",
            "author",
            "assignee",
            "due_at",
            "created_at",
            "updated_at",
            "state",
            "priority",
            "tag",
        )
