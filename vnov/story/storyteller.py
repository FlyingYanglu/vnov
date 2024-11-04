from vnov.story.prompts import (
    STORYTELLER_ROLE,
    TELLING_INSERTION,
    FIRSTPERSON_TELLING_SYSTEM_MSG,
    FIRSTPERSON_TELLING,
    FIRST_PERSON_TELLING_PREVIOUSLY,
    NOVEL_FS_EXAMPLE
)
from vnov.data import Novel
from vnov.role import Role
from vnov.utils import extract_json_from_string, storyteller_character_dict_constructer
import os
import json
import time


class StoryTeller(Role):
    bot_id="vnovStoryTeller"
    
    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        # self.context_token_length = self.model.token_length(self.format_context("",main_character=""))
        self.role = "storyteller"
        self.character_dict = {}
        self.chardict_save_interval = 1

    def take_action(self, **kwargs):
        return self.tell_chapter(**kwargs)

    
    def tell_chapter(self, novel:Novel, chapter_num, main_character="史金", last_context="", new_chat=False):
        stories, scene_jsons = [], []
        #cur_max_length = self.model.max_length - len(FIRSTPERSON_TELLING)-len(TELLING_INSERTION) - len(last_context)
        cur_max_length = self.model.max_length - self.model.token_length(FIRSTPERSON_TELLING)-self.model.token_length(TELLING_INSERTION) - self.model.token_length(last_context)
        print("method len",len(FIRSTPERSON_TELLING),"\n",len(TELLING_INSERTION),"\n",len(last_context))
        print("method token",self.model.token_length(FIRSTPERSON_TELLING),"\n",self.model.token_length(TELLING_INSERTION),"\n",self.model.token_length(last_context))
        chapter_content = novel.load_chapter(chapter_num)
        chapter_content, next_content = Novel.trunc_chapter(chapter_content, cur_max_length)
        while chapter_content:

            if chapter_num == 1:
                prompt = FIRSTPERSON_TELLING.format(content=chapter_content, main_character=main_character, insertion="")
            else:
                prompt = FIRSTPERSON_TELLING.format(content=chapter_content, main_character=main_character, insertion=TELLING_INSERTION)
            if last_context:
                prompt = FIRST_PERSON_TELLING_PREVIOUSLY.format(content=last_context) + prompt

            try:
                response, scene_json = self.parse_response(self.model(prompt, new_chat=new_chat, bot_id=self.bot_id,
                                                                  system_msg=FIRSTPERSON_TELLING_SYSTEM_MSG))
                if not scene_json:
                    raise Exception("No scene json found")
            except Exception as e:
                # redo the prompt
                print(f"Failed to generate response for chapter {chapter_num}, retrying...")
                print(e)
                if "Rate limit exceeded" in str(e):
                    print("Rate limit exceeded, waiting for 10 minutes...")
                    time.sleep(60*10)
                    self.send_init_message()
                continue
            scene_jsons.extend(scene_json)
            last_context = response
            last_context_len = self.model.max_length//4
            if len(last_context) > last_context_len:
                last_context = Novel.split_chapter(last_context, last_context_len)[-1]
                print("len",len(last_context))
            stories.append(response)

            if next_content:
                # cur_max_length = self.model.max_length - len(FIRSTPERSON_TELLING) - len(TELLING_INSERTION) - len(last_context)
                cur_max_length = self.model.max_length - self.model.token_length(FIRSTPERSON_TELLING)-self.model.token_length(TELLING_INSERTION) - self.model.token_length(last_context)
                chapter_content, next_content = Novel.trunc_chapter(next_content, cur_max_length)
            else:
                break
        story = "\n".join(stories)
        return story, scene_jsons
    
    



    def tell_novel(self, novel:Novel, main_character="史金", save_dir=None, start_chapter=1, end_chapter=None, **kwargs):
        if not save_dir:
            # save_dir = os.path.join(novel.dir, Novel.dirs_dict["script"])
            save_dir = novel.get_dir("script")
        
        if main_character is None:
            main_character = novel.main_character

        self.load_character_dict(save_dir, **kwargs)
        if kwargs.get("reset_chapters_inbetween", False):
            self.purge_character_dict(start_chapter, end_chapter, save_dir)


        self.save_prompt(save_dir)
        
        if kwargs.get("send_init", False):
            self.send_init_message()
            
        last_context = ""
        if end_chapter is None:
            end_chapter = novel.num_chapters + 1
        for chapter_num in range(start_chapter, end_chapter+1):
            print(f"Generating chapter {chapter_num}...")            
            story, scene_jsons = self.tell_chapter(novel, chapter_num, main_character=main_character, last_context=last_context)
            last_context = story
            self.update_character_dict(scene_jsons, chapter_num)

            self.save_file(story, os.path.join(save_dir, f"{chapter_num}.txt"))
            self.save_json(scene_jsons, os.path.join(save_dir, f"{chapter_num}.json"))
            if chapter_num % self.chardict_save_interval == 0:
                self.save_character_dict(save_dir)
            print(f"Chapter {chapter_num} generated.")


    def update_character_dict(self, scene_json, chapter_num):
        for scene_num, scene in enumerate(scene_json):
            for character in scene["Character List"]:
                if character not in self.character_dict:
                    self.character_dict[character] = {}

                if chapter_num not in self.character_dict[character]:
                    self.character_dict[character][chapter_num] = []

                self.character_dict[character][chapter_num].append(scene_num)

    def save_character_dict(self, save_dir):
        self.save_json(self.character_dict, os.path.join(save_dir, "character_dict.json"))
        

    def load_character_dict(self, save_dir, **kwargs):
        if kwargs.get("reset_character_dict", False):
            self.character_dict = {}
        character_dict_path = os.path.join(save_dir, "character_dict.json")
        if os.path.exists(character_dict_path):
            with open(character_dict_path, "r", encoding="utf-8") as f:
                self.character_dict = json.load(f)
                # change keys to int
                for character in list(self.character_dict.keys()):
                    self.character_dict[character] = {int(k): v for k, v in self.character_dict[character].items()}
        else:
            self.character_dict = {}

    def purge_character_dict(self, start_chapter, end_chapter, save_dir):
        for character in self.character_dict:
            for chapter_num in list(self.character_dict[character]):
                # if chapter_number is in the range of start_chapter and end_chapter, then remove it
                if chapter_num >= start_chapter and chapter_num <= end_chapter:
                    del self.character_dict[character][chapter_num]

        self.save_character_dict(save_dir)

    def parse_response(self, response):
        split_response = response.split("]")
        # json_string = "]".join(split_response[:-1]) + "]"
        # json_string = json_string[json_string.find("["):]
        # json_data = json.loads(json_string)
        json_data = extract_json_from_string(response)
        response = split_response[-1].strip().replace("```", "")
        return response, json_data

    def send_init_message(self):
        # self.bot.ask(newchat=True, bot=self.bot_model_name, prompt=NOVEL_FS_EXAMPLE)
        self.model(context=NOVEL_FS_EXAMPLE, new_chat=True, 
                   system_msg=FIRSTPERSON_TELLING_SYSTEM_MSG, bot_id=self.bot_id)
    
    def save_file(self, story, filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, "w", encoding="utf-8") as f:
            f.write(story)

    def save_json(self, data, filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_prompt(self, save_dir):
        # save current prompt to the save_dir
        prompt_dict = {
            "STORYTELLER_ROLE": STORYTELLER_ROLE,
            "TELLING_INSERTION": TELLING_INSERTION,
            "FIRSTPERSON_TELLING_SYSTEM_MSG": FIRSTPERSON_TELLING_SYSTEM_MSG,
            "FIRSTPERSON_TELLING": FIRSTPERSON_TELLING,
            "FIRST_PERSON_TELLING_PREVIOUSLY": FIRST_PERSON_TELLING_PREVIOUSLY,
            "NOVEL_FS_EXAMPLE": NOVEL_FS_EXAMPLE
        }
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        with open(os.path.join(save_dir, "prompt.json"), "w", encoding="utf-8") as f:
            json.dump(prompt_dict, f, ensure_ascii=False, indent=4)

    

    def format_context(self, content, **kwargs):
        main_character = kwargs.get("main_character", "")
        last_chapter = kwargs.get("last_chapter", "")
        if last_chapter:
            prev_context = FIRST_PERSON_TELLING_PREVIOUSLY.format(content=last_chapter)
            insertion = TELLING_INSERTION
        else:
            prev_context = ""
            insertion = ""
        context = prev_context + FIRSTPERSON_TELLING.format(content=content, main_character=main_character, insertion=insertion)
        messages = [
            {"role": "system", "content": STORYTELLER_ROLE},
            {"role": "user", "content": context},
        ]
        return messages
    
    def construct_character_dict(self, novel:Novel):
        return storyteller_character_dict_constructer().construct_refined_character_dict(novel)