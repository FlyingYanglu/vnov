from vnov.tts import TTS
from vnov.data import Novel


if __name__ == "__main__":
    tts = TTS()
    novel = Novel( "datasets/yujie", "史金")
    tts.generate_tss(novel, start_scene=582)
