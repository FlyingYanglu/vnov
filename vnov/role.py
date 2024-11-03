from abc import abstractmethod
from vnov.llms.base import BaseLLM
ACTION = """\
{content}
"""
ROLE = "You are a helpful assistant"

class Role:
    role = "role"
    model : BaseLLM = None
    max_length : int = 7000
    context_token_length : int = 0

    def __init__(self, model, **kwargs):
        self.model = model
    
    def format_context(self, content, **kwargs):
        messages = [
            {"role": "system", "content": ROLE},
            {"role": "user", "content": ACTION.format(content=content)},
        ]
        return messages

    @abstractmethod
    def take_action(self, **kwargs):
        pass
    
    