import pathlib
import subprocess

from compeng_gg.django.github.models import Push
from courses.models import CodingAnswerExecution
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json
import os
from time import time

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("coding_answer_execution_id", type=int)

    def handle(self, *args, **options):
        coding_answer_execution_id = options["coding_answer_execution_id"]
        try:
            coding_answer_execution = CodingAnswerExecution.objects.get(id=coding_answer_execution_id)
        except Push.DoesNotExist:
            raise CommandError(f"Coding answer execution {coding_answer_execution_id} does not exist")
        
        solution = coding_answer_execution.solution
        print(f'Solution is {solution}')

        repository = coding_answer_execution.coding_answer.question.quiz.repository

        # TODO: dont use this path. We're doing this to mock is locally for now
        curr_time = str(int(time()))
        tmp_dir = pathlib.Path(f"/tmp/{curr_time}--{coding_answer_execution_id}")

        os.mkdir(tmp_dir)

        repo_dir = tmp_dir / repository.name

        subprocess.run(
            ["git", "clone", "--depth", "1", f"https://github.com/{repository.full_name}"], 
            cwd=tmp_dir, 
            check=True
        )

        file_path_to_replace = coding_answer_execution.coding_answer.question.file_to_replace
        grading_file_directory = coding_answer_execution.coding_answer.question.grading_file_directory

        file_path = f"{repo_dir}/{file_path_to_replace}"

        with open(file_path, "w") as file:
            file.write(solution)


        # TODO: launch this in the quiz container

        grading_file_path = repo_dir / grading_file_directory / "grade.py"

        res2 = subprocess.run(['python', grading_file_path], capture_output=True, text=True)

        actual_stdout = res2.stdout

        print(f"Actual stdout is {actual_stdout}")
        print(f"Stderr is {res2.stderr}")

        try:
            json_result = json.loads(actual_stdout)
            coding_answer_execution.result = json_result
            coding_answer_execution.status = CodingAnswerExecution.Status.SUCCESS
        except Exception:
            coding_answer_execution.status = CodingAnswerExecution.Status.FAILURE

        coding_answer_execution.stderr = res2.stderr
        coding_answer_execution.save()

        print("Saved!!")