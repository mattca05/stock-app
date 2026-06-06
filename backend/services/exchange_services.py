from backend.models import Exchange
from backend.database import Database


def get_all_exchanges() -> list[str]:
    db = Database.get_instance()
    with db.session() as session:
        exchanges = session.query(Exchange).order_by(Exchange.name).all()
        return [ex.name for ex in exchanges]
