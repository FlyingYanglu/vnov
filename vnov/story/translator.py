from vnov.role import Role
from vnov.llms.base import BaseLLM
from vnov.story.prompts.translator import (
    EXAMPLE_RESULT,
    TRANSLATOR_ROLE,
    TRANSLATOR_PROMPT
)
from vnov.utils import extract_json_from_string
from vnov.data.data import Novel
import random
import os
import json


class Translator(Role):
    fields_to_translate = set(["场景", "动作", "表情", "服装"])
    def __init__(self, model: BaseLLM, **kwargs):
        super().__init__(model, **kwargs)
        self.role = "translator"
    
    def get_input(self, novel: Novel):
        combined_path = os.path.join(novel.dir, "storyboard/storyboard_combined_refined_script.json")
        with open(combined_path, "r", encoding="utf-8") as f:
            scenes = json.load(f)
        return scenes

    def translate(self, novel: Novel):
        scenes = self.get_input(novel)
        result = []
        for i, dc in enumerate(scenes):
            rest = {k:dc[k] for k in dc.keys() if k not in self.fields_to_translate}
            to_translate = {k:dc[k] for k in dc.keys() if k in self.fields_to_translate}
            
            system_prompt = TRANSLATOR_ROLE.format(example=EXAMPLE_RESULT)
            prompt = TRANSLATOR_PROMPT.format(input=str(to_translate))
            response = self.model(prompt, system_msg=system_prompt)
            response_json = extract_json_from_string(response)
            rest.update(response_json)

            result.append(rest)
            if i % 10 == 1:
                self.save_output(novel, result)
        self.save_output(novel, result)
        return result
 

    def save_output(self, novel: Novel, result: list):
        save_dir = os.path.join(novel.dir, "storyboard/translated_storyboard.json")
        with open(save_dir, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
