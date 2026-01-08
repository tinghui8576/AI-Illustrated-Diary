import torch
from langchain_core.prompts import PromptTemplate
from langchain_huggingface.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class StableDiffusionPromptGenerator:
    def __init__(self, model_id="meta-llama/Llama-3.2-1B-Instruct"):
        """Initializes the LLM, tokenizer, and LangChain pipeline."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load Model and Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id).to(self.device)
        
        # Setup HF Pipeline
        self.hf_pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=50, 
            temperature=0.5,
            pad_token_id=self.tokenizer.eos_token_id, 
            device=0 if self.device == "cuda" else -1
        )
        
        # Setup LangChain LLM Wrapper and the Prompt Template
        self.llm = HuggingFacePipeline(pipeline=self.hf_pipeline)
        
        self.template = """
        You are an AI image prompt generator for Stable Diffusion.

        Instructions:
        - Use only the Scene Objects & Actions provided; do NOT invent new objects or actions.
        - Based on the Mood and Style, invent visual style attributes: art medium, brush/texture, lighting, color, and emotional tone.
        - Combine Scene Objects & Actions with the visual style into a SINGLE-LINE AI image prompt.
        - Do not include explanations or extra text.

        ### Inputs:
        Scene Objects & Actions: {scene}
        Mood: {mood}
        Style: {style}

        ### Output:
        """
        self.prompt_template = PromptTemplate(
            input_variables=["scene", "mood", "style"],
            template=self.template
        )
        
        self.sd_chain = self.prompt_template | self.llm

    def generate_prompt(self, scene: str, mood: str, style: str, max_retries: int = 3) -> str:
        """Generates prompt with a retry mechanism if validation fails."""
        input_data = {"scene": scene, "mood": mood, "style": style}
        
        for attempt in range(max_retries):
            raw_output = self.sd_chain.invoke(input_data)
            
            if "### Output:" in raw_output:
                content = raw_output.split("### Output:")[-1].strip()
                
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                if lines:
                    final_prompt = lines[0]
                    print(f"✅ Success on attempt {attempt + 1}")
                    return final_prompt
            
            print(f"⚠️ Attempt {attempt + 1} failed validation. Retrying...")

        return "Error: Could not generate a valid prompt after multiple retries."
