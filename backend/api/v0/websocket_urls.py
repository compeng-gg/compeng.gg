from django.urls import path
import courses.assessments.api.websockets as assessments_websocket_api

websocket_urlpatterns = [
    path('api/ws/v0/assessments/<uuid:assessment_id>/run_code/<uuid:coding_question_id>/', assessments_websocket_api.CodeRunConsumer.as_asgi()),
]
