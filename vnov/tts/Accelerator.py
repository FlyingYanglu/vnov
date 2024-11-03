import librosa
import soundfile as sf

class AudioProcessor:
    def __init__(self, speed_factor=1.0):
        self.audio_data = None
        self.sample_rate = None
        self.speed_factor = speed_factor

    # Load the audio file
    def load_audio(self, file_path):
        self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
        return self.audio_data, self.sample_rate

    # Change the tempo without affecting the pitch
    def change_tempo(self, speed_factor):
        if self.audio_data is None:
            raise ValueError("Audio data not loaded. Call load_audio() first.")

        # Compute the STFT (Short-Time Fourier Transform)
        stft = librosa.stft(self.audio_data)
        # Apply time-stretching using phase vocoder
        stretched_stft = librosa.phase_vocoder(stft, rate=speed_factor)
        # Convert back to the time-domain signal
        adjusted_audio = librosa.istft(stretched_stft)
        return adjusted_audio

    # Save the adjusted audio
    def save_audio(self, audio_data, output_path):
        if self.sample_rate is None:
            raise ValueError("Sample rate not set. Load the audio first.")
        sf.write(output_path, audio_data, self.sample_rate)

    # __call__ method to run the entire process in one call
    def __call__(self, file_path, output_file_name=None, speed_factor=None):
        if speed_factor is None:
            speed_factor = self.speed_factor
        if output_file_name is None:
            output_file_name = file_path
        self.load_audio(file_path)
        adjusted_audio = self.change_tempo(speed_factor)
        self.save_audio(adjusted_audio, output_file_name)

# Usage example
if __name__ == "__main__":
    processor = AudioProcessor()
    input_file = 'yujie_tts_0.MP3'  # Replace with your input file path
    output_file = 'yujie_tts_0_15.MP3'  # Replace with your output file path
    speed_factor = 1.5  # 1.5x speed up; change as needed

    # Use the __call__ method to process the audio
    processor(input_file, output_file, speed_factor)
