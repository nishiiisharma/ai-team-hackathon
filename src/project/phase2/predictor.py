from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class IngredientPrediction:
    ingredient: str
    predicted_required_quantity: float
    available_stock: float


class PurchasePredictor:
    """Predict next purchase quantities using order history features."""

    def __init__(self, conn: Any) -> None:
        self.conn = conn

    def predict_for_user(
        self,
        user_id: int,
        ingredients: list[str],
        horizon_days: int = 7,
    ) -> list[IngredientPrediction]:
        normalized = [item.strip().lower() for item in ingredients if item.strip()]
        if not normalized:
            return []

        stock_map = self._get_stock(normalized)
        usage = self._get_usage_features(user_id=user_id, ingredients=normalized)

        predictions: list[IngredientPrediction] = []
        for ingredient in normalized:
            available = stock_map.get(ingredient, 0.0)
            features = usage.get(ingredient, {})

            base_daily = float(features.get("base_daily", 0.0))
            user_ratio = float(features.get("user_ratio", 1.0))
            time_boost = float(features.get("time_of_day_boost", 1.0))
            date_boost = float(features.get("weekday_boost", 1.0))
            season_boost = float(features.get("season_boost", 1.0))

            predicted = base_daily * horizon_days
            predicted *= user_ratio * time_boost * date_boost * season_boost
            predicted = round(max(predicted, 0.0), 2)

            predictions.append(
                IngredientPrediction(
                    ingredient=ingredient,
                    predicted_required_quantity=predicted,
                    available_stock=available,
                )
            )

        return predictions

    def _get_stock(self, ingredients: list[str]) -> dict[str, float]:
        placeholders = ",".join("%s" for _ in ingredients)
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT LOWER(name) AS ingredient, stock_quantity
                FROM products
                WHERE LOWER(name) IN ({placeholders})
                """,
                ingredients,
            )
            rows = cursor.fetchall()
        return {str(row[0]): float(row[1]) for row in rows}

    def _get_usage_features(
        self,
        user_id: int,
        ingredients: list[str],
    ) -> dict[str, dict[str, float]]:
        placeholders = ",".join("%s" for _ in ingredients)
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    LOWER(p.name) AS ingredient,
                    o.user_id,
                    o.order_ts,
                    od.quantity,
                    p.season_tag
                FROM order_details od
                JOIN orders o ON o.id = od.order_id
                JOIN products p ON p.id = od.product_id
                WHERE LOWER(p.name) IN ({placeholders})
                """,
                ingredients,
            )
            rows = cursor.fetchall()

        now = datetime.utcnow()
        per_ingredient_global_qty = defaultdict(float)
        per_ingredient_user_qty = defaultdict(float)
        per_ingredient_hourly_qty = defaultdict(float)
        per_ingredient_weekday_qty = defaultdict(float)
        per_ingredient_season_qty = defaultdict(float)
        per_ingredient_row_count = defaultdict(int)

        for ingredient, row_user_id, order_ts, quantity, season_tag in rows:
            ingredient_name = str(ingredient)
            qty = float(quantity)
            per_ingredient_global_qty[ingredient_name] += qty
            per_ingredient_row_count[ingredient_name] += 1

            parsed = datetime.fromisoformat(str(order_ts))
            if int(row_user_id) == user_id:
                per_ingredient_user_qty[ingredient_name] += qty
            if 11 <= parsed.hour <= 15 or 18 <= parsed.hour <= 23:
                per_ingredient_hourly_qty[ingredient_name] += qty
            if parsed.weekday() in {4, 5, 6}:
                per_ingredient_weekday_qty[ingredient_name] += qty
            if self._season_from_month(now.month) == str(season_tag):
                per_ingredient_season_qty[ingredient_name] += qty

        features: dict[str, dict[str, float]] = {}
        for ingredient in ingredients:
            global_qty = per_ingredient_global_qty.get(ingredient, 0.0)
            row_count = max(per_ingredient_row_count.get(ingredient, 1), 1)

            base_daily = global_qty / 365.0
            user_ratio = self._safe_ratio(
                per_ingredient_user_qty.get(ingredient, 0.0),
                global_qty,
                default=1.0,
                min_value=0.7,
                max_value=1.5,
            )
            time_boost = self._safe_ratio(
                per_ingredient_hourly_qty.get(ingredient, 0.0),
                global_qty,
                default=1.0,
                min_value=0.9,
                max_value=1.25,
            )
            weekday_boost = self._safe_ratio(
                per_ingredient_weekday_qty.get(ingredient, 0.0),
                global_qty,
                default=1.0,
                min_value=0.9,
                max_value=1.2,
            )
            season_boost = self._safe_ratio(
                per_ingredient_season_qty.get(ingredient, 0.0),
                global_qty,
                default=1.0,
                min_value=0.85,
                max_value=1.3,
            )

            features[ingredient] = {
                "base_daily": round(base_daily + (global_qty / row_count) * 0.05, 4),
                "user_ratio": user_ratio,
                "time_of_day_boost": time_boost,
                "weekday_boost": weekday_boost,
                "season_boost": season_boost,
            }
        return features

    @staticmethod
    def _safe_ratio(
        numerator: float,
        denominator: float,
        default: float,
        min_value: float,
        max_value: float,
    ) -> float:
        if denominator <= 0:
            return default
        ratio = numerator / denominator
        return round(min(max(ratio * 2.0, min_value), max_value), 4)

    @staticmethod
    def _season_from_month(month: int) -> str:
        if month in {3, 4, 5, 6}:
            return "summer"
        if month in {7, 8, 9, 10}:
            return "monsoon"
        return "winter"

