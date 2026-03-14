from __future__ import annotations

from dataclasses import dataclass

from langchain_core.documents import Document

from src.project.vectordatabase.chroma_client import ChromaVectorStore


@dataclass(frozen=True)
class RetrievalResult:
    context_text: str
    sources: list[str]


class SemanticRetriever:
    def __init__(self, vector_store: ChromaVectorStore) -> None:
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 4) -> RetrievalResult:
        docs: list[Document] = self.vector_store.similarity_search(query, k=top_k)
        snippets: list[str] = []
        sources: list[str] = []

        for index, doc in enumerate(docs, start=1):
            source = str(doc.metadata.get("source", f"doc_{index}"))
            sources.append(source)
            snippets.append(f"[{source}] {doc.page_content}")

        return RetrievalResult(
            context_text="\n".join(snippets),
            sources=sources,
        )

