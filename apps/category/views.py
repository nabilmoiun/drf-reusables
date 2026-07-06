from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from drf_spectacular.utils import extend_schema

from apps.category.models import Category
from apps.category.serializers import CategoryTreeSerializer


@extend_schema(tags=["category"])
class CategoryViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = CategoryTreeSerializer
    queryset = (
        Category.objects.filter(
            is_active=True,
            parent__isnull=True,
        )
        .order_by("title")
        .only("id", "title", "slug")
    )
    serializer_class_map = {"categories": CategoryTreeSerializer}

    def get_serializer_class(self):
        action = getattr(self, "action")
        return self.serializer_class_map.get(action, self.serializer_class)

    @extend_schema(responses=CategoryTreeSerializer(many=True))
    @action(detail=False, methods=["get"], url_path="categories", pagination_class=None)
    def categories(self, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
