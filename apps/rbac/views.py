from drf_spectacular.utils import extend_schema

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, viewsets, status

from apps.rbac.models import Role
from apps.rbac.serializers import (
    RoleListSerializer,
    RoleViewSerializer,
    RoleCreateSerializer,
    RoleUpdateSerializer,
    PermissionViewSerializer,
)
from core.permissions.rbac import required_permission


@extend_schema(tags=["roles & permissions"])
class RoleViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    serializer_class = RoleListSerializer
    queryset = Role.objects.order_by("name")
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post", "get", "put", "delete"]
    serializer_class_map = {
        "list": RoleListSerializer,
        "retrieve": RoleViewSerializer,
        "create": RoleCreateSerializer,
        "update": RoleUpdateSerializer,
        "permissions": PermissionViewSerializer,
    }
    queryset_map = {
        "list": Role.objects.only("id", "name", "slug"),
        "destroy": Role.objects.only("id", "name", "slug"),
        "update": Role.objects.only("id", "name", "slug", "is_active"),
        "create": Role.objects.only("id", "name", "slug", "description", "is_active"),
        "retrieve": Role.objects.prefetch_related("permissions").only(
            "id", "name", "slug"
        ),
        "permissions": Role.objects.prefetch_related("permissions").only(
            "id", "name", "slug"
        ),
    }

    def get_serializer_class(self):
        action = getattr(self, "action")
        return self.serializer_class_map.get(action, self.serializer_class)

    def get_queryset(self):
        action = getattr(self, "action")
        queryset = self.queryset_map.get(action, self.queryset)

        if self.request.user.is_superuser:
            return queryset

        if action in ("list", "retrieve", "permissions"):
            return queryset.filter(user=self.request.user)
        
        return queryset
    
    @required_permission("role.create")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @required_permission("role.update")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @required_permission("role.delete")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(responses=PermissionViewSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="permissions", pagination_class=None)
    @required_permission("role.view")
    def permissions(self, *args, **kwargs):
        role = self.get_object()
        queryset = role.permissions.order_by("name")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
