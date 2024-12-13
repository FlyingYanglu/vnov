from vnov.role import Role
from vnov.llms.base import BaseLLM
from vnov.data.data import Novel
import asyncio
import os
import pathlib
import json
import time


class TTS(Role):

    def __init__(self, model: BaseLLM, **kwargs):
        super().__init__(model, **kwargs)
        self.role = "TTS"


    async def generate(self, novel: Novel, mode="refined", **kwargs):
        scene_count = 0
        if mode == "refined":
            refined_scripts = novel.load_files(mode="refined")
            for script in refined_scripts:
                content = script["content"]
                fpath = script["fpath"]
                # convert fpath to PATH object
                save_name = pathlib.Path(fpath).stem
                print(f"Generating TTS for {save_name}")
                save_dir = novel.get_dir("tts")
                resp_data = await self.model(content, save_dir, save_name)

        elif mode == "storyboard":
            storyboards = novel.load_files(mode="storyboard", extension="json")
            #filter out those that does not have word "storyboard" in filename stored under "fpath"
            for storyboard in storyboards:
                content = storyboard["content"]
                fpath = storyboard["fpath"]
                print(fpath)
                if "storyboard" not in pathlib.Path(fpath).stem:
                    continue
                # convert fpath to PATH object
                save_dir = novel.get_dir("tts")
                # convert to json
                content = json.loads(content)
                for scene in content:
                    script = scene["text"]
                    print(script)
                    save_name = f"scene_{scene_count}"
                    print(f"Generating TTS for {save_name}")
                    resp_data = await self.model(script, save_dir, save_name)
                    scene_count += 1
                    time.sleep(2)
                    
                # resp_data = await self.model(content, save_dir, save_name)




    


            
