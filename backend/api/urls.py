from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('jwt/obtain-pair/', TokenObtainPairView.as_view(), name='jwt_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='jwt_verify'),
    path('auth/session/', views.session),
]
