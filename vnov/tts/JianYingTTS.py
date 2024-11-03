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
    def __init__(self, start_time: float = 0, end_time: float = 6000, tdid: str = '2804213176076372'):
        self.start_time = start_time
        self.end_time = end_time
        self.tdid = tdid  # Make tdid adjustable
        self.set_up_logger()
        # self.audio_processor = AudioProcessor(speed_factor=self.speed_factor)



    def set_up_logger(self):
        """Set up logger"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        file_handler = logging.FileHandler("tts.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        self.logger.propagate = False

    def generate_sign(self, url: str, pf: str = '4', appvr: str = '6.6.0') -> Tuple[str, str]:
        """Generate signature and timestamp."""
        current_time = str(int(time.time()))
        sign_str = f"9e2c|{url[-7:]}|{pf}|{appvr}|{current_time}|{self.tdid}|11ac"  # Use instance's tdid
        sign = hashlib.md5(sign_str.encode()).hexdigest()
        return sign.lower(), current_time

    def build_headers(self, device_time: str, sign: str) -> Dict[str, str]:
        """Build headers for requests"""
        return {
            'User-Agent': "Cronet/TTNetVersion:d4572e53 2024-06-12 QuicVersion:4bf243e0 2023-04-17",
            'appvr': "6.6.0",
            'device-time': device_time,
            'pf': "4",
            'sign': sign,
            'sign-ver': "1",
            'tdid': self.tdid,  # Use instance's tdid
        }

    def submit(self, article_content: str) -> Tuple[str, dict]:
        """Submit the task to generate TTS"""
        url = "https://lv-pc-api-sinfonlinec.ulikecam.com/lv/v1/text_to_video/submit_generate_video_task"
        payload = {
            "article_content": article_content,
            "article_title": "",
            "mode": 1,
            "only_gif": False,
            "only_tts": True,
            "speech_reader": "BV411_streaming"
        }

        sign, device_time = self.generate_sign(url)
        headers = self.build_headers(device_time, sign)

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code != 200 or 'data' not in response_data:
            self.logger.error("Failed to submit task: " + response.text)
            raise ValueError("Submission failed")

        query_id = response_data['data']['event_id']
        query_config = response_data['data']['query_config']
        self.logger.info(f"Query ID: {query_id}")
        self.logger.info(f"Query Config: {query_config}")
        return query_id, query_config

    def query(self, query_id: str) -> dict:
        """Query the task's status"""
        
        logging.info(f"Querying ID: {query_id}")
        url = "https://lv-pc-api-sinfonlinec.ulikecam.com/lv/v1/text_to_video/query_generate_video_task"
        payload = {"event_id": query_id}
        sign, device_time = self.generate_sign(url)
        headers = self.build_headers(device_time, sign)

        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    async def query_with_config(self, query_id: str, query_config: dict) -> dict:
        """Query the task with retry logic"""
        max_retries = query_config.get('max_retry_times', 5)
        retry_interval = query_config.get('retry_interval', 2)
        logging.info(f"Querying Max retries: {max_retries}, Retry interval: {retry_interval}")

        for attempt in range(max_retries):
            await asyncio.sleep(retry_interval)
            result = self.query(query_id)
            if result['ret'] == "0":
                self.logger.info("Task completed successfully.")
                return result
            self.logger.info(f"Attempt {attempt + 1}/{max_retries} failed.")
        
        raise TimeoutError("Task query timed out.")

    async def _run(self, article_content: str, save_dir: str, save_name: str):
        """Run the full TTS generation task"""
        logging.info("Starting TTS task...")
        query_id, query_config = self.submit(article_content)
        logging.info(f"Task submitted with ID: {query_id}")
        response_data = await self.query_with_config(query_id, query_config)
        
        downloader = AudioDownloader(response_data, save_dir, save_name)
        
        await downloader._run()

        
        logging.info("TTS task completed.")
        
        return response_data

    async def __call__(self, article_content: str, save_dir: str, save_name: str):
        """Execute TTS task with provided article content"""
        return await self._run(article_content, save_dir, save_name)


if __name__ == '__main__':
    tts = JianYingTTS(tdid="2804213176076372")
    text_content = "那天我上了他的当，他说他会给我一份工作，我就跟他走了。"
    resp_data = asyncio.run(tts(text_content, save_dir="tts_output", save_name="test"))
