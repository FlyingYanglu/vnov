import datetime
import hashlib
import json
import logging
import time
import requests
import asyncio
from typing import Dict, Tuple

# Assuming AudioDownloader is already imported
from vnov.tts.DownloadUtils import AudioDownloader
# from vnov.tts.Accelerator import AudioProcessor
import os
import yaml

class JianYingTTS:
    def __init__(self, start_time: float = 0, end_time: float = 6000):
        self.start_time = start_time
        self.end_time = end_time
        self.set_up_logger()
        # self.audio_processor = AudioProcessor(speed_factor=self.speed_factor)
        #load config
        self.config = self.load_config()
        self.tdid = self.config['tdid']
        self.host = self.config["Host"]
        


    def load_config(self, config_path: str = "./vnov/configs/model_config.yaml") -> dict:
        """Load configuration from yaml file"""
        with open(config_path) as file:
            config = yaml.safe_load(file)

        config = config['CapCut']
        return config

    def set_up_logger(self):
        """Set up logger"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        file_handler = logging.FileHandler("tts.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        self.logger.propagate = False

    def generate_sign(self, url: str) -> Tuple[str, str]:
        """Generate signature and timestamp."""
        current_time = str(int(time.time()))
        sign_str = f"9e2c|{url[-7:]}|{self.config['pf']}|{self.config['appvr']}|{current_time}|{self.tdid}|11ac"  # Use instance's tdid
        # print(sign_str)
        sign = hashlib.md5(sign_str.encode()).hexdigest()
        return sign.lower(), current_time

    def build_headers(self, device_time: str, sign: str) -> Dict[str, str]:
        """Build headers for requests"""
        # print(self.config)
        return {
            'appvr': self.config['appvr'],
            'device-time': device_time,
            'pf': self.config['pf'],
            'sign': sign,
            'sign-ver': self.config['sign-ver'],
            'tdid': self.tdid,  # Use instance's tdid
            'User-Agent': self.config['User-Agent'],
        }


    def submit(self, article_content: str) -> Tuple[str, dict]:
        """Submit the task to generate TTS"""
        url = f"https://{self.host}/lv/v1/text_to_video/submit_generate_video_task"
        payload = {
            "article_content": article_content,
            "article_title": "",
            "mode": 1,
            "only_gif": False,
            "only_tts": True,
            "speech_reader": "BV127_streaming"
        }

        sign, device_time = self.generate_sign(url)
        headers = self.build_headers(device_time, sign)

        # print(payload)
        # print(headers)
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code != 200 or 'data' not in response_data:
            self.logger.error("Failed to submit task: " + response.text)
            raise ValueError("Submission failed")

        query_id = response_data['data']['event_id']
        task_sign = response_data['data'].get('task_sign', None)
        query_config = response_data['data']['query_config']
        self.logger.info(f"Query ID: {query_id}")
        self.logger.info(f"Query Config: {query_config}")
        # print(query_config)
        return query_id, task_sign, query_config

    def query(self, query_id: str, task_sign: str = None) -> dict:
        """Query the task's status"""
        
        logging.info(f"Querying ID: {query_id}")
        url = f"https://{self.host}/lv/v1/text_to_video/query_generate_video_task"
        payload = {"event_id": query_id}
        if task_sign:
            payload['task_sign'] = task_sign
        sign, device_time = self.generate_sign(url)
        headers = self.build_headers(device_time, sign)
        # print(headers)

        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    async def query_with_config(self, query_id: str, query_config: dict, task_sign: str=None) -> dict:
        """Query the task with retry logic"""
        max_retries = query_config.get('max_retry_times', 5)
        query_interval = query_config.get('query_interval', 5)
        retry_interval = query_config.get('retry_interval', 2)
        logging.info(f"Querying Max retries: {max_retries}, Retry interval: {retry_interval}")

        for attempt in range(max_retries):
            if attempt == 0:
                await asyncio.sleep(query_interval)
            else:
                await asyncio.sleep(retry_interval)
            result = self.query(query_id, task_sign)
            # print(result)
            if result['ret'] == "0":
                self.logger.info("Task completed successfully.")
                return result
            self.logger.info(f"Attempt {attempt + 1}/{max_retries} failed.")
        raise TimeoutError("Task query timed out.")

    async def _run(self, article_content: str, save_dir: str, save_name: str):
        """Run the full TTS generation task"""
        logging.info("Starting TTS task...")
        query_id, task_sign, query_config = self.submit(article_content)
        logging.info(f"Task submitted with ID: {query_id}")
        response_data = await self.query_with_config(query_id, query_config, task_sign)
        
        downloader = AudioDownloader(response_data, save_dir, save_name)
        
        await downloader._run()

        
        logging.info("TTS task completed.")
        
        return response_data

    async def __call__(self, article_content: str, save_dir: str, save_name: str):
        """Execute TTS task with provided article content"""
        return await self._run(article_content, save_dir, save_name)


# if __name__ == '__main__':
#     tts = JianYingTTS(tdid="2804213176076372")
#     text_content = "那天我上了他的当，他说他会给我一份工作，我就跟他走了。"
#     resp_data = asyncio.run(tts(text_content, save_dir="tts_output", save_name="test"))
