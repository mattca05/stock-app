from backend.database import Database
from backend.models import Exchange, Country, Sector, Ticker, Industry


class ExchangeManager:
    def __init__(self):
        self._db = Database.get_instance()

    def get_all_exchanges(self) -> list[str]:
        with self._db.session() as session:
            exchanges = session.query(Exchange).order_by(Exchange.name).all()
            return [ex.name for ex in exchanges]

    def get_all_countries(self) -> list[str]:
        with self._db.session() as session:
            countries = session.query(Country).order_by(Country.name).all()
            return [c.name for c in countries]

    def get_all_sectors(self) -> list[str]:
        with self._db.session() as session:
            sectors = session.query(Sector).order_by(Sector.name).all()
            return [s.name for s in sectors]

    def get_all_tickers_from_exchange(self, exchange_name: str) -> list[str]:
        with self._db.session() as session:
            exchange = session.query(Exchange).filter_by(name=exchange_name).first()
            if not exchange:
                return []
            return [t.symbol for t in exchange.tickers]

    def get_all_tickers_from_filters(
        self, filters: list[tuple[str, str]]
    ) -> list[tuple[str, str]]:
        exchanges = [n for t, n in filters if t == "exchange"]
        countries = [n for t, n in filters if t == "country"]
        sectors = [n for t, n in filters if t == "sector"]

        with self._db.session() as session:
            query = session.query(Ticker.symbol, Ticker.name)

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

            return [
                (row.symbol, row.name or row.symbol)
                for row in query.order_by(Ticker.name).all()
            ]
