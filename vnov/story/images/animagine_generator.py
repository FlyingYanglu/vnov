from vnov.image_generation.diffusion import Diffusion
from vnov.data import Novel
import os
import tqdm
NEGATIVE_PROMPT = "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name"

class AnimagineGen:
    def __init__(self):
        self.diffusion = Diffusion()


    def generate(self, prompt, negative_prompt=NEGATIVE_PROMPT, **kwargs):
        return self.diffusion.advanced_generate(prompt, negative_prompt, **kwargs)
    

    def generate_all_images(self, novel:Novel, num_images=None, **kwargs):
        prompts = novel.load_prompts(generator="animagine")
        image_path = os.path.join(novel.dir, "animagine_images")
        os.makedirs(image_path, exist_ok=True)
        if num_images is None:
            num_images = len(prompts)
        for i, prompt in tqdm.tqdm(enumerate(prompts[:num_images])):
            image = self.generate(prompt, **kwargs)[0]
            self.diffusion.save_image(image, os.path.join(image_path, f"{i}.png"))
    