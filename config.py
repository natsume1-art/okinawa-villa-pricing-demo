"""価格算出ロジックのパラメータ設定。

実運用では代表者・コンサルタントとの要件定義を通じて
数値をチューニングする想定（このファイルを外部化すればノーコードで調整可能）。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PricingConfig:
    base_price: int = 18000  # 平日・通常期の基準宿泊料金（1棟/泊）

    # 曜日・季節倍率
    weekend_multiplier: float = 1.25          # 金・土曜日
    high_season_multiplier: float = 1.40      # 夏季ハイシーズン
    shoulder_season_multiplier: float = 1.15  # 春・秋の準ハイシーズン

    high_season_start: tuple = (7, 1)   # 7/1
    high_season_end: tuple = (9, 10)    # 9/10
    shoulder_months: tuple = (4, 5, 10, 11)

    # 稼働率連動デマンドプライシング（閾値, 倍率）を稼働率が高い順に評価
    occupancy_thresholds: tuple = (
        (0.85, 1.20),
        (0.60, 1.05),
        (0.30, 1.00),
        (0.0, 0.90),
    )

    # リードタイム（宿泊日までの日数）調整
    last_minute_days: int = 3
    last_minute_discount: float = 0.90   # 直前3日以内の空室は-10%
    early_bird_days: int = 60
    early_bird_discount: float = 0.95    # 60日以上前は-5%（早期予約促進）

    # 周辺相場に対するガードレール
    market_band_lower: float = 0.85
    market_band_upper: float = 1.15

    rounding_unit: int = 100  # 100円単位で丸め
