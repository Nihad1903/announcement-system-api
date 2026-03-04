"""
URL configuration for departments app.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet

app_name = 'departments'

router = DefaultRouter()
router.register('', DepartmentViewSet, basename='department')

urlpatterns = [
    path('', include(router.urls)),
]
