"""ルールベースの宿泊価格算出ロジック。

入力: 対象日、稼働率、周辺相場サマリ、宿泊日までの残り日数（リードタイム）
出力: 提案価格（円）と算出根拠（適用した倍率・調整の内訳）

要件定義との対応:
  「宿泊日数、周辺相場、予約埋まり状況等のデータを収集・ルールベースで価格を算出する」
  に対応するコア機能。
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from config import PricingConfig


@dataclass
class PriceSuggestion:
    target_date: date
    base_price: int
    suggested_price: int
    applied_factors: list = field(default_factory=list)
    market_median: Optional[float] = None
    clamped_by_market: bool = False


def _season_multiplier(d: date, cfg: PricingConfig) -> tuple:
    hs_start = date(d.year, *cfg.high_season_start)
    hs_end = date(d.year, *cfg.high_season_end)
    if hs_start <= d <= hs_end:
        return cfg.high_season_multiplier, "high_season"
    if d.month in cfg.shoulder_months:
        return cfg.shoulder_season_multiplier, "shoulder_season"
    return 1.0, "regular_season"


def _weekend_multiplier(d: date, cfg: PricingConfig) -> tuple:
    if d.weekday() in (4, 5):  # 金・土
        return cfg.weekend_multiplier, "weekend"
    return 1.0, "weekday"


def _occupancy_multiplier(occupancy_rate: float, cfg: PricingConfig) -> tuple:
    for threshold, multiplier in cfg.occupancy_thresholds:
        if occupancy_rate >= threshold:
            return multiplier, f"occupancy>={threshold:.0%}"
    return 1.0, "occupancy_default"


def _lead_time_multiplier(lead_time_days: int, cfg: PricingConfig) -> tuple:
    if lead_time_days <= cfg.last_minute_days:
        return cfg.last_minute_discount, "last_minute_discount"
    if lead_time_days >= cfg.early_bird_days:
        return cfg.early_bird_discount, "early_bird_discount"
    return 1.0, "lead_time_neutral"


def _round_price(price: float, unit: int) -> int:
    return int(round(price / unit) * unit)


def suggest_price(
    target_date: date,
    occupancy_rate: float,
    lead_time_days: int,
    market_summary: Optional[dict] = None,
    cfg: Optional[PricingConfig] = None,
) -> PriceSuggestion:
    cfg = cfg or PricingConfig()
    price = float(cfg.base_price)
    factors = []

    for multiplier, label in (
        _season_multiplier(target_date, cfg),
        _weekend_multiplier(target_date, cfg),
        _occupancy_multiplier(occupancy_rate, cfg),
        _lead_time_multiplier(lead_time_days, cfg),
    ):
        price *= multiplier
        factors.append({"factor": label, "multiplier": multiplier})

    clamped = False
    market_median = None
    if market_summary:
        market_median = market_summary.get("median")
        if market_median:
            lower = market_median * cfg.market_band_lower
            upper = market_median * cfg.market_band_upper
            if price < lower:
                price = lower
                clamped = True
                factors.append({"factor": "market_band_lower_clamp", "multiplier": None})
            elif price > upper:
                price = upper
                clamped = True
                factors.append({"factor": "market_band_upper_clamp", "multiplier": None})

    final_price = _round_price(price, cfg.rounding_unit)

    return PriceSuggestion(
        target_date=target_date,
        base_price=cfg.base_price,
        suggested_price=final_price,
        applied_factors=factors,
        market_median=market_median,
        clamped_by_market=clamped,
    )
