from django.urls import path
import courses.quizzes.api.websockets as quizzes_websocket_api

websocket_urlpatterns = [
    path('api/v0/ws/<slug:course_slug>/quiz/<slug:quiz_slug>/run_code/<uuid:coding_question_id>/', quizzes_websocket_api.CodeRunConsumer.as_asgi()),
]
