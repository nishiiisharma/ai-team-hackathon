from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader

from src.project.llms.base import ModelRequest
from src.project.llms.gemini_client import GeminiClient
from src.project.phase2.types import MenuDish


FALLBACK_RECIPE_BOOK: dict[str, list[str]] = {
    "paneer butter masala": ["paneer", "tomato", "onion", "cream", "butter"],
    "veg biryani": ["rice", "onion", "carrot", "beans", "peas", "spices"],
    "chicken biryani": ["rice", "chicken", "onion", "yogurt", "spices"],
    "margherita pizza": ["flour", "tomato", "mozzarella", "olive oil", "basil"],
    "pasta alfredo": ["pasta", "cream", "garlic", "butter", "cheese"],
    "masala dosa": ["rice", "lentil", "potato", "onion", "oil"],
}


class MenuParser:
    def __init__(self, gemini_api_key: str, llm_model: str) -> None:
        self._llm = GeminiClient(api_key=gemini_api_key, model_name=llm_model)

    def load_menu_text(self, menu_path: str) -> str:
        path = Path(menu_path)
        if not path.exists():
            raise FileNotFoundError(f"Menu file not found: {menu_path}")
        if path.suffix.lower() == ".pdf":
            return self._read_pdf(path)
        return path.read_text(encoding="utf-8")

    def extract_dishes(self, menu_text: str) -> list[MenuDish]:
        prompt = (
            "Extract menu dishes and ingredients from the text.\n"
            "Return valid JSON only as an array of objects.\n"
            'Each object format: {"name":"dish","ingredients":["i1","i2"]}\n'
            "Use concise ingredient names.\n\n"
            f"Menu text:\n{menu_text[:8000]}"
        )
        response = self._llm.generate(
            ModelRequest(
                prompt=prompt,
                temperature=0.1,
                max_tokens=700,
            )
        )
        dishes = self._parse_json(response.text)
        if dishes:
            return dishes
        return self._fallback_extract(menu_text)

    def _parse_json(self, text: str) -> list[MenuDish]:
        try:
            payload = json.loads(text)
            if not isinstance(payload, list):
                return []
            parsed: list[MenuDish] = []
            for item in payload:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "")).strip().lower()
                ingredients = item.get("ingredients", [])
                if not name or not isinstance(ingredients, list):
                    continue
                normalized = [
                    str(ingredient).strip().lower()
                    for ingredient in ingredients
                    if str(ingredient).strip()
                ]
                if normalized:
                    parsed.append(MenuDish(name=name, ingredients=normalized))
            return parsed
        except json.JSONDecodeError:
            return []

    def _fallback_extract(self, menu_text: str) -> list[MenuDish]:
        lowered = menu_text.lower()
        matched: list[MenuDish] = []
        for dish_name, ingredients in FALLBACK_RECIPE_BOOK.items():
            if dish_name in lowered:
                matched.append(MenuDish(name=dish_name, ingredients=ingredients))
        if matched:
            return matched
        # Last-resort fallback: line-based dish guesses.
        lines = [line.strip().lower() for line in menu_text.splitlines() if line.strip()]
        return [MenuDish(name=line[:80], ingredients=["salt", "oil"]) for line in lines[:10]]

    def _read_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        chunks: list[str] = []
        for page in reader.pages:
            chunks.append(page.extract_text() or "")
        return "\n".join(chunks)

