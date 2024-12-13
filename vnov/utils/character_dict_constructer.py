import json
import re
import os
from glob import glob
from natsort import natsorted

class character_dict_constructer:
    """Base class for character dictionary construction."""

    def __init__(self):
        pass

    def load_json(self, file_path):
        """Helper to load JSON with error handling."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {file_path}: {e}")
            return []

    def read_file_content(self, file_path):
        """Helper to read file content with proper error handling."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError as e:
            print(f"File not found: {file_path}")
            return ""

    def find_original_chunk(self, chapter_content, scene, scene_jsons, scene_index):
        """Find the chunk of text corresponding to the scene."""
        # Clean the text and get a mapping from cleaned indices to original indices
        cleaned_content, index_map = self.clean_text_with_mapping(chapter_content)
        cleaned_scene_start = self.clean_text(scene.get("text", ""))

        starting_index = cleaned_content.find(cleaned_scene_start)
        if starting_index == -1:
            return None

        ending_index = self.find_ending_index(cleaned_content, scene_jsons, scene_index, starting_index)

        # Map the indices back to the original text using index_map
        original_starting_index = index_map[starting_index]
        original_ending_index = index_map[ending_index] if ending_index < len(index_map) else len(chapter_content)

        return chapter_content[original_starting_index:original_ending_index]

    def find_ending_index(self, cleaned_content, scene_jsons, current_scene_index, starting_index):
        """Helper to find the ending index of the scene."""
        for next_scene_index in range(current_scene_index + 1, len(scene_jsons)):
            next_start = self.clean_text(scene_jsons[next_scene_index].get("text", ""))
            next_start_index = cleaned_content.find(next_start)
            if next_start_index != -1:
                return next_start_index

        return len(cleaned_content)  # If no next scene, return the rest of the content

    def clean_text_with_mapping(self, text):
        """
        Clean text by removing punctuation, spaces, and newlines.
        Also return a mapping from cleaned text indices to original text indices.
        """
        cleaned_text = []
        index_map = []

        # Regex to match Chinese and English punctuation, spaces, and newlines
        pattern = r'[^\w\u4e00-\u9fff]'

        # Iterate through original text and build cleaned text and index map
        for i, char in enumerate(text):
            if not re.match(pattern, char):
                cleaned_text.append(char)
                index_map.append(i)  # Map cleaned index to original index

        return ''.join(cleaned_text), index_map

    def clean_text(self, text):
        """Helper to clean text by removing punctuation, spaces, and newlines."""
        pattern = r'[^\w\u4e00-\u9fff]'  # Matches punctuation, spaces, and newlines
        return re.sub(pattern, '', text)

    def save_json(self, response_json, output_dir, name):
        """Helper to save JSON files."""
        output_file = os.path.join(output_dir, f"{name}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(response_json, f, indent=4, ensure_ascii=False)


class storyteller_character_dict_constructer(character_dict_constructer):
    """Constructs character dictionary for storyteller."""

    def __init__(self):
        super().__init__()

    def construct_refined_character_dict(self, novel):
        save_dir = os.path.join(novel.dir, novel.dirs_dict["script"])
        original_novel_dir = os.path.join(novel.dir, novel.dirs_dict["original"])
        character_dict = {}

        chunk_files = natsorted(glob(os.path.join(original_novel_dir, "[0-9]*.txt")))
        chunk_scene_jsons = natsorted(glob(os.path.join(save_dir, "[0-9]*.json")))

        for i, (chunk_file, scene_jsons) in enumerate(zip(chunk_files, chunk_scene_jsons)):
            chapter_content = self.read_file_content(chunk_file)
            scene_jsons = self.load_json(scene_jsons)
            for j, scene in enumerate(scene_jsons):
                original_chunk = self.find_original_chunk(chapter_content, scene, scene_jsons, j)
                self.update_character_dict(character_dict, scene, original_chunk, i, j)

        self.save_json(character_dict, save_dir, "character_dict_chunked")
        return character_dict

    def update_character_dict(self, character_dict, scene, original_chunk, chunk_index, scene_index):
        """Helper to update the character dictionary."""
        for char in scene.get("出场人物列表", []):
            char_name = str(char)
            character_dict.setdefault(char_name, {}).setdefault(str(chunk_index + 1), {})[str(scene_index + 1)] = {
                "chunk": original_chunk
            }


class storyboard_character_dict_constructer(character_dict_constructer):
    """Constructs character dictionary for storyboard."""

    def __init__(self):
        super().__init__()

    def construct_refined_character_dict(self, novel):
        storyboard_dir = os.path.join(novel.dir, novel.dirs_dict["storyboard"])
        character_dict = {}

        chunk_files = natsorted(glob(os.path.join(storyboard_dir, "chunk_*.txt")))
        chunk_scene_jsons = natsorted(glob(os.path.join(storyboard_dir, "storyboard_chunk_*.json")))

        for i, (chunk_file, scene_jsons) in enumerate(zip(chunk_files, chunk_scene_jsons)):
            chapter_content = self.read_file_content(chunk_file)
            scene_jsons = self.load_json(scene_jsons)
            for j, scene in enumerate(scene_jsons):
                original_chunk = self.find_original_chunk(chapter_content, scene, scene_jsons, j)
                self.update_character_dict(character_dict, scene, original_chunk, i, j)

        self.save_json(character_dict, storyboard_dir, "character_dict_chunked")
        return character_dict

    def update_character_dict(self, character_dict, scene, original_chunk, chunk_index, scene_index, save_dir=None):
        """Helper to update the character dictionary."""
        for char in scene.get("characters", []):
            char_name = str(char["name"])
            character_dict.setdefault(char_name, {}).setdefault(str(chunk_index), {})[str(scene_index)] = {
                "act": scene.get("act", ""),
                "chunk": original_chunk
            }

        if save_dir:
            self.save_json(character_dict, save_dir, "character_dict_chunked")
