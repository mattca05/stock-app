from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from ui.constants import SPACING_LANDING


class LandingView(QWidget):
    navigate = pyqtSignal(int)  # Emits the index to navigate to

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(SPACING_LANDING)

        # Left — Portfolio Analysis
        btn_portfolio = self._make_tile("Portfolio\nAnalysis")
        btn_portfolio.clicked.connect(lambda: self.navigate.emit(1))

        # Middle — placeholder
        btn_middle = self._make_tile("TBD")

        # Right — placeholder
        btn_right = self._make_tile("TBD")

        layout.addWidget(btn_portfolio)
        layout.addWidget(btn_middle)
        layout.addWidget(btn_right)

    def _make_tile(self, label: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedSize(150, 150)
        return btn
