from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class ChromaVectorStore:
    def __init__(self, persist_dir: str, embedding_model: str, api_key: str) -> None:
        normalized_model = embedding_model.removeprefix("models/")
        embeddings = GoogleGenerativeAIEmbeddings(
            model=normalized_model,
            google_api_key=api_key,
        )
        self._store = Chroma(
            collection_name="kombee_phase1",
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )

    def add_documents(self, documents: list[Document]) -> None:
        if documents:
            try:
                self._store.add_documents(documents)
            except Exception:
                # Fail-open for Phase 1 smoke runs when embeddings endpoint is unavailable.
                return

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        try:
            return self._store.similarity_search(query=query, k=k)
        except Exception:
            # Fall back to empty context instead of failing request orchestration.
            return []

