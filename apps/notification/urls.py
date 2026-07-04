from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.notification.views import NotificationViewSet, FCMTokenViewSet

router = DefaultRouter()

router.register("fcm/tokens", FCMTokenViewSet, basename="fcm-tokens")
router.register("notifications", NotificationViewSet, basename="notifications")


urlpatterns = [path("", include(router.urls))]
