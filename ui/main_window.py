import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStatusBar,
    QMenuBar,
)
from PyQt6.QtCore import Qt
from ui.constants import (
    WINDOW_TITLE,
    WINDOW_INIT_WIDTH,
    WINDOW_INIT_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    MARGIN_ROOT,
    SPACING_ROOT,
)
from ui.views.landing import LandingView
from ui.views.portfolio_analysis import PortfolioAnalysisView
from PyQt6.QtWidgets import QStackedWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_ui()
        self._init_menu()
        self._init_statusbar()

    # ── Window setup ──────────────────────────────────────────
    def _init_window(self):
        self.setWindowTitle("My App")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_INIT_WIDTH, WINDOW_INIT_HEIGHT)
        self.raise_()  # Bring to front
        self.activateWindow()  # Force focus

    # ── Central UI ────────────────────────────────────────────
    def _init_ui(self):
        # Central widget (required for QMainWindow)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Root layout
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(
            MARGIN_ROOT, MARGIN_ROOT, MARGIN_ROOT, MARGIN_ROOT
        )
        root_layout.setSpacing(SPACING_ROOT)

        self.stack = QStackedWidget()
        self.landing = LandingView()
        self.portfolio = PortfolioAnalysisView()

        self.stack.addWidget(self.landing)  # index 0
        self.stack.addWidget(self.portfolio)  # index 1

        # Connect navigation signals
        self.landing.navigate.connect(self.stack.setCurrentIndex)
        self.portfolio.go_back.connect(lambda: self.stack.setCurrentIndex(0))
        root_layout.addWidget(self.stack)

        # Add your content here
        label = QLabel("Hello from MainWindow!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: black; background-color: white;")
        root_layout.addWidget(label)

    # ── Menu bar ──────────────────────────────────────────────
    def _init_menu(self):
        menubar = self.menuBar()
        assert menubar is not None

        # File menu
        file_menu = menubar.addMenu("&File")
        assert file_menu is not None

        file_menu.addAction("&Open", self._on_open)
        file_menu.addAction("&Save", self._on_save)
        file_menu.addSeparator()
        file_menu.addAction("&Quit", self.close)

        # Edit menu (add more as needed)
        edit_menu = menubar.addMenu("&Edit")
        assert edit_menu is not None

        edit_menu.addAction("&Preferences", self._on_preferences)

    # ── Status bar ────────────────────────────────────────────
    def _init_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

    # ── Slots (event handlers) ────────────────────────────────
    def _on_open(self):
        self.status.showMessage("Open triggered")

    def _on_save(self):
        self.status.showMessage("Save triggered")

    def _on_preferences(self):
        self.status.showMessage("Preferences triggered")
