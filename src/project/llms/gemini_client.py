from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI

from src.project.llms.base import BaseLLMClient, ModelRequest, ModelResponse


class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str, model_name: str) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self._fallback_models = [
            "gemini-2.5-flash",
            "gemini-3-flash-preview",
            "gemini-2.5-pro",
            "gemini-2.5-flash-lite"
        ]

    def _create_client(self, model_name: str, temperature: float) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=temperature,
        )

    def generate(self, request: ModelRequest) -> ModelResponse:
        candidates = [self.model_name] + [
            model for model in self._fallback_models if model != self.model_name
        ]
        last_error: Exception | None = None

        for model_name in candidates:
            try:
                client = self._create_client(
                    model_name=model_name,
                    temperature=request.temperature,
                )
                result = client.invoke(request.prompt)
                text = getattr(result, "content", "") or ""

                # Usage metadata can be missing depending on provider responses.
                usage = getattr(result, "usage_metadata", {}) or {}
                prompt_tokens = int(usage.get("input_tokens", 0))
                completion_tokens = int(usage.get("output_tokens", 0))

                self.model_name = model_name
                return ModelResponse(
                    text=text,
                    model_name=self.model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )
            except Exception as error:
                last_error = error
                continue

        tried = ", ".join(candidates)
        raise RuntimeError(
            f"All Gemini model candidates failed. Tried: {tried}"
        )

