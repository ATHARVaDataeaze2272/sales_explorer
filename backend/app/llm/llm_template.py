import os
import logging
import google.generativeai as genai
from openai import OpenAI

logger = logging.getLogger(__name__)

class BaseLLM:
    """Base class for all LLM implementations."""
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement this method")


# ---------------- GEMINI ---------------- #
class GeminiLLM(BaseLLM):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY environment variable.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            return "No response from Gemini model."
        except Exception as e:
            logger.error(f"❌ Gemini Error: {e}")
            return f"Error: {e}"


# ---------------- OPENAI ---------------- #
class OpenAILLM(BaseLLM):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"❌ OpenAI Error: {e}")
            return f"Error: {e}"


# ---------------- QWEN ---------------- #
class QwenLLM(BaseLLM):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        import dashscope
        self.model_name = model_name
        self.client = dashscope.Generation()

    def generate(self, prompt: str) -> str:
        try:
            result = self.client.call(model=self.model_name, prompt=prompt)
            return result.output.text.strip()
        except Exception as e:
            logger.error(f"❌ Qwen Error: {e}")
            return f"Error: {e}"


# ---------------- NVIDIA ---------------- #
class NvidiaLLM(BaseLLM):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        import nvidia_genai as ng
        self.client = ng.Client(api_key=os.getenv("NVIDIA_API_KEY"))
        self.model = model_name

    def generate(self, prompt: str) -> str:
        try:
            result = self.client.generate(model=self.model, prompt=prompt)
            return result.text.strip()
        except Exception as e:
            logger.error(f"❌ NVIDIA Error: {e}")
            return f"Error: {e}"


# ---------------- FACTORY ---------------- #
class LLMFactory:
    PROVIDERS = {
        "gemini": GeminiLLM,
        "openai": OpenAILLM,
        "qwen": QwenLLM,
        "nvidia": NvidiaLLM,
    }

    @staticmethod
    def create(provider: str, model_name: str):
        provider = provider.lower()
        if provider not in LLMFactory.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        return LLMFactory.PROVIDERS[provider](model_name)
