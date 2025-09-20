from groq import Groq
import os

class LlmModel:
    def __init__(self):
        self.model = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
    
    def get_llm_model(self):
        return self.model