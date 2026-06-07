from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QStackedWidget,
    QWidget,
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Callable
from backend.services.exchange_manager import ExchangeManager
from ui.constants import (
    SIDEBAR_PA_WIDTH,
    MARGIN_PA_SIDEBAR,
    SPACING_PA_SIDEBAR,
    SPACING_PA_DIVIDER,
    SIDEBAR_PA_LIST_HEIGHT,
    DROPDOWN_PA_HEIGHT,
    LABEL_PA_BACK,
    LABEL_PA_EXCHANGE,
    LABEL_PA_COUNTRIES,
    LABEL_PA_SECTOR,
    LABEL_PA_SELECTED,
)


class FilterSidebar(QFrame):
    go_back = pyqtSignal()
    filters_changed = pyqtSignal(list)  # emits list[tuple[str, str]]

    def __init__(self):
        super().__init__()
        self._selected_filters: list[tuple[str, str]] = []
        self._exchange_manager = ExchangeManager()
        self._init_ui()

    def _init_ui(self):
        self.setFixedWidth(SIDEBAR_PA_WIDTH)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR
        )
        layout.setSpacing(SPACING_PA_SIDEBAR)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self._create_button(LABEL_PA_BACK, self.go_back.emit))
        layout.addSpacing(SPACING_PA_DIVIDER)
        layout.addWidget(self._create_tabs())

        layout.addWidget(QLabel(LABEL_PA_SELECTED))
        self.selected_list = QListWidget()
        self.selected_list.setFixedHeight(SIDEBAR_PA_LIST_HEIGHT)
        layout.addWidget(self.selected_list)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._create_button("Remove", self._remove_selected))
        btn_layout.addWidget(self._create_button("Clear All", self._clear_filters))
        btn_layout.addWidget(self._create_button("Undo", self._undo_filter))
        layout.addLayout(btn_layout)

        layout.addStretch()
        self._load_filters()

    def _create_tabs(self) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)

        self.filter_stack = QStackedWidget()
        self.filter_stack.addWidget(self._create_list("exchange", DROPDOWN_PA_HEIGHT))
        self.filter_stack.addWidget(self._create_list("country", DROPDOWN_PA_HEIGHT))
        self.filter_stack.addWidget(self._create_list("sector", DROPDOWN_PA_HEIGHT))

        self.exchange_list = self.filter_stack.widget(0)
        self.country_list = self.filter_stack.widget(1)
        self.sector_list = self.filter_stack.widget(2)

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
        self.filters_changed.emit(self._selected_filters)

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
