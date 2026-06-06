from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from backend.services.ticker_service import TickerService


class PortfolioContent(QWidget):
    def __init__(self):
        super().__init__()
        self._ticker_service = TickerService()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.count_label = QLabel("Select filters to begin")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.count_label)

    def on_filters_changed(self, filters: list[tuple[str, str]]):
        count = self._ticker_service.get_ticker_count(filters)
        self.count_label.setText(f"{count} tickers match current filters")
