from openai import OpenAI
from vnov.llms.base import BaseLLM
from vnov.utils import load_config
from vnov.configs import CONFIG

class GPT(BaseLLM):
    def __init__(self, **kwargs):
        self.api_key = CONFIG["openai"]["api_key"]
        self.engine = kwargs.get("engine", "text-davinci-003")
        self.openai = OpenAI(self.api_key)
