from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document


class DocumentProcessor:
    def from_text_file(self, file_path: str) -> list[Document]:
        content = Path(file_path).read_text(encoding="utf-8")
        return self._chunk_text(content=content, source=file_path)

    def from_text(self, content: str, source: str = "inline") -> list[Document]:
        return self._chunk_text(content=content, source=source)

    def _chunk_text(
        self,
        content: str,
        source: str,
        chunk_size: int = 700,
        overlap: int = 100,
    ) -> list[Document]:
        if chunk_size <= overlap:
            raise ValueError("chunk_size must be greater than overlap.")

        text = content.strip()
        if not text:
            return []

        chunks: list[Document] = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]
            chunks.append(
                Document(
                    page_content=chunk_text,
                    metadata={"source": source, "start": start, "end": end},
                )
            )
            if end == len(text):
                break
            start = end - overlap
        return chunks

