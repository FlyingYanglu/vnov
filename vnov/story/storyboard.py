import os
import json
import time
from vnov.data import Novel, NOVEL_MODE
from vnov.story.prompts.storyboard import STORYBOARD_ARTIST_PROMPT, STORYBOARD_ARTIST_ROLE, STORYBOARD_ARTIST_INSERTION, STORYBOARD_ARTIST_ACT, STORYBOARD_EXAMPLE
from poept import PoePT
from vnov.story.refiner import Refiner
from vnov.role import Role
from vnov.utils import extract_json_from_string
from glob import glob
import re
from natsort import natsorted
from vnov.utils import storyboard_character_dict_constructer
from concurrent.futures import ThreadPoolExecutor, as_completed

STORYBOARD_EXAMPLE = json.dumps(STORYBOARD_EXAMPLE, separators=(',', ':'), ensure_ascii=False)

class Storyboard(Role):
    bot_id="vnoStoryboardArtist"
    
    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.role = "storyboard"
        self.character_dict_constructor = storyboard_character_dict_constructer()  # Constructor instance
        self.character_dict = {}  # Dictionary to store character details

    def save_json(self, response_json, output_dir, name):
        output_file = os.path.join(output_dir, f"storyboard_{name}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(response_json, f, indent=4, ensure_ascii=False)

    def save_file(self, content, output_dir, name, extension="txt"):
        output_file = os.path.join(output_dir, f"{name}.{extension}")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

    def parse_response(self, response):
        try:
            response_json = extract_json_from_string(response, raise_exception=True)
            return response_json
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Failed to parse response")
            raise e

    def send_init_message(self):
        raise NotImplementedError("Method not implemented")

    def _read_chunk(self, save_dir, chunk_index):
        with open(os.path.join(save_dir, f"chunk_{chunk_index}.txt"), "r", encoding="utf-8") as f:
            return f.read()

    def _create_prompt(self, last_context, script_content, main_character):
        if last_context:
            return (STORYBOARD_ARTIST_INSERTION.format(content=last_context) +
                    STORYBOARD_ARTIST_PROMPT.format(content=script_content, main_character=main_character, 
                                                    insertion="", example_json=STORYBOARD_EXAMPLE))
        else:
            return STORYBOARD_ARTIST_PROMPT.format(content=script_content, main_character=main_character, 
                                                   insertion=STORYBOARD_ARTIST_ACT, example_json=STORYBOARD_EXAMPLE)

    def _process_chunk(self, chunk_index, save_dir, main_character, last_context, new_chat, num_retries):
        script_content = self._read_chunk(save_dir, chunk_index)
        prompt = self._create_prompt(last_context, script_content, main_character)

        while num_retries > 0:
            try:
                response = self.model(prompt, new_chat=new_chat, bot_id=self.bot_id, system_msg=STORYBOARD_ARTIST_ROLE)
                scene_json = self.parse_response(response)

                # Save scene JSON
                self.save_json(scene_json, save_dir, f"chunk_{chunk_index}")

                

                for j, scene in enumerate(scene_json):
                    original_chunk = self.character_dict_constructor.find_original_chunk(script_content, scene, scene_json, j)
                    self.character_dict_constructor.update_character_dict(
                        self.character_dict, scene, original_chunk, chunk_index, j, save_dir=save_dir
                    )
                return scene_json
            except Exception as e:
                num_retries -= 1
                print(f"Error processing chunk {chunk_index}: {e}, retrying ({num_retries} retries left)")
                time.sleep(5)

        print(f"Failed to process chunk {chunk_index}, skipping...")
        return None

    def _worker(self, chunk_indices, save_dir, main_character, last_context, **kwargs):
        scene_jsons = []
        for chunk_index in chunk_indices:
            scene_json = self._process_chunk(chunk_index, save_dir, main_character, last_context, 
                                             new_chat=True, num_retries=8)
            if scene_json:
                scene_jsons.extend(scene_json)
                last_context = str(self.construct_last_context(mode="original", cur_scene_jsons=scene_jsons, prev_contexts_string=last_context))
        return scene_jsons

    def storyboarding_script(self, script_content, save_dir, main_character="史金", last_context="", 
                             default_num_of_units=4, start_index=None, num_workers=4, **kwargs):
        num_of_units = default_num_of_units
        if start_index is None:
            Novel.split_chapter_by_units(script_content, num_of_units=num_of_units, save_dir=save_dir)
            start_index = 0

        script_files = natsorted(glob(os.path.join(save_dir, "chunk_*.txt")))
        total_chunks = len(script_files)

        if start_index >= total_chunks:
            print("All chunks have been processed.")
            return

        chunk_indices = list(range(start_index, total_chunks))
        chunks_per_worker = (len(chunk_indices) + num_workers - 1) // num_workers  # Round up

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(self._worker, chunk_indices[i:i + chunks_per_worker], save_dir, 
                                main_character, last_context, **kwargs)
                for i in range(0, len(chunk_indices), chunks_per_worker)
            ]

            all_scene_jsons = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        all_scene_jsons.extend(result)
                except Exception as e:
                    print(f"Error in worker thread: {e}")

        return all_scene_jsons

    def construct_last_context(self, mode="original", **kwargs):
        if mode == "original":
            return self.get_history_responses(**kwargs)
        elif mode == "summary":
            return self.get_last_act_scenes(**kwargs)
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def get_history_responses(self, cur_scene_jsons, prev_contexts_string, max_length=2000, **kwargs):
        cur_scene_jsons = str(self.compress_json(cur_scene_jsons))
        new_context = prev_contexts_string + cur_scene_jsons
        new_context = new_context.split("\n")
        while len(new_context) > 0 and len("\n".join(new_context)) > max_length:
            new_context.pop(0)
        return "\n".join(new_context)

    def get_last_act_scenes(self, scene_jsons, max_act=3, last_act_char_costum=None, **kwargs):
        if last_act_char_costum is None:
            last_act_char_costum = {}
        cur_act = last_act_char_costum.get("scene", None)
        environment = {}

        for scene in scene_jsons[::-1]:
            if cur_act is None:
                cur_act = scene["act"]
                for char in scene["characters"]:
                    char_name = char["name"]
                    last_act_char_costum[char_name] = char.get("costume", {})
                environment = scene.get("scene", {})
            elif scene["act"] == cur_act:
                last_act_char_costum.update({char["name"]: char.get("costume", {}) for char in scene["characters"]})
            else:
                break

        last_context_info = {
            "act": cur_act,
            "scene": environment,
            "costume": last_act_char_costum
        }
        return last_context_info

    def storyborading_all_refined(self, novel: Novel, main_character=None, src_file_name="combined_commentaries", start_index=None, **kwargs):
        if kwargs.get("reconcatenate", False):
            Refiner.concatenate_refined(os.path.join(novel.dir, novel.dirs_dict["refined"]), src_file_name)
        novel_content = novel.load_chapter(src_file_name, mode=Novel.NOVEL_MODE.REFINED)
        save_dir = os.path.join(novel.dir, novel.dirs_dict["storyboard"])

        if main_character is None:
            main_character = novel.main_character
        storyboard_scenes = self.storyboarding_script(novel_content, save_dir, main_character=main_character, start_index=start_index, **kwargs)
        self.save_json(storyboard_scenes, save_dir, "combined")
        self.character_dict_constructor.save_json(self.character_dict, save_dir, "character_dict_chunked")

    @staticmethod
    def compress_json(json_obj):
        return json.dumps(json_obj, separators=(',', ':'), ensure_ascii=False)
