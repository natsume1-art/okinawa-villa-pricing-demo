"""周辺相場（競合ヴィラの宿泊料金）の収集モジュール。

本番運用では実際の競合サイト/OTA掲載価格をスクレイピングする想定。
このデモでは無許可でのスクレイピングを避けるため、
ローカルfixture（scripts/generate_sample_fixtures.pyで生成）を解析するオフラインモードを既定とし、
`fetch_competitor_rates(live_url=...)` を渡した場合のみ実URLへのHTTP取得を行う構造にしている。
"""
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Optional

from bs4 import BeautifulSoup

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
DEFAULT_FIXTURE = FIXTURES_DIR / "competitor_rates_sample.html"


def _parse_html(html: str) -> dict:
    """rate-card要素を日付ごとに集計し、統計量（中央値・最小・最大・件数）を返す。"""
    soup = BeautifulSoup(html, "html.parser")
    prices_by_date = defaultdict(list)

    for card in soup.select(".rate-card"):
        d = card.get("data-date")
        price = card.get("data-price")
        if d is None or price is None:
            continue
        prices_by_date[d].append(int(price))

    return {
        d: {
            "median": median(prices),
            "min": min(prices),
            "max": max(prices),
            "sample_size": len(prices),
        }
        for d, prices in prices_by_date.items()
    }


def fetch_competitor_rates(
    fixture_path: Optional[Path] = None,
    live_url: Optional[str] = None,
    timeout: int = 10,
) -> dict:
    """日付をキーとした周辺相場サマリを返す。

    live_url が指定された場合は実サイトへHTTP GETを行う（要・利用規約/robots.txt確認、
    アクセス頻度のレート制限などは本番実装時に追加する）。未指定時はローカルfixtureを使用。
    """
    if live_url:
        import requests

        response = requests.get(live_url, timeout=timeout)
        response.raise_for_status()
        html = response.text
    else:
        path = fixture_path or DEFAULT_FIXTURE
        html = path.read_text(encoding="utf-8")

    return _parse_html(html)


if __name__ == "__main__":
    rates = fetch_competitor_rates()
    for d in sorted(rates)[:5]:
        print(d, rates[d])
