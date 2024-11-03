from vnov.role import Role
from vnov.story.prompts.director import (
    GENERAL_DIRECTOR_INSTRUCTION,
    DIRECTOR_EXAMPLE,
    MIDJOURNEY_DIRECTOR_ROLE,
    DIRECTOR_PROMPT,
    BATCH_DIRECTOR_PROMPT,
    DIRECTOR_ROLE,
    DIRECTOR_MULCHARACTER_EXAMPLE,
    MIDJOURNEY_DIRECTOR_INSTRUCTION,
    MIDJOURNEY_DIRECTOR_EXAMPLE,
    MIDJOURNEY_DIRECTOR_MULCHARACTER_EXAMPLE,
    MIDJOURNEY_DIRECTOR_PROMPT
)
from vnov.utils import extract_json_from_string
from vnov.data import Novel
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class Director(Role):
    role = "director"
    bot_id = "xxxx"

    def generate_image_prompt(self, scene, mode="Dambooru"):
        if mode == "Dambooru":
            prompt = DIRECTOR_PROMPT.format(storyboard=scene, instruction=GENERAL_DIRECTOR_INSTRUCTION, 
                                            example=DIRECTOR_EXAMPLE, multiple_character_example=DIRECTOR_MULCHARACTER_EXAMPLE)
        else:
            prompt = MIDJOURNEY_DIRECTOR_PROMPT.format(storyboard=scene, instruction=MIDJOURNEY_DIRECTOR_INSTRUCTION, 
                                            example=MIDJOURNEY_DIRECTOR_EXAMPLE, multiple_character_example=MIDJOURNEY_DIRECTOR_MULCHARACTER_EXAMPLE)
        system_prompt = DIRECTOR_ROLE if mode == "Dambooru" else MIDJOURNEY_DIRECTOR_ROLE
        response = self.model(prompt, system_msg=system_prompt, new_chat=False, bot_id=self.bot_id)
        response_json = extract_json_from_string(response)
        return response_json
    
    def generate_batch_image_prompt(self, scenes, mode="Dambooru"):
        #TODO: check if this works after change in prompts
        scenes = [json.dumps(scene, ensure_ascii=False) for scene in scenes]
        scenes_text = "\n\n".join(scenes)
        if mode == "Dambooru":
            prompt = BATCH_DIRECTOR_PROMPT.format(storyboard=scenes_text, instruction=GENERAL_DIRECTOR_INSTRUCTION, 
                                                  example=DIRECTOR_EXAMPLE, multiple_character_example=DIRECTOR_MULCHARACTER_EXAMPLE)
        else:
            prompt = BATCH_DIRECTOR_PROMPT.format(storyboard=scenes_text, instruction=MIDJOURNEY_DIRECTOR_EXAMPLE, 
                                                  example=MIDJOURNEY_DIRECTOR_EXAMPLE, multiple_character_example=MIDJOURNEY_DIRECTOR_MULCHARACTER_EXAMPLE)
        system_prompt = DIRECTOR_ROLE if mode == "Dambooru" else MIDJOURNEY_DIRECTOR_ROLE
        response = self.model(prompt, system_msg=system_prompt, new_chat=False, bot_id=self.bot_id)
        response_json = extract_json_from_string(response)
        return response_json


    def load_combined_scenes(self, novel:Novel, mode="Dambooru"):
        character_info = novel.load_characters_info()
        storyboards = novel.load_scene_dict()
        combined_scenes = []
        for scene in storyboards:
            del scene["原文起始点"]
            c_dict = scene["角色"]
            char_info = len(c_dict) > 1
            for character_dict in c_dict:
                character = character_dict["名字"]
                # if character == "我":
                #     character = novel.main_character
                if character in character_info.keys():
                    if mode == "Dambooru":
                        character_dict["角色信息"] = character_info[character]
                        character_dict["角色信息"].pop("Name", None)
                    elif mode == "Midjourney":
                        cinfo = character_info[character]
                        if not char_info:
                            character_dict["角色性别"] = cinfo['Gender']
                        else:
                            character_dict["角色信息"] = character_info[character]
                            character_dict["角色信息"].pop("Name", None)
                else:
                    char_info = True
                    character_dict["角色信息"] = character
                    print(f"Character {character} not found in character_info")
                if mode == "Midjourney":
                    character_dict.pop("名字", None)
            combined_scenes.append(scene)
        return combined_scenes
    
    def run(self, novel, batch_size=1, mode="Dambooru", multiprocess=False):
        combined_scenes = self.load_combined_scenes(novel)
        prompt_lst = [None] * len(combined_scenes)
        save_path = os.path.join(novel.dir, "prompts")
        os.makedirs(save_path, exist_ok=True)
        save_path = os.path.join(save_path, f"director_prompts_{mode}.json")


        def process_batch(i):
            batch = combined_scenes[i]
            response_json = self.generate_image_prompt(batch, mode=mode)
            return i, response_json["prompt"]

        if multiprocess:
            # Multithreading for batch processing
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(process_batch, i): i for i in range(len(combined_scenes))}

                for future in as_completed(futures):
                    i, prompt = future.result()
                    prompt_lst[i] = prompt
                    
                    if i % 10 == 0:
                        # Cache intermediate results every 10 batches
                        with open(save_path, "w", encoding="utf-8") as f:
                            json.dump(prompt_lst, f, ensure_ascii=False, indent=4)  

        else:
            for i in range(0, len(combined_scenes), batch_size):
                if batch_size == 1:
                    batch = combined_scenes[i]
                    response_json = self.generate_image_prompt(batch, mode=mode)
                    prompt_lst.append(response_json["prompt"])
                else:
                    batch = combined_scenes[i:i+batch_size]
                    response_json = self.generate_batch_image_prompt(batch, mode=mode)
                    prompt_lst.extend(response_json["prompts"])
                
                
                if i % 10 == 0:
                    # cache
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(prompt_lst, f, ensure_ascii=False, indent=4)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(prompt_lst, f, ensure_ascii=False, indent=4)
        return prompt_lst
