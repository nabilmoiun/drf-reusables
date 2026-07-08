from drf_spectacular.utils import extend_schema

from rest_framework.views import APIView
from rest_framework.response import Response

from core.services.apps import get_all_model_names
from core.permissions.rbac import required_permission


@extend_schema(tags=["modules"])
class ModuleView(APIView):
    @extend_schema(responses=list[str])
    @required_permission("module.view")
    def get(self, *args, **kwargs):
        return Response(get_all_model_names())
