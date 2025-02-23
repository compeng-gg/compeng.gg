import pytest
from channels.testing import WebsocketCommunicator
from courses.quizzes.api.websockets import CodeRunConsumer
from channels.routing import URLRouter
from django.urls import path


@pytest.mark.asyncio
async def test_code_run_consumer_happy_path():
    # Define test parameters
    test_quiz_slug = "123e4567-e89b-12d3-a456-426614174000"
    test_coding_question_id = "987e6543-e21b-45c6-b123-426614174000"

    # Define WebSocket application for testing
    application = URLRouter(
        [
            path(
                "api/v0/ws/quizzes/<uuid:quiz_slug>/run_code/<uuid:coding_question_id>/",
                CodeRunConsumer.as_asgi(),
            ),
        ]
    )

    # Define the WebSocket URL with the parameters
    url = f"api/v0/ws/quizzes/{test_quiz_slug}/run_code/{test_coding_question_id}/"

    # Create a WebSocket communicator for testing
    communicator = WebsocketCommunicator(application, url)

    try:
        # Connect to the WebSocket
        connected, _ = await communicator.connect()
        assert connected

        # Send a test message
        solution = "print('Hello World!')"

        test_message = {"solution": solution}
        await communicator.send_json_to(test_message)

        # Receive the response
        response = await communicator.receive_json_from()

        assert response["test_cases_passed"] == 2
        assert response["test_cases_failed"] == 5

    finally:
        # Ensure the WebSocket is closed to avoid dangling tasks
        await communicator.disconnect()
