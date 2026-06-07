from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDoubleSpinBox,
    QCheckBox,
    QGroupBox,
    QToolButton,
)
from PyQt6.QtCore import Qt
from backend.services.ticker_service import TickerService
from analysis.markowitz import MarkowitzOptimizer

from backend.services.price_service import PriceService

import time
from PyQt6.QtGui import QFont


class PortfolioContent(QWidget):
    def __init__(self):
        super().__init__()
        self._ticker_service = TickerService()
        self._price_service = PriceService()
        self._current_filters: list[tuple[str, str]] = []
        self._current_tickers: list[str] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self._make_settings())
        layout.addWidget(self._make_run_button())

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.result_label = QLabel("Select filters and tickers to begin")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setFont(QFont("Courier New", 10))
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        layout.addStretch()

    # ── Settings panel ────────────────────────────────────────
    def _make_settings(self) -> QGroupBox:
        group = QGroupBox("Optimizer Settings")
        layout = QVBoxLayout(group)

        # Min / Max weight row
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel("Min Weight:"))
        self.min_weight = self._make_spinbox(0.0, 1.0, 0.00, 0.01)
        weight_layout.addWidget(self.min_weight)
        weight_layout.addWidget(QLabel("Max Weight:"))
        self.max_weight = self._make_spinbox(0.0, 1.0, 0.40, 0.01)
        weight_layout.addWidget(self.max_weight)
        layout.addLayout(weight_layout)

        # Risk free rate / Max volatility row
        risk_layout = QHBoxLayout()
        risk_layout.addWidget(QLabel("Risk Free Rate:"))
        self.risk_free_rate = self._make_spinbox(0.0, 1.0, 0.02, 0.005)
        risk_layout.addWidget(self.risk_free_rate)
        risk_layout.addWidget(QLabel("Max Volatility:"))
        self.max_volatility = self._make_spinbox(0.0, 1.0, 0.15, 0.01)
        risk_layout.addWidget(self.max_volatility)
        layout.addLayout(risk_layout)

        # ── Advanced toggle ───────────────────────────────────────
        advanced_toggle = QToolButton()
        advanced_toggle.setText("▶ Advanced")
        advanced_toggle.setCheckable(True)
        advanced_toggle.setChecked(False)
        advanced_toggle.setStyleSheet(
            "QToolButton { border: none; font-weight: bold; }"
        )
        layout.addWidget(advanced_toggle)

        # Advanced panel — hidden by default
        advanced_panel = QWidget()
        advanced_layout = QVBoxLayout(advanced_panel)
        advanced_layout.setContentsMargins(0, 0, 0, 0)

        # L2 lambda
        l2_layout = QHBoxLayout()
        l2_layout.addWidget(QLabel("L2 Lambda:"))
        self.l2_lambda = self._make_spinbox(0.0, 10.0, 0.10, 0.01)
        l2_layout.addWidget(self.l2_lambda)
        l2_layout.addStretch()
        advanced_layout.addLayout(l2_layout)

        # Checkboxes
        check_layout = QHBoxLayout()
        self.no_short = QCheckBox("No Short Selling")
        self.no_short.setChecked(True)
        self.use_ledoit_wolf = QCheckBox("Ledoit-Wolf Shrinkage")
        self.use_ledoit_wolf.setChecked(True)
        check_layout.addWidget(self.no_short)
        check_layout.addWidget(self.use_ledoit_wolf)
        advanced_layout.addLayout(check_layout)

        advanced_panel.setVisible(False)
        layout.addWidget(advanced_panel)

        # Toggle visibility on click
        advanced_toggle.toggled.connect(advanced_panel.setVisible)
        advanced_toggle.toggled.connect(
            lambda checked: advanced_toggle.setText(
                "▼ Advanced" if checked else "▶ Advanced"
            )
        )

        return group

    def _make_spinbox(
        self, min_val: float, max_val: float, default: float, step: float
    ) -> QDoubleSpinBox:
        sb = QDoubleSpinBox()
        sb.setRange(min_val, max_val)
        sb.setValue(default)
        sb.setSingleStep(step)
        sb.setDecimals(3)
        return sb

    def _make_run_button(self) -> QPushButton:
        btn = QPushButton("Run Analysis")
        btn.clicked.connect(self._run_analysis)
        return btn

    # ── Public interface ──────────────────────────────────────
    def on_filters_changed(self, filters: list[tuple[str, str]]):
        self._current_filters = filters
        count = self._ticker_service.get_ticker_count(filters)
        self.result_label.setText(f"{count} tickers match current filters")

    def on_tickers_changed(self, selection: dict):
        self._current_tickers = selection.get("available", [])
        self._held_tickers = selection.get("held", {})

    def show_message(self, text: str):
        self.result_label.setText(text)

    # ── Run ───────────────────────────────────────────────────
    def _run_analysis(self):
        if not self._current_tickers:
            self.show_message("Please select filters to define the universe.")
            return

        self.status_label.setText(
            f"Running analysis on {len(self._current_tickers)} tickers..."
        )
        from PyQt6.QtWidgets import QApplication

        QApplication.processEvents()

        from backend.services.price_service import PriceService

        prices = PriceService().get_prices_for_tickers(self._current_tickers)

        optimizer = MarkowitzOptimizer(
            min_weight=self.min_weight.value(),
            max_weight=self.max_weight.value(),
            no_short=self.no_short.isChecked(),
            risk_free_rate=self.risk_free_rate.value(),
            max_volatility=self.max_volatility.value(),
            use_ledoit_wolf=self.use_ledoit_wolf.isChecked(),
            l2_lambda=self.l2_lambda.value(),
            pinned=self._held_tickers if self._held_tickers else None,
        )

        try:
            start = time.perf_counter()
            result = optimizer.optimize(prices)
            elapsed = time.perf_counter() - start

            self.status_label.setText(f"Analysis complete — {elapsed:.2f}s")
            self._display_result(result)
        except Exception as e:
            self.status_label.setText("Analysis failed.")
            self.show_message(f"Optimization failed: {e}")

    def _display_result(self, result: dict):
        from backend.services.price_service import PriceService

        names = PriceService().get_names_for_tickers(result["tickers"])

        min_var = result["min_variance"]
        max_sh = result["max_sharpe"]

        top_10 = sorted(
            max_sh["weights"].items(),
            key=lambda x: result["individual_stats"]
            .get(x[0], {})
            .get("annual_return", 0),
            reverse=True,
        )[:10]

        lines = [
            f"Min Variance  —  Return: {min_var['expected_annual_return']:.2%}  "
            f"Vol: {min_var['annual_volatility']:.2%}  "
            f"Sharpe: {min_var['sharpe_ratio']:.2f}",
            "",
            f"Max Sharpe  —  Return: {max_sh['expected_annual_return']:.2%}  "
            f"Vol: {max_sh['annual_volatility']:.2%}  "
            f"Sharpe: {max_sh['sharpe_ratio']:.2f}",
            "",
            "── Top 10 Holdings (Max Sharpe) ──",
        ]

        for i, (symbol, weight) in enumerate(top_10, 1):
            individual = result["individual_stats"].get(symbol, {})
            annual_return = individual.get("annual_return", 0)
            name = names.get(symbol, symbol)[:20]
            lines.append(
                f"{i:>2}. {name:<20}  Weight: {weight:>6.1%}  Exp. Return: {annual_return:>8.2%}"
            )

        self.result_label.setText("\n".join(lines))
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
