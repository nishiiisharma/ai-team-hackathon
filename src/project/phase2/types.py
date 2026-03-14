from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MenuDish:
    name: str
    ingredients: list[str]


@dataclass(frozen=True)
class IngredientDemand:
    ingredient: str
    available_stock: float
    predicted_required_quantity: float
    recommended_order_quantity: float

