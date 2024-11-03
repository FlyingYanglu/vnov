import json
import threading
import os
from concurrent.futures import ThreadPoolExecutor
import time
import random
from vnov.image_generation.midjourney import Midjourney
from vnov.data.data import NOVEL_MODE
class ImageGenerationPipeline:
    def __init__(self, novel, taotao_url="https://s.mj.run/qRhIa9TaD5Q"):
        """
        Initialize the pipeline with the novel instance and taotao reference URL.

        Args:
            novel (Novel): Instance of the Novel class.
            taotao_url (str): URL reference for taotao character.
        """
        self.novel = novel
        self.taotao_url = taotao_url
        self.mj_prompts = novel.get_mj_prompts()
        self.storyboard = novel.get_storyboard()
        self.char_to_url = novel.get_char_to_url()
        self.scene_to_url = [None for _ in self.storyboard]
        self.char_to_url_lock = threading.Lock()
        self.scene_to_url_lock = threading.Lock()
        self.img_dir = novel.get_dir(NOVEL_MODE.SCENE_IMAGES)

    def process_scene(self, i, multithread=True, save_every=5):
        """Process a scene and generate the corresponding image."""
        if self.scene_to_url[i] is not None:
            return
        
        mj = Midjourney()
        if multithread:
            time.sleep(random.uniform(1, 10))
        prompt = "anime episode still image: " + self.mj_prompts[i] + ", anime, japanese manga style. Art by Kohei Horikoshi."
        scene_info = self.storyboard[i]
        characters = [item['名字'] for item in scene_info['角色']]
        print(f"Setting up scene {i}")

        if len(characters) == 1 and characters[0] in self.char_to_url:
            char_url = self.char_to_url[characters[0]][0] # pick the first one from the four images
            if not char_url.startswith("https://s.mj.run/"):
                urls = mj.fetch_image(prompt, image_folder=self.img_dir, 
                                      image_name=f'scene{i}', cref=char_url, cw=20, 
                                      sref=self.taotao_url, sw=45, niji=True, need_new_ref_url=True)
                with self.char_to_url_lock:
                    self.char_to_url[characters[0]][0] = urls['cref_url']
                    print(f"Updated char_to_url for character: {characters[0]}")
            else:
                urls = mj.fetch_image(prompt, image_folder=self.img_dir, 
                                      image_name=f'scene{i}', cref=char_url, cw=20, 
                                      sref=self.taotao_url, niji=True, sw=45)
            url = urls['image_url']
        else:
            urls = mj.fetch_image(prompt, image_folder=self.img_dir, 
                                  image_name=f'scene{i}', sref=self.taotao_url, niji=True, sw=200)
            url = urls['image_url']

        with self.scene_to_url_lock:
            self.scene_to_url[i] = url
        print(f"Processed scene {i}")

        if i % save_every == 0:
            self.save_progress()

    def save_progress(self):
        """Save progress of scene and character URL mappings."""
        with self.scene_to_url_lock:
            with open(os.path.join(self.img_dir, "scene_to_url.json"), "w", encoding="utf-8") as f:
                json.dump(self.scene_to_url, f, indent=4, ensure_ascii=False)

        with self.char_to_url_lock:
            with open(os.path.join(self.img_dir, "char_to_url.json"), "w", encoding="utf-8") as f:
                json.dump(self.char_to_url, f, indent=4, ensure_ascii=False)
        
    def generate_images(self, multithread=True):
        """
        Generate images for all scenes.
        
        Parameters:
        multithread (bool): If True, uses multithreading for concurrent image generation.
                            If False, processes scenes one by one (single-threaded).
        """
        if multithread:
            # Multithreading mode
            with ThreadPoolExecutor(max_workers=3) as executor:
                executor.map(self.process_scene, range(len(self.scene_to_url)))
        else:
            # Single-threaded mode
            for i in range(len(self.scene_to_url)):
                if self.scene_to_url[i] is None:
                    self.process_scene(i, multithread=False)

        self.save_progress()
        

    def regenerate_missing_images(self, multithread=True):
        """
        Regenerate missing images for scenes where the URL is None.
        
        Parameters:
        multithread (bool): If True, uses multithreading for concurrent image generation.
                            If False, processes missing images one by one (single-threaded).
        """
        self.reload_scene_to_url()
        missing_indices = [i for i, url in enumerate(self.scene_to_url) if url is None]
        
        if len(missing_indices) <= 0:
            return

        if multithread:
            # Multithreading mode
            with ThreadPoolExecutor(max_workers=3) as executor:
                executor.map(lambda i: self.process_scene(i, multithread=True, save_every=1), missing_indices)
        else:
            # Single-threaded mode
            for i in missing_indices:
                self.process_scene(i, multithread=False, save_every=1)
        
        self.save_progress()
        

    def reload_scene_to_url(self):
        """Reload the scene_to_url file."""
        with open(os.path.join(self.img_dir, "scene_to_url.json"), "r", encoding="utf-8") as f:
            self.scene_to_url = json.load(f)
