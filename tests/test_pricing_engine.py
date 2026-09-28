import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import PricingConfig
from pricing_engine import suggest_price

cfg = PricingConfig()


def test_weekend_is_more_expensive_than_weekday():
    # 2026-08-07(金) と 2026-08-10(月) で同一稼働率・リードタイムで比較
    weekday = suggest_price(
        date(2026, 8, 10), occupancy_rate=0.5, lead_time_days=30, cfg=cfg
    )
    weekend = suggest_price(
        date(2026, 8, 7), occupancy_rate=0.5, lead_time_days=30, cfg=cfg
    )
    assert weekend.suggested_price > weekday.suggested_price


def test_high_occupancy_raises_price():
    low = suggest_price(
        date(2026, 11, 10), occupancy_rate=0.1, lead_time_days=30, cfg=cfg
    )
    high = suggest_price(
        date(2026, 11, 10), occupancy_rate=0.9, lead_time_days=30, cfg=cfg
    )
    assert high.suggested_price > low.suggested_price


def test_last_minute_discount_applies_within_threshold():
    far = suggest_price(
        date(2026, 11, 10), occupancy_rate=0.5, lead_time_days=30, cfg=cfg
    )
    last_minute = suggest_price(
        date(2026, 11, 10), occupancy_rate=0.5, lead_time_days=1, cfg=cfg
    )
    assert last_minute.suggested_price < far.suggested_price


def test_price_is_clamped_within_market_band():
    # 周辺相場が極端に低い場合、下限バンドでクランプされる
    result = suggest_price(
        date(2026, 8, 7),  # 金曜・高稼働
        occupancy_rate=0.95,
        lead_time_days=30,
        market_summary={"median": 5000, "min": 4500, "max": 5500, "sample_size": 5},
        cfg=cfg,
    )
    upper_bound = 5000 * cfg.market_band_upper
    # 100円単位の丸め処理があるため、丸め単位の範囲内であることを許容する
    assert result.suggested_price <= upper_bound + cfg.rounding_unit
    assert result.clamped_by_market is True


def test_suggested_price_is_rounded_to_configured_unit():
    result = suggest_price(
        date(2026, 11, 10), occupancy_rate=0.5, lead_time_days=30, cfg=cfg
    )
    assert result.suggested_price % cfg.rounding_unit == 0
