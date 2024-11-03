from vnov.role import Role
from vnov.story.prompts import (
    ARTIST_ROLE,
    PROMPT_OPTIMIZATION
)


class Artist(Role):
    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.context_token_length = self.model.token_length(self.format_context(""))
        self.role = "photographer"

    def format_context(self, content, **kwargs):
        messages = [
            {"role": "system", "content": ARTIST_ROLE},
            {"role": "user", "content": PROMPT_OPTIMIZATION.format(content=content)},
        ]
        return messages

    def take_action(self, **kwargs):
        pass

    def optimize_prompt(self, content):
        context = self.format_context(content)
        token_length = self.model.token_length(context)
        if token_length < self.max_length:
            outputs = self.model(context, max_length=self.max_length)
        else:
            raise ValueError(f"Content too long: {token_length}")
        return outputs