from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.authentication.views import AuthViewSet

router = DefaultRouter()

router.register("auth", AuthViewSet, basename="auth")


urlpatterns = [path("", include(router.urls))]
