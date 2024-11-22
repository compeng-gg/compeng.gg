from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views
from .views_github_webhook import github_webhook
import courses.teams.api as teams_api
import courses.assessments.api as assessments_api

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
    path('teams/join/request/', teams_api.request_to_join_team),
    path('teams/join/manage/', teams_api.manage_join_team_request),
    path('teams/delete/', teams_api.delete_team),
    path('teams/leave/', teams_api.leave_team),
    path('teams/get/<slug:slug>', teams_api.teams),
    path('teams/create/', teams_api.create_team),
    path('teams/settings/get/', teams_api.get_team_settings_for_offering),
    path('teams/settings/create/', teams_api.create_team_settings_for_offering),
    path('teams/settings/update/', teams_api.update_team_settings_for_offering),
    path('teams/admin/create/', teams_api.create_team_with_leader),
    path('teams/admin/add/', teams_api.add_member_to_team),
    path('teams/admin/remove/', teams_api.remove_member_from_team),
    path('teams/admin/delete/', teams_api.delete_team_as_admin),
    

    path('assessments/<uuid:assessment_id>/', assessments_api.get_assessment),
    path('assessments/<uuid:assessment_id>/answer/checkbox/<uuid:checkbox_question_id>/', assessments_api.submit_checkbox_answer),
    path('assessments/<uuid:assessment_id>/answer/multiple_choice/<uuid:multiple_choice_question_id>/', assessments_api.submit_multiple_choice_answer),
    path('assessments/<uuid:assessment_id>/answer/written_response/<uuid:written_response_question_id>/', assessments_api.submit_written_response_answer),
    path('assessments/<uuid:assessment_id>/answer/coding/<uuid:coding_question_id>/', assessments_api.submit_coding_answer),
    path('assessments/<uuid:assessment_id>/complete/', assessments_api.complete_assessment),

    path('github/webhook/', github_webhook),

    path('users/', views.UserViewSet.as_view({'get': 'list'})),
]

if settings.BUILTIN_FRONTEND:
    urlpatterns += [
        path('', views.api_root),
    ]
