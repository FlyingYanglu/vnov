from vnov.role import Role
from vnov.story.prompts import (
    PHOTOGRAPHER_ROLE,
    SHOT_TAKING
)
import json
import re

class Photographer(Role):
    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.context_token_length = self.model.token_length(self.format_context(""))
        self.role = "photographer"

    def format_context(self, content, **kwargs):
        messages = [
            {"role": "system", "content": PHOTOGRAPHER_ROLE},
            {"role": "user", "content": SHOT_TAKING.format(content=content)},
        ]
        return messages
    
    def take_action(self, **kwargs):
        pass


    def take_shots(self, content):
        context = self.format_context(content)
        token_length = self.model.token_length(context)
        if token_length < self.max_length:
            outputs = self.model(context, max_length=self.max_length)
        else:
            raise ValueError(f"Content too long: {token_length}")
        return self._parse_json(outputs)
    

    def _parse_json(self, outputs):
        # Looking for ```json\n{...}```
        pattern = re.compile(r"```json\n(.*?)```", re.DOTALL)
        match = pattern.search(outputs)
        if match:
            outputs = match.group(1)
        else:
            raise ValueError(f"Could not find JSON in {outputs}")
        return json.loads(outputs)

    def save_shots(self, shots, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(shots, f, indent=4, ensure_ascii=False)

    