from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views
from .views_github_webhook import github_webhook

from django.conf import settings
from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='verify'),

    path('auth/discord/', views.auth_discord),
    path('connect/discord/', views.connect_discord),
    # path('disconnect/discord/', views.disconnect_discord),

    path('auth/github/', views.auth_github),
    path('connect/github/', views.connect_github),

    # path('auth/google/', views.auth_google),
    # path('connect/google/', views.connect_google),

    path('auth/laforge/', views.auth_laforge),
    path('connect/laforge/', views.connect_laforge),

    path('users/self/', views.self),

    path('dashboard/', views.dashboard),
    path('settings/', views.settings),

    path('tasks/', views.tasks),

    path('courses/offerings/', views.offerings),
    path('courses/<slug:slug>/', views.course),
    path('courses/<slug:course_slug>/staff/', views.staff),
    path('courses/<slug:course_slug>/staff/<slug:assignment_slug>/', views.staff_assignment),
    path('courses/<slug:course_slug>/staff/<slug:assignment_slug>/accommodation/', views.staff_assignment_accommodation),
    path('courses/<slug:course_slug>/staff/<slug:assignment_slug>/private-release/', views.staff_assignment_private_release),
    path('courses/<slug:course_slug>/staff/<slug:assignment_slug>/<str:student_username>/', views.staff_assignment_student),
    path('courses/<slug:slug>/students/', views.students),
    path('courses/<slug:slug>/students/commits/', views.students_commits),

    path('github/webhook/', github_webhook),

    path('users/', views.UserViewSet.as_view({'get': 'list'})),
]

if settings.BUILTIN_FRONTEND:
    urlpatterns += [
        path('', views.api_root),
    ]
