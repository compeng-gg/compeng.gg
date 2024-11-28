import json
from channels.generic.websocket import AsyncWebsocketConsumer
import time
import sys, io

def run_python_code_and_get_stdout(code: str):
    output_buffer = io.StringIO()

    original_stdout = sys.stdout
    sys.stdout = output_buffer

    try:
        exec(code)
    finally:
        # Reset stdout
        sys.stdout = original_stdout

    # Get the output from the buffer
    captured_output = output_buffer.getvalue()
    output_buffer.close()

    # Print the captured output
    print("Captured Output:")
    print(captured_output)

    return captured_output


def run__add_numbers__function(solution: str, num1: int, num2: int):
    code = f"""
{solution}
value = add_numbers({num1}, {num2})
print(value)
"""
    captured_output = run_python_code_and_get_stdout(code)
    print(f"Captured output is {captured_output}")
    return captured_output.strip()


ADD_NUMBERS__TEST_CASES = [
    [[1, 2], 3],
    [[5, 5], 10]
]

ADD_NUMBERS__QUESTION_ID = "215a939a-1e86-415c-acb2-0bbffcf35e71"

def run__hello_world__script(solution: str):
    captured_output = run_python_code_and_get_stdout(solution)
    print(f"Captured output is {captured_output}")
    return captured_output.strip()

HELLO_WORLD_TEST_CASES = [
    [[], "Hello World!"]
]

HELLO_WORLD__QUESTION_ID = "fb597156-6b5c-4721-b635-b1625624e568"

def run_python_test_cases(test_cases, runner_function, solution):
    num_test_cases_passed = 0
    num_test_cases_failed = 0

    for test_case, expected_value in test_cases:
        result = runner_function(solution, *test_case)

        print(f"Got {result}, expected {expected_value}")
        if result == str(expected_value):
            num_test_cases_passed += 1
        else:
            num_test_cases_failed += 1

    return num_test_cases_passed, num_test_cases_failed

class CodeRunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kwargs = self.scope['url_route']['kwargs']

        self.assessment_slug = kwargs.get('assessment_slug')
        self.coding_question_id = str(kwargs.get('coding_question_id'))
        print(f"Coding question id is {self.coding_question_id}")
        
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        solution = data['solution']

        if self.coding_question_id == ADD_NUMBERS__QUESTION_ID:
            num_test_cases_passed, num_test_cases_failed = run_python_test_cases(ADD_NUMBERS__TEST_CASES, run__add_numbers__function, solution)
        elif self.coding_question_id == HELLO_WORLD__QUESTION_ID:
            num_test_cases_passed, num_test_cases_failed = run_python_test_cases(HELLO_WORLD_TEST_CASES, run__hello_world__script, solution)
        else:
            num_test_cases_passed, num_test_cases_failed = 0, 2

        print(f"Passed {num_test_cases_passed}, failed {num_test_cases_failed}")

        response_data = {
            'test_cases_passed': num_test_cases_passed,
            'test_cases_failed': num_test_cases_failed
        }

        await self.send(text_data=json.dumps(response_data))
