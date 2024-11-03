from vnov.role import Role
from vnov.llms.base import BaseLLM
from vnov.data.data import Novel
import asyncio
import os
import pathlib


class TTS(Role):

    def __init__(self, model: BaseLLM, **kwargs):
        super().__init__(model, **kwargs)
        self.role = "TTS"


    async def generate(self, novel: Novel, **kwargs):
        refined_scripts = novel.load_files(mode="refined")
        for script in refined_scripts:
            content = script["content"]
            fpath = script["fpath"]
            # convert fpath to PATH object
            save_name = pathlib.Path(fpath).stem
            print(f"Generating TTS for {save_name}")
            save_dir = novel.get_dir("tts")
            resp_data = await self.model(content, save_dir, save_name)


    


            
