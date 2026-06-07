from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
from ui.views.portfolio_analysis.filter_sidebar import FilterSidebar
from ui.views.portfolio_analysis.ticker_selector import TickerSelector
from ui.views.portfolio_analysis.content import PortfolioContent
from backend.services.exchange_manager import ExchangeManager
from ui.constants import MARGIN_PA_ROOT, SPACING_PA_ROOT


class PortfolioAnalysisView(QWidget):
    go_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._exchange_manager = ExchangeManager()
        self.sidebar = FilterSidebar()
        self.ticker_selector = TickerSelector()
        self.content = PortfolioContent()
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            MARGIN_PA_ROOT, MARGIN_PA_ROOT, MARGIN_PA_ROOT, MARGIN_PA_ROOT
        )
        layout.setSpacing(SPACING_PA_ROOT)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.ticker_selector)
        layout.addWidget(self.content)

    def _connect_signals(self):
        self.sidebar.go_back.connect(self.go_back)
        self.sidebar.filters_changed.connect(self._on_filters_changed)
        self.sidebar.filters_changed.connect(self.content.on_filters_changed)
        self.ticker_selector.tickers_changed.connect(self.content.on_tickers_changed)

    def _on_filters_changed(self, filters: list[tuple[str, str]]):
        if not filters:
            self.ticker_selector.load_tickers([])
            self.content.on_tickers_changed({"available": [], "held": {}})
            return

        tickers = self._exchange_manager.get_all_tickers_from_filters(filters)
        self.ticker_selector.load_tickers(tickers)
        self.content.on_tickers_changed(
            {
                "available": [s for s, _ in tickers],
                "held": self.ticker_selector._held_tickers,
            }
        )
