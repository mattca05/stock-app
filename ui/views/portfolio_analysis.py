from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt

from ui.constants import (
    SPACING_PA_SIDEBAR,
    MARGIN_PA_SIDEBAR,
    SIDEBAR_PA_WIDTH,
    SPACING_PA_DIVIDER,
    LABEL_PA_EXCHANGE,
    LABEL_PA_BACK,
    LABEL_PA_SELECTED,
    MARGIN_PA_ROOT,
    SPACING_PA_ROOT,
    SPACING_PA_SELECTED,
    LABEL_PA_SELECT_EXCHANGE,
)

from backend.services.exchange_services import get_all_exchanges


class PortfolioAnalysisView(QWidget):
    go_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(
            MARGIN_PA_ROOT, MARGIN_PA_ROOT, MARGIN_PA_ROOT, MARGIN_PA_ROOT
        )
        root_layout.setSpacing(SPACING_PA_ROOT)

        root_layout.addWidget(self._make_sidebar())

    # ── Sidebar ───────────────────────────────────────────────
    def _make_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(SIDEBAR_PA_WIDTH)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(
            MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR
        )
        layout.setSpacing(SPACING_PA_SIDEBAR)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Back button
        btn_back = QPushButton(LABEL_PA_BACK)
        btn_back.clicked.connect(self.go_back.emit)
        layout.addWidget(btn_back)

        # Divider
        layout.addSpacing(SPACING_PA_DIVIDER)

        # Exchange selector label
        lbl_exchange = QLabel(LABEL_PA_EXCHANGE)
        layout.addWidget(lbl_exchange)

        # Dropdown
        self.exchange_dropdown = QComboBox()
        # self.exchange_dropdown.currentTextChanged.connect(self._on_exchange_changed)
        layout.addWidget(self.exchange_dropdown)

        # Selected exchanges list label
        lbl_selected = QLabel(LABEL_PA_SELECTED)
        layout.addWidget(lbl_selected)

        # Container for selected exchange tags
        self.selected_layout = QVBoxLayout()
        self.selected_layout.setSpacing(SPACING_PA_SELECTED)
        layout.addLayout(self.selected_layout)

        # Push everything to top
        layout.addStretch()

        # Load exchanges from DB
        self._load_exchanges()

        return sidebar

    # ── Main content ──────────────────────────────────────────
    def _make_content(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR, MARGIN_PA_SIDEBAR
        )

        self.content_label = QLabel(LABEL_PA_SELECT_EXCHANGE)
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.content_label)

        return content

    def _load_exchanges(self):
        self.exchange_dropdown.addItem("-- Select Exchange --")
        for name in get_all_exchanges():
            self.exchange_dropdown.addItem(name)

    """
    # ── Slots ─────────────────────────────────────────────────
    def _on_exchange_changed(self, name: str):
        if name == "-- Select Exchange --" or name in self._selected_exchanges:
            return

        self._selected_exchanges.append(name)
        self._refresh_selected()
    """
