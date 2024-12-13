import os
import json
from typing import Union
import re
from vnov.utils.sentence_splitter.spliter_sentence import Spliter
from natsort import natsorted

class NOVEL_MODE:
    ORIGINAL = "original"
    SCRIPT = "script"
    REFINED = "refined"
    STORYBOARD = "storyboard"
    PROMPTS = "prompts"
    CHAR_IMAGES = "char_images"
    SCENE_IMAGES = "scene_images"
    TTS = "tts"

class Novel:
    dirs_dict = {
        "original": "original",
        "script": "script",
        "refined": "refined_script",
        "storyboard": "storyboard",
        "prompts": "prompts",
        "scene_images": "scene_images2",
        "char_images": "mj_char_images",
        "tts": "tts",
        "summary": "summary"
    }
    dir : str = None
    bookname : str = None
    description : str = None
    num_chapters : int = None
    NOVEL_MODE = NOVEL_MODE
    main_character : str = None

    def __init__(self, dir, main_character, novel_mode: str = NOVEL_MODE.ORIGINAL, **kwargs):
        self.data_dir = dir
        sub_dir = kwargs.get('sub_dir', "default")
        self.dir = os.path.join(dir, sub_dir)
        self.novel_mode = novel_mode
        self.load_novel_info()
        self.main_character = main_character
        self.default_mode = novel_mode


    def get_dir(self, mode: str):

        sub_dir = self.dirs_dict[mode]
        if mode in self.dirs_dict:
            if mode == NOVEL_MODE.ORIGINAL:
                return os.path.join(self.data_dir, sub_dir)
            else:
                return os.path.join(self.dir, sub_dir)
        else:
            raise ValueError(f"Invalid mode: {mode}")



    
    def load_novel_info(self):
        dir = self.get_dir(NOVEL_MODE.ORIGINAL)
        with open(os.path.join(dir, 'info.json'), 'r', encoding="utf-8") as f:
            info = json.load(f)
        folder_name = os.path.basename(self.dir)
        self.bookname = info.get('bookname', folder_name)
        self.description = info.get('description', 'No description')

        with open(os.path.join(dir, 'chapters.json'), 'r', encoding="utf-8") as f:
            # load json list
            chapters = json.load(f)
        self.num_chapters = len(chapters)
        for dir in self.dirs_dict.values():
            os.makedirs(os.path.join(self.dir, dir), exist_ok=True)

    def load_chapter(self, chapter: Union[int, str], mode: str = NOVEL_MODE.ORIGINAL, extension = "txt", **kwargs):
        dir = self.get_dir(mode)
        with open(os.path.join(dir, f'{chapter}.{extension}'), 'r', encoding="utf-8") as f:
            return f.read()
        
    def get_mode_paths(self, mode: str, extension = None):
        dir = self.get_dir(mode)
        if extension is None:
            return [os.path.join(dir, f) for f in natsorted(os.listdir(dir))]
        files = [f for f in natsorted(os.listdir(dir)) if f.endswith(f".{extension}")]
        return [os.path.join(dir, f) for f in files]
    
    def load_files(self, mode: str = NOVEL_MODE.ORIGINAL, extension="txt", as_generator=True):
        """
        Load all files in the specified mode directory with the given extension.

        :param mode: The mode of the novel, e.g., original, script, refined.
        :param extension: The extension of the files to load, e.g., txt, json.
        :param as_generator: If True, return a generator. Otherwise, return a list.

        :return: A generator if as_generator is True; otherwise, a list of file contents.
        """
        
        file_paths = self.get_mode_paths(mode, extension)

        if as_generator:
            # Act as a generator
            for fpath in file_paths:
                with open(fpath, 'r', encoding="utf-8") as f:
                    yield {"fpath": fpath, "content": f.read()}
        else:
            # Collect all contents in a list and return
            contents = []
            for fpath in file_paths:
                with open(fpath, 'r', encoding="utf-8") as f:
                    contents.append({"fpath": fpath, "content": f.read()})
            return contents
    
    def load_character_dict(self, mode=NOVEL_MODE.SCRIPT, version = "normal", **kwargs):
        dir = self.get_dir(mode)
        if version == "normal":
            file = os.path.join(dir, 'character_dict.json')
        elif version == "chunked":
            file = os.path.join(dir, 'character_dict_chunked.json')
        with open(file, 'r', encoding="utf-8") as f:
            return json.load(f)
        
    def load_scenes(self):
        dir = self.get_dir(NOVEL_MODE.SCRIPT)
        scenes = []
        # load all json files with name like 1.json, 2.json, not word.json
        for fpath in os.listdir(dir):
            if re.match(r'\d+\.json', fpath):
                with open(os.path.join(dir, fpath), 'r', encoding="utf-8") as f:
                    scenes.extend(json.load(f))
        return scenes
    
    def count_scenes(self):
        # if hasattr(self, 'num_scenes'):
        if hasattr(self, 'num_scenes') and self.num_scenes is not None:
            return self.num_scenes
        self.num_scenes = len(self.load_scenes())
        return self.num_scenes

    
    def load_characters_info(self):
        fpath = os.path.join(self.dir, 'characters_info.json')
        if not os.path.exists(fpath):
            return {}
        with open(fpath, 'r', encoding="utf-8") as f:
            return json.load(f)
        
    def load_scene_dict(self):
        storyboard_dir = self.get_dir(NOVEL_MODE.STORYBOARD)
        fpath = os.path.join(storyboard_dir, 'storyboard_combined.json')
        if not os.path.exists(fpath):
            return {}
        with open(fpath, 'r', encoding="utf-8") as f:
            return json.load(f)
    
    def locate_character(self, character):
        character_dict = self.load_character_dict()
        if character in character_dict:
            chapter_list = list(character_dict[character].keys())
            chapter_list = sorted([int(chapter) for chapter in chapter_list])
            contents = [(chapter, self.load_chapter(chapter, NOVEL_MODE.ORIGINAL)) for chapter in chapter_list]
            return contents
        else:
            raise ValueError(f"Character {character} not found in novel {self.bookname} Out of {character_dict.keys()}")
    
    def locate_character_scenes(self, character, mode=NOVEL_MODE.SCRIPT, version = "chunked", **kwargs):
        # using character to chapter, scene information in the character_dict to locate the scenes to level of original text
        # return contexts list of tuples (chapter, scene), scene_content

        character_dict = self.load_character_dict(mode = mode, version = version, **kwargs)
        res = []
        if character in character_dict:
            for chapter, scenes in character_dict[character].items():
                for scene, scene_info in scenes.items():
                    scene_content = scene_info["chunk"]
                    # yield (chapter, scene), scene_content
                    res.append(((chapter, scene), scene_content))
            
            return res
        else:
            raise ValueError(f"Character {character} not found in novel {self.bookname} out of {character_dict.keys()}")
    
    def get_mj_prompts(self):
        """Retrieve Midjourney prompts from the storyboard."""
        prompts_dir = self.get_dir(NOVEL_MODE.PROMPTS)
        with open(os.path.join(prompts_dir, "eng_director_prompts_Midjourney.json"), "r", encoding="utf-8") as f:
            mj_prompts = json.load(f)
        return mj_prompts

    def get_storyboard(self):
        """Retrieve storyboard information for scenes."""
        return self.load_scene_dict()  # this method already returns the storyboard data

    def get_char_to_url(self):
        """Retrieve character to URL mappings."""
        char_images_dir = self.get_dir(NOVEL_MODE.CHAR_IMAGES)
        with open(os.path.join(char_images_dir, "char_to_url.json"), "r", encoding="utf-8") as f:
            char_to_url = json.load(f)
        return char_to_url

    @staticmethod
    def split_chapter(content, max_length, model=None):
        def calculate_token_length(text):
            """Calculate token length if a model is provided."""
            return model.token_length(text) if model else 0

        def can_add_to_chunk(chunk, unit_txt):
            """Check if a unit can be added to the current chunk."""
            return (
                len(chunk) + len(unit_txt) < max_length and
                (not model or calculate_token_length(chunk + unit_txt) <= max_length)
            )

        def split_long_unit(unit_txt):
            """Split a long unit into smaller chunks based on max_length."""
            temp_chunks = []
            temp_chunk = ""
            for char in unit_txt:
                temp_chunk += char
                if model:
                    if calculate_token_length(temp_chunk) >= max_length or len(temp_chunk) >= max_length:
                        temp_chunks.append(temp_chunk)
                        temp_chunk = ""
                else:
                    if len(temp_chunk) >= max_length:
                        temp_chunks.append(temp_chunk)
                        temp_chunk = ""
            if temp_chunk:
                temp_chunks.append(temp_chunk)
            return temp_chunks

        def redistribute_chunks(chunks):
            """Redistribute the last two chunks if the final chunk is too small."""
            if len(chunks) > 1 and len(chunks[-1]) < max_length // 10:
                print("Imbalance detected, redistributing the last two chunks.")
                last_chunk = chunks.pop()
                second_last_chunk = chunks.pop()
                combined_chunks = second_last_chunk + last_chunk
                max_combined_tokens = calculate_token_length(combined_chunks) // 2
                max_combined_length = len(combined_chunks) // 2

                chunk1, chunk2 = "", ""
                for paragraph in combined_chunks.split('\n'):
                    if (
                        (not model or calculate_token_length(chunk1 + paragraph) <= max_combined_tokens) and
                        len(chunk1 + paragraph) <= max_combined_length
                    ):
                        chunk1 += paragraph + '\n'
                    else:
                        chunk2 += paragraph + '\n'
                chunks.append(chunk1.strip())
                chunks.append(chunk2.strip())
            return chunks

        # Main splitting logic
        minimum_txt_units = content.split('\n')
        chunks = []
        chunk = ""

        for unit_txt in minimum_txt_units:
            if can_add_to_chunk(chunk, unit_txt):
                chunk += unit_txt + '\n'
            else:
                if len(chunk) == 0:
                    chunks.extend(split_long_unit(unit_txt))
                else:
                    chunks.append(chunk)
                    chunk = unit_txt

        if len(chunk) > 0:
            chunks.append(chunk)

        return redistribute_chunks(chunks)


    @staticmethod
    def trunc_chapter(content, max_length, mode="force_split"):
        # mode: force_split, minimum_unit

        if max_length < 100:
            raise ValueError(f"max_length must be at least 100, got {max_length}")
        
        minimum_txt_units = re.split(r'[。\n]+', content)
        minimum_txt_units = [unit for unit in minimum_txt_units if unit]
        chunk = ""
        for i, unit_txt in enumerate(minimum_txt_units):
            if len(chunk) + len(unit_txt) < max_length:
                chunk += unit_txt + '\n'
            else:
                # if chunk is empty, then we need to split the unit_txt
                if len(chunk) == 0:
                    if mode == "force_split":
                        return unit_txt[:max_length], unit_txt[max_length:] + "\n" + "\n".join(minimum_txt_units[i+1:])
                    elif mode == "minimum_unit":
                        return unit_txt, "\n".join(minimum_txt_units[i:])
                else:
                    return chunk, "\n".join(minimum_txt_units[i:])
                
        return chunk, ""
    @staticmethod
    def trunc_chapter_by_units(content, num_of_units = 2):

        minimum_txt_units = re.split(r'[。\n]+', content)
        minimum_txt_units = [unit for unit in minimum_txt_units if unit]
        chunk = ""
        for i, unit_txt in enumerate(minimum_txt_units):
            if i < num_of_units:
                chunk += unit_txt + '\n'
            else:
                break
        return chunk, "\n".join(minimum_txt_units[i:])
    
    @staticmethod
    def split_chapter_by_units(content, num_of_units=2, save_dir=None, max_sentence_length=100, min_sentence_length=40):
        # Create Spliter instance
        spliter = Spliter(max_length=max_sentence_length, min_length=min_sentence_length)

        # Split the content into refined sentences
        refined_units = spliter.cut_to_sentences(content)

        # Group sentences into chunks with the specified number of units
        chunks = []
        chunk = ""
        count = 0
        for unit in refined_units:
            if count < num_of_units:
                chunk += unit + '\n'
                count += 1
            else:
                chunks.append(chunk.strip())
                chunk = unit + '\n'
                count = 1
        if chunk:
            chunks.append(chunk.strip())

        # Save chunks if save_dir is provided
        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)
            for i, chunk in enumerate(chunks):
                with open(os.path.join(save_dir, f"chunk_{i}.txt"), 'w', encoding="utf-8") as f:
                    f.write(chunk)

        return chunks


class Script:
    dir : str = None

    def __init__(self, dir):
        self.dir = dir
        self.load_script()

    def load_script(self):
        # list all txt files in the directory
        files = [f for f in os.listdir(self.dir) if f.endswith('.txt')]
        scripts = []
        for f in files:
            with open(os.path.join(self.dir, f), 'r', encoding="utf-8") as file:
                scripts.append(file.read())
        self.scripts = scripts
    
    def __getitem__(self, idx):
        return self.scripts[idx]
    
    def __len__(self):
        return len(self.scripts)
