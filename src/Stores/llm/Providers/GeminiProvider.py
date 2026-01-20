import logging
from google import genai

from ..LLMInterface import LLMInterface
from ..LLMEnums import DocumentTypeEnum, GeminiEnums
from typing import List ,Union

class GeminiProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        default_input_max_characters: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ):
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.enums=GeminiEnums
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = genai.Client(api_key=self.api_key)
        # Stateful chat session (initialized lazily on first generate_text call)
        self.chat = None

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[: self.default_input_max_characters].strip()

    def generate_text(
        self,
        prompt: str,
        chat_history: list = [],
        max_output_tokens: int = None,
        temperature: float = None,
    ):
        if not self.generation_model_id:
            self.logger.error("Generation model for Gemini was not set")
            return None

        try:
            # Initialize chat session on first use
            if self.chat is None:
                self.chat = self.client.chats.create(
                    model=self.generation_model_id
                )

            # Send message using stateful chat (history managed automatically)
            response = self.chat.send_message(
                self.process_text(prompt)
            )

            if not response or not getattr(response, "text", None):
                self.logger.error("Error while generating text with Gemini")
                return None

            return response.text
        except Exception as e:
            self.logger.error(f"Gemini generate_text error: {e}")
            return None

    def embed_text(self, text: Union[str, List[str]], document_type: str = None):
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Gemini was not set")
            return None
        if isinstance(text, str):
            text = [text]

        try:
            resp = self.client.models.embed_content(
                model=self.embedding_model_id,
                contents=[self.process_text(t) for t in text],
            )

            embedding = None
            # New google genai client typically returns `data` list with `embedding.values`
            if hasattr(resp, "data") and resp.data:
                item = resp.data[0]
                emb = getattr(item, "embedding", None)
                if emb is not None:
                    embedding = getattr(emb, "values", None)
            # Fallbacks
            if embedding is None and hasattr(resp, "embeddings") and resp.embeddings:
                emb = resp.embeddings[0]
                embedding = getattr(emb, "values", None)
            if embedding is None and hasattr(resp, "embedding"):
                emb = resp.embedding
                embedding = getattr(emb, "values", None)

            if not embedding:
                self.logger.error("Error while embedding text with Gemini")
                return None
            return [c for c in embedding]
        except Exception as e:
            self.logger.error(f"Gemini embed_text error: {e}")
            return None

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": prompt,
        }
