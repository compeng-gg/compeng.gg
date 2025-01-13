import pathlib
import subprocess

from compeng_gg.django.github.models import Push
from courses.models import CodingAnswerExecution, CodingQuestionTestCaseExecution
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import shutil

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

        repository = coding_answer_execution.coding_question.repository

        tmp_dir = pathlib.Path("/tmp")

        repo_dir = tmp_dir / repository.name

        try:
            shutil.rmtree(repo_dir)
            print("Directory deleted successfully!")
        except FileNotFoundError:
            print("Directory not found.")

        subprocess.run(["git", "clone", "--depth", "1", f"git@github.com:{repository.full_name}"], cwd=tmp_dir)

        # TODO: uncomment this / figure out how to test this
        registry_url = "localhost:6000" if settings.RUN_LOCALLY else "gitea.eyl.io/jon"

        tag = f"{registry_url}/{repository.name}:latest"

        print(f"Pushing tag {tag}")
        #subprocess.run(["podman", "build", "-t", tag, "."], cwd=repo_dir)
        #subprocess.run(["podman", "push", "--tls-verify=false", tag])

        print(f"Repo dir is {repo_dir}")
        ### Replace a specifc file in the repo with the solution

        file_path_to_replace = "add.py"

        file_path = f"{repo_dir}/{file_path_to_replace}"

        with open(file_path, "w") as file:
            file.write(solution)

        print("Replaced content!")

        ## TODO: we also need to remove the content of EVERY file that is marked as an "answer" file.
        # If we don't do this, students will be able to extract the correct solutions via std(out/err). Which is bad
        # This does force instructors not to depend answer files on other answer files. Which should be true, but should be validated?

        # ALTERNATIVELY: every question is it's own repo?? Maybe this makes more sense
        # Currently doing this.

        subprocess.run(["podman", "build", "-t", "testcontainer", "."], cwd=repo_dir)

        test_cases = coding_answer_execution.coding_question.test_cases.all()
        print(len(test_cases))

        for test_case in test_cases:
            print(f"Running testcase command {test_case.command}")
            res = subprocess.run(["podman", "run", "--rm", "testcontainer", "sh", "-c", test_case.command], capture_output=True, text=True)

            actual_stdout = res.stdout.strip()
            print(type(actual_stdout))
            print(type(test_case.expected_stdout))
            print(f"stdout: {res.stdout.strip()}")
            print(f"stderr: {res.stderr.strip()}")

            if actual_stdout!= test_case.expected_stdout:
                print(f"Wrong! Expected {test_case.expected_stdout}")
            else:
                print("Right")

            CodingQuestionTestCaseExecution.objects.create(
                stdout=actual_stdout,
                stderr=res.stderr,
                test_case=test_case,
                coding_answer_execution=coding_answer_execution,
            )
