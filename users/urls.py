from django.urls import path, include
from rest_framework import routers
from .views import MyTokenObtainPairView, RegisterView, ActivateAccountView, UserViewSet
from rest_framework_simplejwt.views import (
    TokenRefreshView, )

router = routers.DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/',
         MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('auth/login/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name="sign_up"),
    path('auth/activate/<str:token>/',
         ActivateAccountView.as_view(),
         name='activate_account'),
]