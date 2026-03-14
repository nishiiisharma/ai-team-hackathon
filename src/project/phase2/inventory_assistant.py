from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from src.project.config.settings import Settings
from src.project.phase2.menu_parser import MenuParser
from src.project.phase2.predictor import PurchasePredictor
from src.project.phase2.types import IngredientDemand
from src.project.vectordatabase.chroma_client import ChromaVectorStore


class RestaurantInventoryAssistant:
    def __init__(self, settings: Settings, conn: Any) -> None:
        self.settings = settings
        self.conn = conn
        self.menu_parser = MenuParser(
            gemini_api_key=settings.gemini_api_key,
            llm_model=settings.default_llm_model,
        )
        self.predictor = PurchasePredictor(conn=conn)
        self.vector_store = ChromaVectorStore(
            persist_dir=settings.chroma_persist_dir,
            embedding_model=settings.default_embedding_model,
            api_key=settings.gemini_api_key,
        )

    def run(self, menu_path: str, user_id: int) -> dict[str, object]:
        menu_text = self.menu_parser.load_menu_text(menu_path)
        dishes = self.menu_parser.extract_dishes(menu_text)
        ingredients = sorted(
            {ingredient for dish in dishes for ingredient in dish.ingredients}
        )

        self._store_menu_knowledge(menu_path=menu_path, dishes=dishes)

        predictions = self.predictor.predict_for_user(
            user_id=user_id,
            ingredients=ingredients,
            horizon_days=7,
        )
        demand_rows = [
            IngredientDemand(
                ingredient=item.ingredient,
                available_stock=item.available_stock,
                predicted_required_quantity=item.predicted_required_quantity,
                recommended_order_quantity=round(
                    max(item.predicted_required_quantity - item.available_stock, 0.0),
                    2,
                ),
            )
            for item in predictions
            if item.predicted_required_quantity > item.available_stock
        ]

        return {
            "menu_path": str(Path(menu_path)),
            "user_id": user_id,
            "dish_count": len(dishes),
            "ingredient_count": len(ingredients),
            "dishes": [asdict(dish) for dish in dishes],
            "cart_table": [asdict(row) for row in demand_rows],
            "cart_table_markdown": self._as_markdown_table(demand_rows),
        }

    def _store_menu_knowledge(self, menu_path: str, dishes: list[object]) -> None:
        documents: list[Document] = []
        for dish in dishes:
            payload = json.dumps(asdict(dish), ensure_ascii=True)
            documents.append(
                Document(
                    page_content=payload,
                    metadata={
                        "source": menu_path,
                        "content_type": "menu_dish_ingredients",
                    },
                )
            )
        self.vector_store.add_documents(documents)

    @staticmethod
    def _as_markdown_table(rows: list[IngredientDemand]) -> str:
        header = (
            "| Ingredient | Available Stock | Predicted Required Quantity | "
            "Recommended Order Quantity |\n"
            "|---|---:|---:|---:|"
        )
        body = [
            (
                f"| {row.ingredient} | {row.available_stock:.2f} | "
                f"{row.predicted_required_quantity:.2f} | "
                f"{row.recommended_order_quantity:.2f} |"
            )
            for row in rows
        ]
        return "\n".join([header] + body) if body else f"{header}\n| - | 0.00 | 0.00 | 0.00 |"

