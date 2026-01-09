import torch
from diffusers import StableDiffusionPipeline

class ImageGenerator:
    def __init__(self, model_id="sd-legacy/stable-diffusion-v1-5"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        self.pipe.to(self.device)
        self.pipe.safety_checker = None

    def paint(self, prompt, num_images=2):
        negative_prompt = "blurry, low quality, distorted, extra limbs, text"
        
        result = self.pipe(
            prompt=[prompt] * num_images,
            negative_prompt=[negative_prompt] * num_images,
            num_inference_steps=20,
            guidance_scale=7.5
        )
        return result.images

