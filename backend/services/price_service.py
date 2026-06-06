from backend.database import Database
from backend.models import Price, Ticker
from datetime import date


class PriceService:
    def __init__(self):
        self._db = Database.get_instance()

    def get_latest_price(self, symbol: str) -> float | None:
        with self._db.session() as session:
            result = (
                session.query(Price)
                .join(Price.ticker)
                .filter(Ticker.symbol == symbol)
                .order_by(Price.date.desc())
                .first()
            )
            return result.close if result else None

    def get_prices_for_ticker(self, symbol: str) -> list[tuple[date, float]]:
        with self._db.session() as session:
            results = (
                session.query(Price)
                .join(Price.ticker)
                .filter(Ticker.symbol == symbol)
                .order_by(Price.date.asc())
                .all()
            )
            return [(r.date, r.close) for r in results]

    def get_prices_for_tickers(
        self, symbols: list[str]
    ) -> dict[str, list[tuple[date, float]]]:
        return {symbol: self.get_prices_for_ticker(symbol) for symbol in symbols}
