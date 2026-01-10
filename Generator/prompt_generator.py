import torch
from langchain_core.prompts import PromptTemplate
from langchain_huggingface.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class PromptGenerator:
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
            max_new_tokens=60, 
            temperature=0.5,
            pad_token_id=self.tokenizer.eos_token_id, 
            device=0 if self.device == "cuda" else -1
        )
        
        # Setup LangChain LLM Wrapper and the Prompt Template
        self.llm = HuggingFacePipeline(pipeline=self.hf_pipeline)
        
        self.template = """
        You are an AI image prompt generator for Stable Diffusion.

        CRITICAL RULES:
        - Use ONLY the Scene Objects & Actions provided. Do NOT invent or add any new objects, people, animals, or locations.
        - Retrieved Memory is for STYLE INFLUENCE ONLY. Never copy objects, actions, or locations from memory.
        - Based on Mood, Style, and Retrieved Memory, invent visual style attributes: art medium, brush or texture, lighting, color palette, emotional tone.
        - Combine the Scene Objects & Actions with the visual style into a SINGLE-LINE Stable Diffusion prompt.
        - Output ONE line only with 40 words. 
        - No Explanations.

        ### Inputs
        Scene Objects & Actions:{scene}
        Retrieved Memory:{memory}
        Mood:{mood}
        Style:{style}

        ### Output
        """

        self.prompt_template = PromptTemplate(
            input_variables=["scene", "memory", "mood", "style"],
            template=self.template
        )
        
        self.sd_chain = self.prompt_template | self.llm

    def generate_prompt(self, scene: str, memory: str, mood: str, style: str, max_retries: int = 3) -> str:
        """Generates prompt with a retry mechanism if validation fails."""
        input_data = {"scene": scene, "memory": memory, "mood": mood, "style": style}
        
        for attempt in range(max_retries):
            raw_output = self.sd_chain.invoke(input_data)
            if "### Output" in raw_output:
                content = raw_output.split("### Output")[-1].strip()
                
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                if lines:
                    final_prompt = lines[0]
                    print(f"✅ Success on attempt {attempt + 1}")
                    return final_prompt
            
            print(f"⚠️ Attempt {attempt + 1} failed validation. Retrying...")

        return "Error: Could not generate a valid prompt after multiple retries."
