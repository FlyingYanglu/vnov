import PIL.Image as pil
import moviepy.editor as mp
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
import os
import re
from moviepy.config import change_settings

from glob import glob
import natsort
import re
import random
import multiprocessing

import moviepy.editor as mp
from moviepy.editor import TextClip



pil.ANTIALIAS = pil.Resampling.LANCZOS
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})
def parse_srt(srt_file, encoding="utf-8"):
    """Parses the SRT file into a list of (start_time, end_time, subtitle_text) tuples."""
    pattern = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")
    subtitles = []

    with open(srt_file, 'r', encoding=encoding) as f:
        lines = f.readlines()

    current_sub = {}
    for line in lines:
        # Match time codes
        if pattern.search(line):
            times = pattern.findall(line)
            start_time = int(times[0][0]) * 3600 + int(times[0][1]) * 60 + int(times[0][2]) + int(times[0][3]) / 1000
            end_time = int(times[1][0]) * 3600 + int(times[1][1]) * 60 + int(times[1][2]) + int(times[1][3]) / 1000
            current_sub['start'] = start_time
            current_sub['end'] = end_time
        elif line.strip() == '':
            if 'text' in current_sub:
                # Remove prefix numbers and keep only the subtitle text
                text = re.sub(r'^\d+\s*', '', current_sub['text'].strip())
                subtitles.append((current_sub['start'], current_sub['end'], text))
            current_sub = {}
        else:
            if 'text' not in current_sub:
                current_sub['text'] = line.strip()
            else:
                current_sub['text'] += ' ' + line.strip()
    
    return subtitles


def create_video_with_audio_and_subtitles(image_file, audio_file, subtitle_file, output_file, direction=0):

    # direction: 0 for top to bottom, 1 for bottom to top

    # Load the audio
    audio = mp.AudioFileClip(audio_file)
    
    # Load the image
    image_clip = mp.ImageClip(image_file).set_duration(audio.duration)  # Set the duration to match audio

    # Resize the image to maintain a 16:9 aspect ratio (1920x1080) while preserving its aspect ratio
    target_width = 12/9*1080 // 1
    target_height = 1080
    image_clip = image_clip.resize(height=target_width)  # Set height to 1920x1920

    # Create a video clip with zooming and vertical panning effect
    def make_frame(t):
        if direction == 0:
            # Pan from top to bottom
            y_offset = (image_clip.h - target_height) * (t / audio.duration)  # Calculate vertical pan offset
        else:
            # Pan from bottom to top
            y_offset = (image_clip.h - target_height) * (1 - t / audio.duration)

        frame = image_clip.set_position(('center', 'top')).get_frame(t)
        return frame[int(y_offset):int(y_offset + target_height), :, :]

    # Create a video clip with the zoom and vertical panning effect
    video_clip = mp.VideoClip(make_frame, duration=audio.duration)

    # Set the audio for the video clip
    video_clip = video_clip.set_audio(audio)

    # Parse the subtitles manually
    subtitles = parse_srt(subtitle_file)

    # Create TextClip objects for each subtitle and overlay them
    subtitle_clips = []
    for start, end, text in subtitles:
        # Use the specified custom font
        txt_clip = TextClip(text, font='./datasets/simyou.ttf', fontsize=40, color='white')
        txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(start).set_duration(end - start)
        subtitle_clips.append(txt_clip)

    # Composite the video and subtitles
    final_video = mp.CompositeVideoClip([video_clip] + subtitle_clips)
    final_video = final_video.subclip(0, min(audio.duration, video_clip.duration)- 0.1)
    # Export the final video
    final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac', preset='fast')

def process_video_task(mp3_folder, output_folder):
    index = re.search(r'\d+', mp3_folder).group()
    image_file = f"datasets/yujie/scene_images/scene{index}.png"
    audio_file = f"{mp3_folder}yujie_tts_{index}.mp3"
    subtitle_file = f"{mp3_folder}yujie_tts_{index}.srt"
    output_file = f"{output_folder}{index}.mp4"
    direction = random.choice([0, 1])
    
    create_video_with_audio_and_subtitles(image_file, audio_file, subtitle_file, output_file, direction=direction)
    print(f"Created video {output_file}")

# Use multiprocessing to generate videos in parallel
if __name__ == "__main__":

    all_mp3_folders = glob("datasets/yujie/yujie_n/*_tts_*/")
    all_mp3_folders = natsort.natsorted(all_mp3_folders)
    output_folder = "datasets/yujie/videos/"
    pool = multiprocessing.Pool(processes=4)  # Adjust '4' to the number of available CPU cores
    pool.starmap(process_video_task, [(mp3_folder, output_folder) for mp3_folder in all_mp3_folders])
    pool.close()
    pool.join()
