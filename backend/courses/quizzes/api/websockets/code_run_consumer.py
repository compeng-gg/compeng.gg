import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from typing import Optional
from rest_framework_simplejwt.tokens import UntypedToken
from asgiref.sync import sync_to_async
import courses.models as db
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser, User
from runner.utils import create_quiz_task
from django.utils import timezone
from pydantic import BaseModel


class TestCaseExecution(BaseModel):
    is_public: bool
    is_passed: bool
    input: Optional[str]
    stdout: Optional[str]
    expected_stdout: Optional[str]
    stderr: Optional[str]


class CodeRunResponse(BaseModel):
    num_passed: int
    num_failed: int

    results: list[TestCaseExecution]


@database_sync_to_async
def get_user_from_token(token):
    try:
        valid_data = UntypedToken(token)
        return User.objects.get(id=valid_data["user_id"])
    except Exception:
        return AnonymousUser()


def do_stuff(quiz_submission, coding_question_id, solution):
    coding_answer = db.CodingAnswer.objects.get(quiz_submission=quiz_submission)

    if coding_answer is None:
        coding_answer = db.CodingAnswer.objects.create(
            quiz_submission=quiz_submission,
            question_id=coding_question_id,
            solution=solution,
            last_updated_at=timezone.now(),
        )
    else:
        coding_answer.solution = solution
        coding_answer.last_updated_at = timezone.now()
        coding_answer.save()

    db.CodingAnswerExecution.objects.create()


@database_sync_to_async
def create_coding_answer_execution(
    solution: str, coding_question_id
) -> db.CodingAnswerExecution:
    coding_answer_execution = db.CodingAnswerExecution.objects.create(
        coding_question_id=coding_question_id,
        solution=solution,
        status=db.CodingAnswerExecution.Status.IN_PROGRESS,
    )
    print(f"Create execution {coding_answer_execution.id}")
    return coding_answer_execution


def get_result(coding_answer_execution: db.CodingAnswerExecution):
    coding_answer_execution.refresh_from_db()

    print(coding_answer_execution.result)

    ### Hide private / hidden test cases of the returned result
    num_passed = 0
    num_failed = 0

    if coding_answer_execution.result is not None:
        tests = []
        for test in coding_answer_execution.result["tests"]:
            kind = test["kind"]

            if kind == "hidden":
                continue

            test.pop("weight")

            if kind == "private":
                test.pop("expected_result", None)
                test.pop("actual_result", None)

            if test["result"] == "OK":
                num_passed += 1
            else:
                num_failed += 1

            tests.append(test)
    else:
        tests = None

    return {
        "status": coding_answer_execution.status,
        "tests": tests,
        "stderr": coding_answer_execution.stderr
        if coding_answer_execution.stderr != ""
        else None,
        "num_passed": num_passed,
        "num_failed": num_failed,
    }


class CodeRunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope["query_string"].decode("utf-8")
        query_params = parse_qs(query_string)

        token = query_params.get("token", [None])[0]

        print(f"Auth token is {token}")

        user = await get_user_from_token(token)

        self.user = user

        print(f"User is {user}")

        # TODO: reject if bad auth token

        kwargs = self.scope["url_route"]["kwargs"]
        print(f"KWARGS are {kwargs}")

        self.quiz_slug = kwargs.get("quiz_slug")
        self.course_slug = kwargs.get("course_slug")
        self.coding_question_id = str(kwargs.get("coding_question_id"))
        print(f"Coding question id is {self.coding_question_id}")

        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        solution = data["solution"]

        coding_answer_execution = await create_coding_answer_execution(
            solution, self.coding_question_id
        )

        await sync_to_async(create_quiz_task)(coding_answer_execution)

        response = await sync_to_async(get_result)(coding_answer_execution)

        print(f"Response is {response}")

        await self.send(text_data=json.dumps(response))
