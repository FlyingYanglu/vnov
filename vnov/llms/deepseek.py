from vnov.configs import CONFIG
from vnov.llms.base import BaseLLM
from openai import OpenAI


class Deepseek(BaseLLM):
    max_length = 4096
    def __init__(self, **kwargs):
        self.api_key = CONFIG["Deepseek"]["api_key"]
        self.base_url = CONFIG["Deepseek"]["base_url"]
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.last_output = None
    def generate(self, context, **kwargs):
        system_msg = kwargs.get("system_msg", "You are a helpful assistant")
        context = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": context}
        ]
        print(context)
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=context,
            stream=False
        )
        print(response)
        self.last_output = response
        return response.choices[0].message.content
