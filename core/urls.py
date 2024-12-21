from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationAPIView, UserLoginAPIView, UserLogoutAPIView, OrganizationViewSet, ClusterViewSet, DeploymentViewSet

router = DefaultRouter()
router.register('organizations', OrganizationViewSet)
router.register('clusters', ClusterViewSet)
router.register('deployments', DeploymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', UserRegistrationAPIView.as_view(), name='register'),
    path('auth/login/', UserLoginAPIView.as_view(), name='login'),
    path('auth/logout/', UserLogoutAPIView.as_view(), name='logout'),
]
