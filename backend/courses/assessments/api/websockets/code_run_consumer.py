import json
from channels.generic.websocket import AsyncWebsocketConsumer
import time

class CodeRunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        kwargs = self.scope['url_route']['kwargs']

        self.assessment_id = kwargs.get('assessment_id')
        self.coding_question_id = kwargs.get('coding_question_id')
        
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        solution = data['solution']

        # TODO: actually run code

        time.sleep(5)

        response_data = {
            'test_cases_passed': 2,
            'test_cases_failed': 5
        }

        await self.send(text_data=json.dumps(response_data))