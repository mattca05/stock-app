from backend.database import Database
from backend.models import Ticker, Exchange, Country, Sector, Industry


class TickerService:
    def __init__(self):
        self._db = Database.get_instance()

    def get_ticker_count(self, filters: list[tuple[str, str]]) -> int:
        if not filters:
            return 0

        exchanges = [n for t, n in filters if t == "exchange"]
        countries = [n for t, n in filters if t == "country"]
        sectors = [n for t, n in filters if t == "sector"]

        with self._db.session() as session:
            query = session.query(Ticker)

            if exchanges:
                query = query.join(Ticker.exchange).filter(Exchange.name.in_(exchanges))
            if countries:
                query = query.join(Ticker.country).filter(Country.name.in_(countries))
            if sectors:
                query = (
                    query.join(Ticker.industry)
                    .join(Industry.sector)
                    .filter(Sector.name.in_(sectors))
                )

            return query.count()
