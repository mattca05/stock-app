from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QDoubleSpinBox,
    QTabWidget,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
import re

from ui.constants import (
    WIDTH_TICKER_LIST,
    MARGIN_TICKER_SIDEBAR,
    SPACING_TICKER_SIDEBAR,
)


class TickerSelector(QFrame):
    tickers_changed = pyqtSignal(dict)  # {"held": {symbol: weight}}

    def __init__(self):
        super().__init__()
        self._available_tickers: list[tuple[str, str]] = []
        self._held_tickers: dict[str, float] = {}
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

        self.available_list = QTreeWidget()
        self.available_list.setFixedHeight(200)
        self.available_list.setHeaderLabels(["Name", "Symbol"])
        self.available_list.setColumnWidth(0, 180)
        self.available_list.setColumnWidth(1, 80)
        self.available_list.setRootIsDecorated(False)
        layout.addWidget(self.available_list)

        # Weight input + add button
        weight_row = QHBoxLayout()
        weight_row.addWidget(QLabel("Weight %:"))
        self.held_weight_input = QDoubleSpinBox()
        self.held_weight_input.setRange(0.01, 100.0)
        self.held_weight_input.setValue(10.0)
        self.held_weight_input.setSingleStep(0.1)
        self.held_weight_input.setDecimals(1)
        weight_row.addWidget(self.held_weight_input)
        btn_add = QPushButton("Pin →")
        btn_add.clicked.connect(self._add_to_held)
        weight_row.addWidget(btn_add)
        layout.addLayout(weight_row)

        layout.addWidget(QLabel("Pinned Tickers"))

        self.held_list = QTreeWidget()
        self.held_list.setFixedHeight(150)
        self.held_list.setHeaderLabels(["Name", "Symbol", "Weight %"])
        self.held_list.setColumnWidth(0, 120)
        self.held_list.setColumnWidth(1, 60)
        self.held_list.setColumnWidth(2, 70)
        self.held_list.setRootIsDecorated(False)
        layout.addWidget(self.held_list)

        btn_layout = QHBoxLayout()
        btn_remove = QPushButton("Remove")
        btn_remove.clicked.connect(self._remove_from_held)
        btn_clear = QPushButton("Clear All")
        btn_clear.clicked.connect(self._clear_all)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_clear)
        layout.addLayout(btn_layout)

        layout.addStretch()

    def load_tickers(self, tickers: list[tuple[str, str]]):
        self.available_list.clear()
        self._available_tickers = tickers
        for symbol, name in tickers:
            clean = self._clean_name(name)
            item = QTreeWidgetItem([clean[:30], symbol[:10]])
            self.available_list.addTopLevelItem(item)

    def get_selection(self) -> dict:
        return {
            "available": [s for s, _ in self._available_tickers],
            "held": self._held_tickers.copy(),
        }

    def _add_to_held(self):
        item = self.available_list.currentItem()
        if item is None:
            return
        row = self.available_list.indexOfTopLevelItem(item)
        symbol, name = self._available_tickers[row]
        if symbol in self._held_tickers:
            return
        clean = self._clean_name(name)
        weight = self.held_weight_input.value() / 100.0
        self._held_tickers[symbol] = weight
        self.held_list.addTopLevelItem(
            QTreeWidgetItem([clean[:30], symbol, f"{weight*100:.1f}%"])
        )
        self._emit_changed()

    def _remove_from_held(self):
        item = self.held_list.currentItem()
        if item is None:
            return
        row = self.held_list.indexOfTopLevelItem(item)
        symbol = list(self._held_tickers.keys())[row]
        del self._held_tickers[symbol]
        self.held_list.takeTopLevelItem(row)
        self._emit_changed()

    def _clear_all(self):
        self._held_tickers.clear()
        self.held_list.clear()
        self._emit_changed()

    def _emit_changed(self):
        self.tickers_changed.emit(self.get_selection())

    def _clean_name(self, name: str) -> str:
        suffixes = r"\b(p\.?l\.?c\.?|ag|se|ab|asa|nv|sa|inc|corp|ltd|llc|co)\b\.?"
        name = re.sub(r"\s*\(publ\.?\)\s*", "", name, flags=re.IGNORECASE)
        name = re.sub(rf"\s*{suffixes}\s*$", "", name, flags=re.IGNORECASE)
        return name.strip()
