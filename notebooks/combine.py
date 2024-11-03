import os
import natsort
import subprocess

if __name__ == "__main__":
    # Set the absolute path to the folder containing videos
    video_folder = os.path.abspath('datasets/yujie/videos')

    # Absolute path where filelist.txt will be saved
    filelist_path = os.path.abspath('datasets/yujie/filelist.txt')

    # Get a list of all .mp4 files in the folder
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]

    # Sort the files in natural order
    sorted_videos = natsort.natsorted(video_files)

    # Create the filelist.txt file with absolute paths for each video
    with open(filelist_path, 'w') as filelist:
        for video in sorted_videos:
            filelist.write(f"file '{os.path.join(video_folder, video)}'\n")

    print(f"filelist.txt created successfully at {filelist_path}.")

    # Define the FFmpeg command to concatenate videos using absolute path to filelist.txt
    ffmpeg_command = [
        'ffmpeg', '-f', 'concat', '-safe', '0', '-i', filelist_path, '-c', 'copy', 'output.mp4'
    ]

    # Run the FFmpeg command using subprocess
    try:
        subprocess.run(ffmpeg_command, check=True)
        print("Videos concatenated successfully into output.mp4.")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg command failed: {e}")
