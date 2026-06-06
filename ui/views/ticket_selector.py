from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
)
from PyQt6.QtCore import Qt
import re

from ui.constants import (
    WIDTH_TICKER_LIST,
    MARGIN_TICKER_SIDEBAR,
    SPACING_TICKER_SIDEBAR,
)


class TickerSelector(QFrame):
    def __init__(self):
        super().__init__()
        self._selected_tickers: list[str] = []
        self._available_tickers: list[tuple[str, str]] = []
        self._init_ui()

    def _init_ui(self):
        self.setFixedWidth(WIDTH_TICKER_LIST)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            MARGIN_TICKER_SIDEBAR,
            MARGIN_TICKER_SIDEBAR,
            MARGIN_TICKER_SIDEBAR,
            MARGIN_TICKER_SIDEBAR,
        )
        layout.setSpacing(SPACING_TICKER_SIDEBAR)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(QLabel("Available Tickers"))

        # Two column list
        self.available_list = QTreeWidget()
        self.available_list.setFixedHeight(200)
        self.available_list.setHeaderLabels(["Name", "Symbol"])
        self.available_list.setColumnWidth(0, 180)  # Name column
        self.available_list.setColumnWidth(1, 80)  # Symbol column
        self.available_list.setRootIsDecorated(False)  # No expand arrows
        layout.addWidget(self.available_list)

        # Add / Remove buttons
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add →")
        btn_add.clicked.connect(self._add_ticker)
        btn_remove = QPushButton("← Remove")
        btn_remove.clicked.connect(self._remove_ticker)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)

        layout.addWidget(QLabel("Selected Tickers"))

        # Selected tickers list
        self.selected_list = QListWidget()
        self.selected_list.setFixedHeight(200)
        layout.addWidget(self.selected_list)

        btn_clear = QPushButton("Clear All")
        btn_clear.clicked.connect(self._clear_tickers)
        layout.addWidget(btn_clear)

        layout.addStretch()

    def _clean_name(self, name: str) -> str:
        suffixes = r"\b(p\.?l\.?c\.?|ag|se|ab|asa|nv|sa|inc|corp|ltd|llc|co)\b\.?"
        name = re.sub(r"\s*\(publ\.?\)\s*", "", name, flags=re.IGNORECASE)
        name = re.sub(rf"\s*{suffixes}\s*$", "", name, flags=re.IGNORECASE)
        return name.strip()

    def load_tickers(self, tickers: list[tuple[str, str]]):
        self.available_list.clear()
        self._available_tickers = tickers
        for symbol, name in tickers:
            clean = self._clean_name(name)
            item = QTreeWidgetItem([clean[:30], symbol[:10]])
            self.available_list.addTopLevelItem(item)

    def _add_ticker(self):
        item = self.available_list.currentItem()
        if item is None:
            return
        row = self.available_list.indexOfTopLevelItem(item)
        symbol, name = self._available_tickers[row]
        clean = self._clean_name(name)
        if symbol in self._selected_tickers:
            return
        self._selected_tickers.append(symbol)
        self.selected_list.addItem(f"{clean[:30]} ({symbol[:10]})")

    def _remove_ticker(self):
        item = self.selected_list.currentItem()
        if item is None:
            return
        row = self.selected_list.row(item)
        self._selected_tickers.pop(row)
        self.selected_list.takeItem(row)

    def _clear_tickers(self):
        self._selected_tickers.clear()
        self.selected_list.clear()
