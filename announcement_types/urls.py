"""
URL configuration for announcement_types app.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AnnouncementTypeViewSet

app_name = 'announcement_types'

router = DefaultRouter()
router.register('', AnnouncementTypeViewSet, basename='announcement-type')

urlpatterns = [
    path('', include(router.urls)),
]
