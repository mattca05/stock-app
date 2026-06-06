from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QListWidget,
    QStackedWidget,
)
from typing import Callable
from PyQt6.QtCore import pyqtSignal, Qt
from ui.views.portfolio_content import PortfolioContent
from ui.constants import (
    SPACING_PA_SIDEBAR,
    MARGIN_PA_SIDEBAR,
    SIDEBAR_PA_WIDTH,
    SPACING_PA_DIVIDER,
    LABEL_PA_EXCHANGE,
    LABEL_PA_BACK,
    LABEL_PA_SELECTED,
    LABEL_PA_SELECT_COUNTRY,
    MARGIN_PA_ROOT,
    SPACING_PA_ROOT,
    SPACING_PA_SELECTED,
    LABEL_PA_SELECT_EXCHANGE,
    DROPDOWN_PA_HEIGHT,
    DROPDOWN_MAX_ITEMS,
    LABEL_PA_SELECT_SECTOR,
    LABEL_PA_SECTOR,
    LABEL_PA_SELECT_EXCHANGE_TO_BEGIN,
    SIDEBAR_PA_LIST_HEIGHT,
    LABEL_PA_COUNTRIES,
)

from backend.services.exchange_manager import ExchangeManager
from ui.views.ticket_selector import TickerSelector


class PortfolioAnalysisView(QWidget):
    go_back = pyqtSignal()
    filters_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._selected_filters: list[tuple[str, str]] = (
            []
        )  # [("exchange", "NYSE"), ("country", "USA")]
        self._exchange_manager = ExchangeManager()
        self.content = PortfolioContent()
        self.ticker_selector = TickerSelector()
        self._init_ui()

    def _init_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(
            MARGIN_PA_ROOT, MARGIN_PA_ROOT, MARGIN_PA_ROOT, MARGIN_PA_ROOT
        )
        root_layout.setSpacing(SPACING_PA_ROOT)

        root_layout.addWidget(self._make_sidebar())
        root_layout.addWidget(self.ticker_selector)
        root_layout.addWidget(self.content)

    # ── Sidebar ───────────────────────────────────────────────
    def _make_sidebar(self) -> QFrame:
        sidebar, layout = self._setup_sidebar()

        btn_back = self._create_button(LABEL_PA_BACK, lambda: self.go_back.emit())
        layout.addWidget(btn_back)
        layout.addSpacing(SPACING_PA_DIVIDER)

        tabs = self._create_tabs()
        layout.addWidget(tabs)

        layout.addWidget(QLabel(LABEL_PA_SELECTED))
        self.selected_list = QListWidget()
        self.selected_list.setFixedHeight(SIDEBAR_PA_LIST_HEIGHT)
        layout.addWidget(self.selected_list)

        btn_layout = QHBoxLayout()
        btn_remove = self._create_button("Remove", self._remove_selected)
        btn_clear = self._create_button("Clear All", self._clear_filters)
        btn_undo = self._create_button("Undo", self._undo_filter)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_clear)
        btn_layout.addWidget(btn_undo)
        layout.addLayout(btn_layout)

        # ── Run button ────────────────────────────────────────────
        btn_run = self._create_button("Run Analysis", self._run_analysis)
        layout.addWidget(btn_run)

        layout.addStretch()
        self._load_filters()
        return sidebar

    def _run_analysis(self):
        if not self._selected_filters:
            self.content.show_message("Please select at least one filter.")
            return
        self.content.on_filters_changed(self._selected_filters)

    def _setup_sidebar(self) -> tuple[QFrame, QVBoxLayout]:
        sidebar = QFrame()
        sidebar.setFixedWidth(SIDEBAR_PA_WIDTH)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(
            MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR
        )
        layout.setSpacing(SPACING_PA_SIDEBAR)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        return sidebar, layout

    def _create_tabs(self) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)

        # Stack for the lists
        self.filter_stack = QStackedWidget()
        self.filter_stack.addWidget(
            self._create_list("exchange", DROPDOWN_PA_HEIGHT)
        )  # index 0
        self.filter_stack.addWidget(
            self._create_list("country", DROPDOWN_PA_HEIGHT)
        )  # index 1
        self.filter_stack.addWidget(
            self._create_list("sector", DROPDOWN_PA_HEIGHT)
        )  # index 2

        # Store lists for populating later
        self.exchange_list = self.filter_stack.widget(0)
        self.country_list = self.filter_stack.widget(1)
        self.sector_list = self.filter_stack.widget(2)

        # Toggle buttons
        self._tab_buttons: list[QPushButton] = []
        for i, label in enumerate(
            [LABEL_PA_EXCHANGE, LABEL_PA_COUNTRIES, LABEL_PA_SECTOR]
        ):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, idx=i: self._switch_tab(idx))
            container_layout.addWidget(btn)
            self._tab_buttons.append(btn)

        container_layout.addWidget(self.filter_stack)

        # Activate first tab
        self._switch_tab(0)

        return container

    def _switch_tab(self, index: int):
        self.filter_stack.setCurrentIndex(index)
        for i, btn in enumerate(self._tab_buttons):
            btn.setChecked(i == index)

    def _create_button(self, text: str, func: Callable) -> QPushButton:
        btn = QPushButton(text)
        btn.clicked.connect(func)
        return btn

    def _create_list(self, filter_type: str, height: int) -> QListWidget:
        lst = QListWidget()
        lst.setFixedHeight(height)
        lst.itemClicked.connect(
            lambda item: self._on_filter_changed(filter_type, item.text())
        )
        return lst

    def _load_filters(self):
        for name in self._exchange_manager.get_all_exchanges():
            self.exchange_list.addItem(name)

        for name in self._exchange_manager.get_all_countries():
            self.country_list.addItem(name)

        for name in self._exchange_manager.get_all_sectors():
            self.sector_list.addItem(name)

    # ── Slots ─────────────────────────────────────────────────
    def _on_filter_changed(self, filter_type: str, name: str):
        if name.startswith("--"):
            return
        entry = (filter_type, name)
        if entry in self._selected_filters:
            return
        self._selected_filters.append(entry)
        self._refresh_selected()

    def _refresh_selected(self):
        self.selected_list.clear()
        for filter_type, name in self._selected_filters:
            self.selected_list.addItem(f"[{filter_type}] {name}")

        if self._selected_filters:
            tickers = self._exchange_manager.get_all_tickers_from_filters(
                self._selected_filters
            )
            self.ticker_selector.load_tickers(tickers)
        else:
            self.ticker_selector.load_tickers([])

    def _remove_selected(self):
        item = self.selected_list.currentItem()
        if item is None:
            return
        text = item.text()
        filter_type, name = text.split("] ")
        filter_type = filter_type.lstrip("[")
        self._selected_filters = [
            f
            for f in self._selected_filters
            if not (f[0] == filter_type and f[1] == name)
        ]
        self._refresh_selected()

    def _clear_filters(self):
        self._selected_filters.clear()
        self._refresh_selected()

    def _undo_filter(self):
        if self._selected_filters:
            self._selected_filters.pop()
            self._refresh_selected()
