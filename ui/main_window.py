import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QStatusBar, QMenuBar
)
from PyQt6.QtCore import Qt


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
        self.setMinimumSize(800, 600)
        self.resize(1024, 768)

    # ── Central UI ────────────────────────────────────────────
    def _init_ui(self):
        # Central widget (required for QMainWindow)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Root layout
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(8)

        # Add your content here
        label = QLabel("Hello from MainWindow!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(label)

    # ── Menu bar ──────────────────────────────────────────────
    def _init_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&Open",  self._on_open)
        file_menu.addAction("&Save",  self._on_save)
        file_menu.addSeparator()
        file_menu.addAction("&Quit",  self.close)

        # Edit menu (add more as needed)
        edit_menu = menubar.addMenu("&Edit")
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