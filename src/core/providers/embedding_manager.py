import os

class EmbeddingManager:
    def __init__(self):
        self.hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models/microsoft/codebert-base"
        
    def get_embedding_model(self):
        embed_model = {
            "name": "codebert-base",
            "url": self.base_url,
            "token": self.hf_token
        }
        
        return embed_model
