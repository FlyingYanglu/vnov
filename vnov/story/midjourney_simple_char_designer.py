from vnov.story.character_designer import CharacterDesigner
from vnov.data.data import Novel
from vnov.story.prompts.midjourney_simple_char_designer import (
    DESIGNER_PROMPT,
    DESIGNER_ROLE,
    CHARACTER_INFO_EXAMPLE,
    DESIGNER_INSERTION
)

import random
import os
import json

class MidJourneySimpleCharDesigner(CharacterDesigner):

    designer_prompt = DESIGNER_PROMPT
    designer_role = DESIGNER_ROLE
    character_info_example = CHARACTER_INFO_EXAMPLE
    designer_insertion = DESIGNER_INSERTION

    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
    
    
    # def design_character(self, novel: Novel, character, context=None, **kwargs):
    #     # print("calling design_char in midjourney")
    #     if context is None:

    #         context, num_occurence = self.construct_design_context(novel, character, **kwargs)
    #         # contexts = self.find_character_context(novel, character)
    #         # chapter, context = random.choice(contexts)

    #     system_prompt = DESIGNER_ROLE.format(example=CHARACTER_INFO_EXAMPLE)
    #     prompt = DESIGNER_PROMPT.format(character_name=character, context=context)
    #     response = self.model(prompt, system_msg=system_prompt)
    #     response_json = self.parse_response(response)
    #     response_json["num_occurence"] = num_occurence
    #     return response_json

    def save_characters_info(self, novel: Novel, characters_info):
        save_dir = os.path.join(novel.dir, "midjourney_char_info.json")
        with open(save_dir, "w", encoding="utf-8") as f:
            json.dump(characters_info, f, ensure_ascii=False, indent=4)

