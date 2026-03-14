from src.project.phase2.predictor import PurchasePredictor


def test_predictor_safe_ratio_bounds() -> None:
    ratio = PurchasePredictor._safe_ratio(
        numerator=100.0,
        denominator=10.0,
        default=1.0,
        min_value=0.9,
        max_value=1.2,
    )
    assert ratio == 1.2


def test_predictor_season_mapping() -> None:
    assert PurchasePredictor._season_from_month(4) == "summer"
    assert PurchasePredictor._season_from_month(8) == "monsoon"
    assert PurchasePredictor._season_from_month(12) == "winter"

