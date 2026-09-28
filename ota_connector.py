"""サイトコントローラー／OTAへの価格自動反映のインターフェース。

実運用では「ねっぱん！」等のサイトコントローラーAPI（またはベンダーとの
individual協議によるCSV連携・SFTP連携）に接続する部分。
契約前の現時点では実APIの仕様・認証情報が未確定のため、
ここでは差し替え可能なインターフェース（NeppanConnector）としてスタブ実装している。

本番移行時の想定ステップ:
  1. ベンダー（ねっぱん！等）と連携方式を協議（REST API / CSVアップロード / SFTP）
  2. 認証情報・レート制限・反映タイミング（即時 or バッチ）を確認
  3. push_rates() の中身を実API呼び出しに置き換える
  4. 反映結果のロギング・失敗時リトライ/アラートを追加
"""
from dataclasses import dataclass
from datetime import date


@dataclass
class RateUpdate:
    target_date: date
    price: int


class NeppanConnector:
    """ねっぱん！等のサイトコントローラーを想定した価格反映コネクタ（スタブ）。"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def push_rates(self, updates: list[RateUpdate]) -> list[dict]:
        results = []
        for update in updates:
            if self.dry_run:
                results.append(
                    {
                        "date": update.target_date.isoformat(),
                        "price": update.price,
                        "status": "would_push (dry_run)",
                    }
                )
            else:
                # TODO: 本番実装。ベンダーAPI確定後にHTTPリクエスト or ファイル連携に置き換える。
                raise NotImplementedError(
                    "実際のOTA連携はベンダー折衝・API仕様確定後に実装します。"
                )
        return results
