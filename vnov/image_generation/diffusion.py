import torch
from diffusers import DiffusionPipeline
from diffusers import StableDiffusionXLPipeline, StableDiffusionPipeline
from compel import Compel, ReturnedEmbeddingsType

from vnov.configs.config import MODEL_CONFIG
import os

class Diffusion:

    def __init__(self, model_name=MODEL_CONFIG["Diffusion"]["model_name"], 
                 model_path=MODEL_CONFIG["Diffusion"]["model_path"], **kargs):
        if model_path and os.path.exists(model_path):
            self.pipe = StableDiffusionXLPipeline.from_single_file(model_path)
        else:
            self.pipe = DiffusionPipeline.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16, 
                    use_safetensors=True, 
                )
        self.pipe.to("cuda")
    
    def generate(self, prompt, negative_prompt, **kwargs):
        image = self.pipe(
            prompt, 
            negative_prompt=negative_prompt,
            width=1344,
            height=768, 
            guidance_scale=7,
            num_inference_steps=28,
            **kwargs
        ).images[0]
        return image
    
    def encode_prompts(self, prompt, negative_prompt):
        compel = Compel(tokenizer=[self.pipe.tokenizer, self.pipe.tokenizer_2], 
                        text_encoder=[self.pipe.text_encoder, self.pipe.text_encoder_2], 
                        returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED, 
                        requires_pooled=[False, True],
                        truncate_long_prompts=False)
        conditioning, pooled = compel(prompt)
        negative_conditioning, negative_pooled = compel(negative_prompt)
        prompt_embeds, negative_prompt_embeds = compel.pad_conditioning_tensors_to_same_length(
            [conditioning, negative_conditioning])
        pooled_prompt_embeds, negative_pooled_prompt_embeds = compel.pad_conditioning_tensors_to_same_length(
            [pooled, negative_pooled])
        return prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds.squeeze(0), negative_pooled_prompt_embeds.squeeze(0), 

    def advanced_generate(self, prompt, negative_prompt, **kwargs):
        num_images_per_prompt = kwargs.get("num_images_per_prompt", 1)
        seed = kwargs.get("seed", -1)
        width = kwargs.get("width", 1344)
        height = kwargs.get("height", 768)
        guidance_scale = kwargs.get("guidance_scale", 7)
        num_inference_steps = kwargs.get("num_inference_steps", 28)

        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = \
            self.encode_prompts(prompt=prompt, negative_prompt=negative_prompt )
        print(prompt_embeds.shape, negative_prompt_embeds.shape, pooled_prompt_embeds.shape, negative_pooled_prompt_embeds.shape)
        new_img = self.pipe(
            prompt_embeds = prompt_embeds,
            negative_prompt_embeds = negative_prompt_embeds,
            pooled_prompt_embeds = pooled_prompt_embeds,
            negative_pooled_prompt_embeds = negative_pooled_prompt_embeds,
            width=width,
            height=height, 
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            num_images_per_prompt = num_images_per_prompt,
            generator = torch.manual_seed(seed) if seed != -1 else None,
        ).images
        return new_img
    
    def save_image(self, image, filename):
        image.save(filename)

