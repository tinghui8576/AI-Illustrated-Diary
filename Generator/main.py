from Generator.prompt_generator import PromptGenerator
from Generator.image_generator import ImageGenerator

class LLMsManager:
    def __init__(self, text_model_id="meta-llama/Llama-3.2-1B-Instruct", image_model_id="sd-legacy/stable-diffusion-v1-5"):
        print("--- Initializing Systems ---")
        self.brain = PromptGenerator(text_model_id)
        self.artist = ImageGenerator(image_model_id)

    def create_image_from_diary(self, scene, mood, style, num_images=2):
        print(f"\n🧠 Thinking about: {scene}...")
        refined_prompt = self.brain.generate_prompt(
            scene=scene,
            mood=mood,
            style=style)
        
        print(f"🎨 Painting: {refined_prompt}")
        images = self.artist.paint(refined_prompt, num_images)
        
        return images, refined_prompt