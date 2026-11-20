"""Compare a lagged signal with a deliberately leaky same-period signal."""

from __future__ import annotations

import math


def _compound(returns: list[float], positions: list[int]) -> float:
    value = 1.0
    for ret, position in zip(returns, positions):
        value *= 1.0 + ret * position
    return value - 1.0


def backtest_returns(prices: list[float]) -> dict:
    if len(prices) < 3:
        raise ValueError("prices must contain at least three finite positive values")
    if any(isinstance(x, (str, bytes, bool)) for x in prices):
        raise ValueError("prices must be numeric values, not strings or booleans")
    try:
        prices = [float(x) for x in prices]
    except (TypeError, ValueError) as exc:
        raise ValueError("prices must be numeric values") from exc
    if any(not math.isfinite(x) or x <= 0 for x in prices):
        raise ValueError("prices must contain at least three finite positive values")
    returns = [(prices[i] / prices[i - 1]) - 1.0 for i in range(1, len(prices))]
    # At the close of t-1, decide whether to hold during t-1 -> t using only t-2 -> t-1.
    safe_positions = [0] + [int(returns[i - 1] > 0) for i in range(1, len(returns))]
    # Deliberately wrong: choose the position using the same return it then earns.
    lookahead_positions = [int(ret > 0) for ret in returns]
    return {
        "observations": len(returns),
        "safe_signal_observations": max(0, len(returns) - 1),
        "lagged_signal_total_return": _compound(returns, safe_positions),
        "lookahead_total_return": _compound(returns, lookahead_positions),
        "safe_positions": safe_positions,
        "lookahead_positions": lookahead_positions,
        "per_period_returns": returns,
    }


def run(seed: int = 42) -> dict:
    result = backtest_returns([100, 90, 80, 100, 130, 120])
    return {
        "evidence_type": "synthetic",
        "seed": seed,
        **result,
        "limitations": [
            "Prices are a tiny hand-authored fixture, not market data.",
            "The example illustrates signal timing only; it excludes fees, slippage, and portfolio constraints.",
        ],
    }
