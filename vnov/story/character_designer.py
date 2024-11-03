from vnov.role import Role
from vnov.utils import extract_json_from_string
from vnov.story.prompts import (
    CHARACTER_INFO_EXAMPLE,
    DESIGNER_ROLE,
    DESIGNER_PROMPT,
    DESIGNER_INSERTION,
    EXAMPLAR_OUTPUT
)
from vnov.data.data import Novel
import random
import os
import json
from vnov.data import Novel
from typing import List, Union, Literal

class CharacterDesigner(Role):
    bot_id = "vnoCharacterDesign"
    designer_prompt = DESIGNER_PROMPT
    designer_role = DESIGNER_ROLE
    character_info_example = CHARACTER_INFO_EXAMPLE
    designer_insertion = DESIGNER_INSERTION


    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.role = "character designer"

    def take_action(self, **kwargs):
        pass

    
    def find_character_context(self, novel: Novel, character, base_unit="chapter", design_source : List[str] = ["script", "storyboard"], **kwargs):
        assert base_unit in ["chapter", "scene"], "base_unit must be either 'chapter' or 'scene'"
        if base_unit == "chapter":
            return novel.locate_character(character)
        if base_unit == "scene":
            source_list = design_source
            for design_source in source_list:
                try:
                    if design_source == "script":
                        return novel.locate_character_scenes(character, mode = Novel.NOVEL_MODE.SCRIPT, **kwargs)
                    elif design_source == "storyboard":
                        return novel.locate_character_scenes(character, mode = Novel.NOVEL_MODE.STORYBOARD, **kwargs)
                except ValueError as e:
                    print(f"Failed to locate character {character} in mode {design_source}, trying alt mode. Error: {e}")
                    continue

            return novel.locate_character_scenes(character, **kwargs)
        
    def estimate_early_stop_count(self, novel: Novel, num_scenes = None, **kwargs):
        if not hasattr(self, "early_stop_count") or self.early_stop_count is None:
            if num_scenes is None:
                num_scenes = novel.count_scenes()
            self.early_stop_count = num_scenes//10
            print(f"Estimated early stop count: {self.early_stop_count}")
            return self.early_stop_count
        return self.early_stop_count
    
    def construct_design_context(self, 
                                 novel: Novel, 
                                 character, 
                                 base_unit="chapter", 
                                 context_choose_mode="random", 
                                 early_stop_count=50, 
                                 extra_contexts=3,
                                 design_source : List[str] = ["script", "storyboard"],
                                 **kwargs):
        assert context_choose_mode in ["random", "start", "dynamic_start"], "context_choose_mode must be either 'random', 'start' or 'dynamic_start'"
        # Get early_stop_count from kwargs if it isn't directly passed
        if early_stop_count is None:
            early_stop_count = self.estimate_early_stop_count(novel, character, **kwargs)

            
        contexts = self.find_character_context(novel, character, base_unit=base_unit, early_stop_count=early_stop_count, design_source = design_source, **kwargs)
        print(f"Found {len(contexts)} contexts for character {character}")
        chosen_contexts = []
        if context_choose_mode == "random":
            chapter, context = random.choice(contexts)
            chosen_contexts.append(context)
        elif context_choose_mode == "start":
            chapter, context = contexts[0]
            chosen_contexts.append(context)
        elif context_choose_mode == "dynamic_start":
            if len(contexts) >= early_stop_count:
                # do three contexts if early stop
                num_contexts = extra_contexts
                print(f"Detected early stop at {early_stop_count} contexts, using {num_contexts} contexts to ensure enough information")
            else:
                num_contexts = 1
                
            context = ""
            with_previous = False
            skip_count = 0
            for chapter, scene_content in contexts:
                if skip_count > 0:
                    skip_count -= 1
                    continue
                scene_content = f"Chapter {chapter} \n{scene_content}"
                if with_previous:
                    context_max_length = self.model.max_length - len(self.designer_insertion) - len(self.character_info_example)
                else:
                    context_max_length = self.model.max_length - len(self.designer_prompt)
                if len(context) + len(scene_content) < context_max_length:
                    context += scene_content
                else:
                    chosen_contexts.append(context)
                    context = ""
                    num_contexts -= 1
                    with_previous = True
                    if num_contexts == 0:
                        break
                    skip_count = early_stop_count//extra_contexts - 1

            if context:
                chosen_contexts.append(context)
        return chosen_contexts, len(contexts)
    
    
    def filter_character_names(self, character_dict, filter_threshold=-1):
        if filter_threshold == -1:
            return list(character_dict.keys())
        filtered_character_names = [name for name in character_dict if sum(len(s) for s in character_dict[name].values()) > filter_threshold]
        return filtered_character_names

    
    def design_all_characters(self, 
                          novel: Novel,
                          re_design: bool = False,
                          filter_threshold: int = -1, 
                          num_retries: int = 2,
                          base_unit: Literal["chapter", "scene"] = "chapter",
                          context_choose_mode: Literal["random", "start", "dynamic_start"] = "dynamic_start",
                          design_source : List[str] = ["script", "storyboard"],
                          source_character_dict: Literal["script", "storyboard"] = "storyboard",
                          **kwargs):
        if source_character_dict == "script":
            mode = Novel.NOVEL_MODE.SCRIPT
            version = "normal"
        elif source_character_dict == "storyboard":
            mode = Novel.NOVEL_MODE.STORYBOARD
            version = "chunked"
        character_dict = novel.load_character_dict(mode=mode, version=version)

        num_scenes = sum([sum(len(s) for s in character_dict[name].values()) for name in character_dict])
        early_stop_count = kwargs.get("early_stop_count", None)
        if early_stop_count is None:
            early_stop_count = self.estimate_early_stop_count(novel, num_scenes=num_scenes, **kwargs)
        
        character_names = self.filter_character_names(character_dict, filter_threshold=filter_threshold)
        characters_info = dict()
        if not re_design:
            characters_info = novel.load_characters_info()
        i = 0
        while i < len(character_names):
            character_name = character_names[i]
            if character_name in characters_info:
                continue
            print(f"Designing character {character_name} {i+1}/{len(character_names)}")
            
            try:
                character = self.design_character(
                    novel, character_name, 
                    base_unit=base_unit, 
                    context_choose_mode=context_choose_mode, 
                    num_retries=num_retries,
                    design_source=design_source,
                    early_stop_count=early_stop_count,
                    **kwargs
                )
            except Exception as e:
                print(f"Error designing character {character_name}: {e}")
                i += 1
                continue
            characters_info[character_name] = character
            self.save_characters_info(novel, characters_info)
            i += 1
        return characters_info
    

    def design_character(self, 
                         novel: Novel, 
                         character_name, 
                         contexts: List[str] = None, 
                         base_unit : Literal["chapter", "scene"] = "scene",
                         context_choose_mode : Literal["random", "start", "dynamic_start"] = "dynamic_start",
                         num_retries: int = 2,
                         design_source : List[str] = ["script", "storyboard"],
                         **kwargs
                         ):
        
        
        if not contexts:
            contexts, num_occurence = self.construct_design_context(novel, character_name, base_unit = base_unit, 
                                                     context_choose_mode=context_choose_mode, design_source = design_source, **kwargs)

        prev_out = ""
        i = 0
        new_chat = True
        retries = num_retries
        while i < len(contexts):
            context = contexts[i]
            system_prompt = self.designer_role.format(example=self.character_info_example)
            prompt = self.designer_prompt.format(character_name=character_name, context=context)
            if prev_out:
                prompt = self.designer_insertion.format(prev_out=prev_out, character_name=character_name, context=context)
            
            try:
                response = self.model(prompt, system_msg=system_prompt, new_chat=new_chat, bot_id=self.bot_id)
                response_json = self.parse_response(response)
                prev_out = response_json
                retries = num_retries
            except Exception as e:
                if retries > 0:
                    print(f"Error designing character {character_name} retrying for {retries} more times")
                    retries -= 1
                    continue
                else:
                    print(f"Retry failed! Error designing character {character_name} skipping")
                    i += 1
                    
                    continue
            i += 1
            new_chat = False
        if not contexts:
            print("WARNING: Context is empty, Character info might be random")
            response_json["random_character_generated"] = True
        response_json["num_occurence"] = num_occurence
        return response_json
    



    def parse_response(self, response):
        response_json = extract_json_from_string(response, raise_exception=True)
        return response_json
    
    def save_characters_info(self, novel: Novel, characters_info):
        save_dir = os.path.join(novel.dir, "characters_info.json")
        with open(save_dir, "w", encoding="utf-8") as f:
            json.dump(characters_info, f, ensure_ascii=False, indent=4)


