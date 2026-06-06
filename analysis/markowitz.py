import numpy as np
from scipy.optimize import minimize
from datetime import date

try:
    from sklearn.covariance import LedoitWolf
    HAVE_SKLEARN = True
except Exception:
    HAVE_SKLEARN = False

TRADING_DAYS = 252


class MarkowitzOptimizer:

    def __init__(
        self,
        min_weight: float = 0.0,
        max_weight: float = 1.0,
        no_short: bool = True,
        risk_free_rate: float = 0.02,
        max_volatility: float | None = None,
        use_ledoit_wolf: bool = True,
        l2_lambda: float = 0.0,
    ):
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.no_short = no_short
        self.risk_free_rate = risk_free_rate
        self.max_volatility = max_volatility
        self.use_ledoit_wolf = use_ledoit_wolf
        self.l2_lambda = l2_lambda

    def optimize(self, prices: dict[str, list[tuple[date, float]]]) -> dict:
        series = self._build_returns(prices)
        if len(series) < 2:
            raise ValueError("Need at least 2 tickers for Markowitz optimization.")

        matrix, tickers = self._align_matrix(series)
        mu, cov = self._estimate_mu_cov(matrix)

        n = len(tickers)
        self._check_feasible(n)
        bounds = self._make_bounds(n)

        w_minvar = self._min_variance(mu, cov, bounds)
        w_maxsh  = self._max_sharpe(mu, cov, bounds)
        frontier = self._efficient_frontier(mu, cov, bounds)

        def stats(w):
            ret = float(w @ mu)
            vol = float(np.sqrt(w @ cov @ w))
            sharpe = (ret - self.risk_free_rate) / vol if vol > 0 else 0.0
            return round(ret, 4), round(vol, 4), round(sharpe, 4)

        r_min, v_min, s_min = stats(w_minvar)
        r_max, v_max, s_max = stats(w_maxsh)

        individual_stats = {
            t: {
                "annual_return":     round(float(mu[i]), 4),
                "annual_volatility": round(float(np.sqrt(cov[i, i])), 4),
            }
            for i, t in enumerate(tickers)
        }

        return {
            "tickers": tickers,
            "min_variance": {
                "weights":               {t: round(float(w), 4) for t, w in zip(tickers, w_minvar)},
                "expected_annual_return": r_min,
                "annual_volatility":      v_min,
                "sharpe_ratio":           s_min,
            },
            "max_sharpe": {
                "weights":               {t: round(float(w), 4) for t, w in zip(tickers, w_maxsh)},
                "expected_annual_return": r_max,
                "annual_volatility":      v_max,
                "sharpe_ratio":           s_max,
            },
            "efficient_frontier": frontier,
            "individual_stats":   individual_stats,
            "settings": {
                "min_weight":      self.min_weight,
                "max_weight":      self.max_weight,
                "no_short":        self.no_short,
                "risk_free_rate":  self.risk_free_rate,
                "max_volatility":  self.max_volatility,
                "use_ledoit_wolf": self.use_ledoit_wolf and HAVE_SKLEARN,
                "l2_lambda":       self.l2_lambda,
            },
        }

    # ── Data preparation ──────────────────────────────────────

    def _build_returns(
        self, prices: dict[str, list[tuple[date, float]]]
    ) -> dict[str, list[float]]:
        series = {}
        for ticker, price_data in prices.items():
            if len(price_data) < 2:
                continue
            px = [p for _, p in price_data]
            returns = [
                np.log(px[i] / px[i - 1])
                for i in range(1, len(px))
            ]
            series[ticker] = returns
        return series

    def _align_matrix(
        self, series: dict[str, list[float]]
    ) -> tuple[np.ndarray, list[str]]:
        tickers = list(series.keys())
        min_len = min(len(v) for v in series.values())
        matrix  = np.array([series[t][-min_len:] for t in tickers]).T  # (days, n)
        return matrix, tickers

    def _estimate_mu_cov(
        self, matrix: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        mu_daily = matrix.mean(axis=0)
        mu = mu_daily * TRADING_DAYS

        if self.use_ledoit_wolf and HAVE_SKLEARN:
            cov_daily = LedoitWolf().fit(matrix).covariance_
        else:
            cov_daily = np.cov(matrix.T)

        cov = cov_daily * TRADING_DAYS
        return mu, cov

    # ── Bounds & constraints ──────────────────────────────────

    def _make_bounds(self, n: int) -> list[tuple[float, float]]:
        lo = max(0.0 if self.no_short else -1.0, self.min_weight)
        hi = min(1.0, self.max_weight)
        return [(lo, hi)] * n

    def _check_feasible(self, n: int):
        if n * self.min_weight > 1.0 + 1e-12:
            raise ValueError(
                f"Infeasible: {n} tickers × min_weight {self.min_weight} = "
                f"{n * self.min_weight:.3f} > 1.0"
            )
        if n * self.max_weight < 1.0 - 1e-12:
            raise ValueError(
                f"Infeasible: {n} tickers × max_weight {self.max_weight} = "
                f"{n * self.max_weight:.3f} < 1.0"
            )

    def _make_constraints(
        self, mu: np.ndarray | None = None, target_return: float | None = None
    ) -> list[dict]:
        cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
        if target_return is not None and mu is not None:
            cons.append({
                "type": "eq",
                "fun": lambda w, mu=mu, tr=target_return: (w @ mu) - tr
            })
        return cons

    def _l2_penalty(self, w: np.ndarray) -> float:
        return float(self.l2_lambda * np.sum(w ** 2)) if self.l2_lambda > 0 else 0.0

    # ── Solvers ───────────────────────────────────────────────

    def _min_variance(
        self, mu: np.ndarray, cov: np.ndarray, bounds: list
    ) -> np.ndarray:
        n  = len(mu)
        w0 = np.ones(n) / n

        def objective(w):
            return float(w @ cov @ w) + self._l2_penalty(w)

        def grad(w):
            w = np.asarray(w)
            return 2.0 * (cov @ w) + (2.0 * self.l2_lambda * w if self.l2_lambda > 0 else 0.0)

        result = minimize(
            objective, w0,
            method="SLSQP",
            jac=grad,
            bounds=bounds,
            constraints=self._make_constraints(),
            options={"maxiter": 300, "ftol": 1e-9},
        )
        if not result.success:
            raise RuntimeError(f"Min variance failed: {result.message}")
        return result.x

    def _max_sharpe(
        self, mu: np.ndarray, cov: np.ndarray, bounds: list
    ) -> np.ndarray:
        n  = len(mu)
        w0 = np.ones(n) / n
        rf = self.risk_free_rate

        def objective(w):
            ret = float(w @ mu)
            vol = float(np.sqrt(w @ cov @ w))
            sharpe = (ret - rf) / vol if vol > 0 else -np.inf
            return -sharpe + self._l2_penalty(w)

        cons = self._make_constraints()
        if self.max_volatility is not None:
            cons.append({
                "type": "ineq",
                "fun": lambda w, cov=cov: self.max_volatility - np.sqrt(w @ cov @ w)
            })

        result = minimize(
            objective, w0,
            method="SLSQP",
            bounds=bounds,
            constraints=cons,
            options={"maxiter": 300, "ftol": 1e-9},
        )
        if not result.success:
            raise RuntimeError(f"Max Sharpe failed: {result.message}")
        return result.x

    def _efficient_frontier(
        self, mu: np.ndarray, cov: np.ndarray, bounds: list, points: int = 40
    ) -> list[dict]:
        n      = len(mu)
        w0     = np.ones(n) / n
        frontier = []

        for target_r in np.linspace(float(mu.min()), float(mu.max()), points):
            result = minimize(
                lambda w: float(np.sqrt(w @ cov @ w)) + self._l2_penalty(w),
                w0,
                method="SLSQP",
                bounds=bounds,
                constraints=self._make_constraints(mu=mu, target_return=target_r),
                options={"maxiter": 300, "ftol": 1e-9},
            )
            if result.success:
                vol = float(np.sqrt(result.x @ cov @ result.x))
                frontier.append({
                    "return":     round(float(target_r), 4),
                    "volatility": round(vol, 4),
                })

        return frontier