import aiohttp
import asyncio
import os
import aiofiles
from pydub import AudioSegment
import json
from audiostretchy.stretch import stretch_audio
import yaml

class AudioDownloader:

    def __init__(self, resp_data, target_download_folder, save_name, logger=None):
        self.load_config("vnov/configs/model_config.yaml")
        self._prepare_download_path(target_download_folder, self.audio_format, save_name)
        self.segments = self._parse_segments(resp_data)
        self.logger = logger

    def load_config(self, config_path: str):
        """Load configuration from a YAML file"""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.config = self.config.get("TTS", {})
        self.speed_factor = self.config.get("speed_factor", 1.0)
        self.audio_format = self.config.get("audio_format", "mp3")

    def _prepare_download_path(self, target_download_folder, audio_format, save_name):
        self.target_download_folder = target_download_folder
        self.combined_audio_path = os.path.join(target_download_folder, f"{save_name}.{audio_format}")
        self.temp_audio_folder = os.path.join(target_download_folder, f"{save_name}_temp")
        self.srt_file_path = os.path.join(target_download_folder, f"{save_name}.srt")

        if not os.path.exists(self.target_download_folder):
            raise Exception(f"Save directory {self.target_download_folder} does not exist")
        if not os.path.exists(self.temp_audio_folder):
            os.makedirs(self.temp_audio_folder)

    def _parse_segments(self, data):
        segments = []
        for sect_info in data['data']['sect_infos']:
            text = sect_info.get('text', '')
            segment_id = sect_info.get('segment_id', '')
            audio_url = None
            source_timerange = None
            target_timerange = None

            for elem in sect_info.get('elems', []):
                if elem['elem_type'] == 'tts':
                    audio_url = elem.get('url', '')
                    source_timerange = elem["source_timerange"]
                    target_timerange = elem["target_timerange"]
                    break

            segments.append({
                'segment_id': segment_id,
                'text': text,
                'audio_url': audio_url,
                'source_timerange': source_timerange,
                'target_timerange': target_timerange,
                'ignore_audio': float(source_timerange['start_offset']) - 0.001 > 0.0,
                "audio_path": None
            })

        with open(self.temp_audio_folder + '/segments.json', 'w', encoding='utf-8') as f:
            json.dump(segments, f, indent=4, ensure_ascii=False)

        return segments

    async def _run(self):
        print("Downloading audio segments...")
        await self.download_all_audios()
        print("Combining audio files and generating SRT...")
        await self.combine_audio_segments()

    async def download_audio_for_segment(self, session, segment):
        audio_url = segment['audio_url']
        segment_id = segment['segment_id']
        
        if audio_url:
            try:
                async with session.get(audio_url) as response:
                    if response.status == 200:
                        audio_filename = os.path.join(self.temp_audio_folder, f"{segment_id}.{self.audio_format}")
                        content = await response.read()
                        await self.save_audio_file(audio_filename, content)
                        segment['audio_path'] = audio_filename
                    else:
                        print(f"Failed to download audio for segment {segment_id}, Status: {response.status}")
            except Exception as e:
                print(f"Error downloading audio for segment {segment_id}: {e}")
        else:
            print(f"No audio URL found for segment {segment_id}")

    async def save_audio_file(self, audio_filename, content):
        async with aiofiles.open(audio_filename, 'wb') as f:
            await f.write(content)

    async def download_all_audios(self):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.download_audio_for_segment(session, segment)
                for segment in self.segments if not segment.get('ignore_audio')
            ]
            await asyncio.gather(*tasks)

    def combine_audio(self):
        combined_audio = AudioSegment.empty()
        for segment in self.segments:
            if segment.get('ignore_audio'):
                continue
            audio_segment = self.load_audio(segment)
            if audio_segment:
                # Stretch the audio using the speed_factor before combining
                stretched_audio_path = os.path.join(self.temp_audio_folder, f"stretched_{segment['segment_id']}.{self.audio_format}")
                stretch_audio(segment['audio_path'], stretched_audio_path, self.speed_factor)
                stretched_audio = AudioSegment.from_file(stretched_audio_path, format=self.audio_format)
                
                # Update segment with new duration based on speed_factor
                duration = stretched_audio.duration_seconds
                segment['adjusted_duration'] = duration
                
                combined_audio += stretched_audio
        combined_audio.export(self.combined_audio_path, format=self.audio_format)

    def load_audio(self, segment):
        audio_path = segment.get('audio_path')
        if audio_path and os.path.exists(audio_path):
            if self.audio_format == "mp3":
                return AudioSegment.from_mp3(audio_path)
            elif self.audio_format == "wav":
                return AudioSegment.from_wav(audio_path)
        return None

    def build_srt(self):
        srt_content = []
        current_time = 0.0
        for idx, segment in enumerate(self.segments):
            start_offset = current_time
            end_offset = start_offset + segment.get('adjusted_duration', 0)
            text = segment['text']
            srt_entry = self.generate_srt_entry(idx + 1, start_offset, end_offset, text)
            srt_content.append(srt_entry)
            current_time = end_offset
        return srt_content

    async def combine_audio_segments(self):
        self.combine_audio()
        srt_content = self.build_srt()
        await self.save_srt(srt_content)

    async def save_srt(self, srt_content):
        async with aiofiles.open(self.srt_file_path, 'w') as srt_file:
            await srt_file.write('\n'.join(srt_content))

    def generate_srt_entry(self, index, start_offset, end_offset, text):
        start_time = self.format_time_for_srt(start_offset)
        end_time = self.format_time_for_srt(end_offset)
        return f"{index}\n{start_time} --> {end_time}\n{text}\n"

    def format_time_for_srt(self, offset):
        hours, remainder = divmod(offset, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"
