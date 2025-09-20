from src.core.providers import EmbeddingManager, LlmModel

class Factory:
    def __init__(self) -> None:
        self.__embeder_model = None
        self.__llm_model = None
        
    def get_embedding_model(self):
        if self.__embeder_model is None:
            embedding_model = EmbeddingManager()
            self.__embeder_model = embedding_model.get_embedding_model()
        
        return self.__embeder_model
    
    def get_llm_model(self):
        if self.__llm_model is None:
            llm_model = LlmModel()
            self.__llm_model = llm_model.get_llm_model()

        return self.__llm_model