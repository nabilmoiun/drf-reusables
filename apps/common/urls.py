from django.urls import path, include

from apps.common.views import ModuleView

urlpatterns = [
    path("modules/", ModuleView.as_view(), name="modules-list")
]