from django.urls import path
import courses.exams.api.websockets as exams_websocket_api

websocket_urlpatterns = [
    path('api/ws/v0/<slug:course_slug>/exam/<slug:exam_slug>/run_code/<uuid:coding_question_id>/', exams_websocket_api.CodeRunConsumer.as_asgi()),
]
