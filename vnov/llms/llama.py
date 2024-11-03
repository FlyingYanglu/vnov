from vnov.llms.base import BaseLLM
import transformers
import torch
from typing import List, Dict



class Llama(BaseLLM):
    max_length = 1000
    def __init__(self, **kwargs):
        model_id = kwargs.get("model_id", "meta-llama/Meta-Llama-3.1-8B-Instruct")
        self.model_id = model_id
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=model_id,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )
        self.terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]


    def token_length(self, context):
        if isinstance(context, str) or (isinstance(context, list) and all(isinstance(c, str) for c in context)):
            return len(self.pipeline.tokenizer(context)["input_ids"])
        elif isinstance(context, list) and all(isinstance(c, dict) for c in context):
            inputs = self.pipeline.tokenizer.apply_chat_template(context)
            return len(inputs)
        else:
            raise ValueError(f"{context} should be a string or a dictionary")

    def generate(self, context, **kwargs):
        max_length = kwargs.get("max_length", self.max_length)
        temperature = kwargs.get("temperature", 0.8)
        return self.pipeline(context,
                                max_length=max_length,
                                eos_token_id=self.terminators,
                                do_sample=True,
                                temperature=temperature,
                             )[0]["generated_text"][-1]["content"]


    def __call__(self, context, **kwargs):
        return self.generate(context, **kwargs)