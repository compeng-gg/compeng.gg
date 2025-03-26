from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views
from .views_github_webhook import github_webhook
import courses.teams.api as teams_api
import courses.quizzes.api as quizzes_api

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

    path('navbar/', views.navbar),
    path('dashboard/', views.dashboard),
    path('settings/', views.settings),

    path('tasks/', views.tasks),

    path('courses/offerings/', views.offerings),
    
    path('courses/<slug:slug>/', views.course),
    
    
    
    path('teams/join/request/', teams_api.request_to_join_team),
    path('teams/join/manage/', teams_api.manage_join_team_request),
    path('teams/delete/', teams_api.delete_team),
    path('teams/leave/', teams_api.leave_team),
    path('teams/get/<slug:course_slug>/<slug:offering_slug>', teams_api.teams),
    path('teams/create/', teams_api.create_team),
    path('teams/settings/get/<slug:course_slug>/<slug:offering_slug>', teams_api.get_team_settings_for_offering),
    path('teams/settings/create/<slug:course_slug>/<slug:offering_slug>', teams_api.create_team_settings_for_offering),
    path('teams/settings/update/<slug:course_slug>/<slug:offering_slug>', teams_api.update_team_settings_for_offering),
    path('teams/admin/create/', teams_api.create_team_with_leader),
    path('teams/admin/add/', teams_api.add_member_to_team),
    path('teams/admin/remove/', teams_api.remove_member_from_team),
    path('teams/admin/delete/', teams_api.delete_team_as_admin),
    path('teams/user/status/<slug:slug>/', teams_api.get_user_team_status),
    
    path('offering/role/<slug:slug>/', teams_api.get_user_role),
    path('offering/students/<slug:slug>/', teams_api.get_enrolled_students),
    

    path('quizzes/list/all/', quizzes_api.list_all),
    path('quizzes/list/<slug:course_slug>/', quizzes_api.list_for_course),
    path('<slug:course_slug>/quiz/<slug:quiz_slug>/', quizzes_api.get_questions),
    path('<slug:course_slug>/quiz/<slug:quiz_slug>/answer/checkbox/<uuid:checkbox_question_id>/', quizzes_api.submit_checkbox_answer),
    path('<slug:course_slug>/quiz/<slug:quiz_slug>/answer/multiple_choice/<uuid:multiple_choice_question_id>/', quizzes_api.submit_multiple_choice_answer),
    path('<slug:course_slug>/quiz/<slug:quiz_slug>/answer/written_response/<uuid:written_response_question_id>/', quizzes_api.submit_written_response_answer),
    path('<slug:course_slug>/quiz/<slug:quiz_slug>/answer/coding/<uuid:coding_question_id>/', quizzes_api.submit_coding_answer),
    path('<slug:course_slug>/quiz/<slug:quiz_slug>/complete/', quizzes_api.complete_quiz),
    path('quizzes/admin/<slug:course_slug>/create/', quizzes_api.create_quiz),
    path('quizzes/<slug:course_slug>/<slug:quiz_slug>/image/<uuid:question_image_id>/', quizzes_api.get_quiz_question_image),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/multiple_choice/create/', quizzes_api.create_multiple_choice_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/checkbox/create/', quizzes_api.create_checkbox_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/coding/create/', quizzes_api.create_coding_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/written_response/create/', quizzes_api.create_written_response_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/checkbox/<uuid:checkbox_question_id>/edit/', quizzes_api.edit_checkbox_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/coding/<uuid:coding_question_id>/edit/', quizzes_api.edit_coding_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/written_response/<uuid:written_response_question_id>/edit/', quizzes_api.edit_written_response_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/multiple_choice/<uuid:multiple_choice_question_id>/edit/', quizzes_api.edit_multiple_choice_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/checkbox/<uuid:checkbox_question_id>/delete/', quizzes_api.delete_checkbox_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/coding/<uuid:coding_question_id>/delete/', quizzes_api.delete_coding_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/written_response/<uuid:written_response_question_id>/delete/', quizzes_api.delete_written_response_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/multiple_choice/<uuid:multiple_choice_question_id>/delete/', quizzes_api.delete_multiple_choice_question),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/delete/', quizzes_api.delete_quiz),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/edit/', quizzes_api.edit_quiz),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/release-now/', quizzes_api.release_quiz_now),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/', quizzes_api.get_quiz),
    path('quizzes/<slug:course_slug>/<slug:quiz_slug>/info/', quizzes_api.get_quiz_info),

    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/accommodation/create/', quizzes_api.create_quiz_accommodation),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/accommodation/delete/', quizzes_api.delete_quiz_accommodation),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/accommodations/', quizzes_api.list_quiz_accommodations),
    
    path('quizzes/admin/<slug:course_slug>/', quizzes_api.admin_list_quizzes_for_course),
    path('quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/submissions/', quizzes_api.get_quiz_submissions),
    path("quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/submissions/<int:student_id>/", quizzes_api.get_student_quiz_submission_staff),
    path("quizzes/admin/<slug:quiz_slug>/submissions/<int:student_id>/update-question/", quizzes_api.update_submission_question),
    path("quizzes/admin/<slug:quiz_slug>/submissions/<int:student_id>/submit-grade/", quizzes_api.compute_total_grade),
    
    path("quizzes/<slug:course_slug>/<slug:quiz_slug>/submission/", quizzes_api.get_student_quiz_submission),


    path("quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/images/add/", quizzes_api.create_question_image),
    path("quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/images/delete/<uuid:image_id>/", quizzes_api.delete_question_image),
    path("quizzes/admin/<slug:course_slug>/<slug:quiz_slug>/images/edit/<uuid:image_id>/", quizzes_api.update_question_image),
    path('github/webhook/', github_webhook),

    path('users/', views.UserViewSet.as_view({'get': 'list'})),
]

if settings.BUILTIN_FRONTEND:
    urlpatterns += [
        path('', views.api_root),
    ]
