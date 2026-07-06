from rest_framework import serializers

from apps.category.models import Category
from core.tree.serializers import TreeSerializer


class CategoryTreeSerializer(TreeSerializer):
    class Meta:
        model = Category
        fields = ("id", "title", "slug", "children")


