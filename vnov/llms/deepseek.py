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
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=context,
            stream=False
        )
        self.last_output = response
        return response.choices[0].message.content
    
    def token_length(self, context):
        token_count = 0
        
        for char in context:
            # Check if the character is Chinese (Unicode range: 0x4e00-0x9fff)
            if '\u4e00' <= char <= '\u9fff':
                token_count += 0.6
            # Check if the character is English (uppercase or lowercase letters a-z or A-Z)
            elif 'a' <= char <= 'z' or 'A' <= char <= 'Z':
                token_count += 0.3
            # If it's another character (e.g., whitespace or punctuation), treat it as an English character
            else:
                token_count += 0.3

        # Round the token count to the nearest integer
        return round(token_count)
