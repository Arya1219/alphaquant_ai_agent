import pandas as pd
import numpy as np
from typing import Any


# ── Strategy Parameters (mirrors the backtester) ──────────────────────────────
IMPULSE_MIN_LONG   = 0.0013
IMPULSE_MAX_LONG   = 0.0027
BREAKOUT_MIN_LONG  = 0.019
BREAKOUT_MAX_LONG  = 0.05
RETRACE_MAX_LONG   = 0.03

IMPULSE_MIN_SHORT  = 0.02
IMPULSE_MAX_SHORT  = 0.07
BREAKOUT_MIN_SHORT = 0.058
BREAKOUT_MAX_SHORT = 0.063
RETRACE_MAX_SHORT  = 0.01

WINDOW_THRESHOLD   = 40
TCS                = 0.0015          # transaction cost per side


class QuantTradingToolset:
    """AI Agent Toolset for the Impulse Flow Alpha quant strategy."""

    # ── 1. Strategy explanation ───────────────────────────────────────────────
    async def explain_strategy(self, strategy_text: str = "") -> str:
        """
        Return a plain-English explanation of Impulse Flow Alpha.

        Args:
            strategy_text: Optional extra context / code snippet to include.

        Returns:
            Structured explanation string.
        """
        try:
            explanation = (
                "=== Impulse Flow Alpha — Strategy Explanation ===\n\n"
                "CONCEPT\n"
                "-------\n"
                "The strategy exploits a 3-phase market structure that repeats across\n"
                "trending assets:\n\n"
                "  1. IMPULSE   – A sharp directional price move that signals intent.\n"
                "  2. CONSOLIDATION – A shallow pullback / pause that holds structure.\n"
                "  3. BREAKOUT  – A continuation move that confirms trend resumption.\n\n"
                "LONG SETUP (buy signal)\n"
                "-----------------------\n"
                f"  • Impulse bar return : {IMPULSE_MIN_LONG*100:.2f}% – {IMPULSE_MAX_LONG*100:.2f}%\n"
                f"  • Max retrace        : {RETRACE_MAX_LONG*100:.1f}%  (structure must hold)\n"
                f"  • Breakout range     : {BREAKOUT_MIN_LONG*100:.1f}% – {BREAKOUT_MAX_LONG*100:.1f}%\n\n"
                "SHORT SETUP (sell signal)\n"
                "-------------------------\n"
                f"  • Impulse bar return : -{IMPULSE_MAX_SHORT*100:.1f}% – -{IMPULSE_MIN_SHORT*100:.1f}%\n"
                f"  • Max retrace        : {RETRACE_MAX_SHORT*100:.1f}%  (structure must hold)\n"
                f"  • Breakout range     : -{BREAKOUT_MAX_SHORT*100:.2f}% – -{BREAKOUT_MIN_SHORT*100:.2f}%\n\n"
                "EXECUTION\n"
                "---------\n"
                f"  • Lookback window    : {WINDOW_THRESHOLD} bars\n"
                f"  • Transaction cost   : {TCS*100:.2f}% per trade\n"
                "  • Positions          : Long / Short / Flat (no leverage assumed)\n\n"
            )
            if strategy_text.strip():
                explanation += f"ADDITIONAL CONTEXT PROVIDED\n---------------------------\n{strategy_text}\n"
            return explanation
        except Exception as e:
            return f"Error explaining strategy: {str(e)}"

    # ── 2. Performance analysis ───────────────────────────────────────────────
    async def analyze_performance(
        self,
        net_return: float = 4307.12,
        annualised_return: float = 157.32,
        sharpe: float = 1.9659,
        sortino: float = 3.0001,
        calmar: float = 5.1007,
        max_drawdown: float = 30.84,
        total_days: int = 1462,
        trade_events: int = 28,
    ) -> str:
        """
        Interpret a set of backtest performance metrics.

        Args:
            net_return        : Total net return in %.
            annualised_return : CAGR in %.
            sharpe            : Sharpe ratio (annualised, rf=0).
            sortino           : Sortino ratio.
            calmar            : Calmar ratio (CAGR / Max DD).
            max_drawdown      : Maximum drawdown in %.
            total_days        : Number of trading days.
            trade_events      : Total OPEN + CLOSE events logged.

        Returns:
            Structured performance interpretation.
        """
        try:
            # Qualitative rating helpers
            def rate(val, thresholds, labels):
                for t, l in zip(thresholds, labels):
                    if val >= t:
                        return l
                return labels[-1]

            sharpe_label  = rate(sharpe,  [2, 1.5, 1],  ["Excellent", "Good", "Acceptable", "Poor"])
            sortino_label = rate(sortino, [3, 2, 1],    ["Excellent", "Good", "Acceptable", "Poor"])
            calmar_label  = rate(calmar,  [3, 2, 1],    ["Excellent", "Good", "Acceptable", "Poor"])
            dd_label      = rate(100 - max_drawdown, [80, 70, 60], ["Low risk", "Moderate risk", "High risk", "Very high risk"])

            analysis = (
                "=== Performance Analysis — Impulse Flow Alpha ===\n\n"
                "RETURN METRICS\n"
                "--------------\n"
                f"  Net Return        : {net_return:.2f}%  (4 years, BTC-USDT daily)\n"
                f"  Annualised Return : {annualised_return:.2f}% CAGR\n"
                f"  Total Days        : {total_days}  |  Trade Events : {trade_events}\n\n"
                "RISK-ADJUSTED METRICS\n"
                "---------------------\n"
                f"  Sharpe  Ratio : {sharpe:.4f}  → {sharpe_label}\n"
                f"  Sortino Ratio : {sortino:.4f}  → {sortino_label}\n"
                f"  Calmar  Ratio : {calmar:.4f}  → {calmar_label}\n\n"
                "DRAWDOWN\n"
                "--------\n"
                f"  Max Drawdown  : {max_drawdown:.2f}%  → {dd_label}\n\n"
                "INTERPRETATION\n"
                "--------------\n"
                "  • The net return of ~4300% over 4 years is exceptional; however,\n"
                "    this figure is in-sample and must be treated as an upper bound.\n"
                "  • A Sharpe > 1.96 indicates the strategy earns well per unit of risk.\n"
                "  • A Sortino of 3.0 shows downside volatility is tightly controlled.\n"
                "  • A Calmar of 5.1 means each % of drawdown 'buys' ~5.1% annual return.\n"
                "  • Only 28 trade events over 1462 days = ~1 trade per 2 months.\n"
                "    This selectivity reduces overtrading noise but also limits sample size.\n"
            )
            return analysis
        except Exception as e:
            return f"Error analyzing performance: {str(e)}"

    # ── 3. Risk evaluation ────────────────────────────────────────────────────
    async def evaluate_risk(self) -> str:
        """
        Summarise stress-test results and forward-looking risks.

        Returns:
            Structured risk evaluation string.
        """
        try:
            risk_report = (
                "=== Risk Evaluation — Impulse Flow Alpha ===\n\n"
                "STRESS TEST RESULTS\n"
                "-------------------\n\n"
                "1. Trade Connectivity Test (20% Random Dropout)\n"
                "   • Avg simulated annualised return : ~114%  (vs original 157%)\n"
                "   • Alpha is spread across trades; not concentrated in a few lucky ones.\n"
                "   • Strategy remains highly profitable even with 20% trade removal.\n\n"
                "2. Monte-Carlo Shuffle (2 000 iterations)\n"
                "   • Actual Max DD : 30.84%  |  Avg shuffled DD : 41.74%\n"
                "   • 95% VaR DD    : 55.70%\n"
                "   • The real sequence produces lower drawdown than most random orderings,\n"
                "     suggesting the strategy's timing genuinely reduces risk.\n\n"
                "3. Gaussian Diffusion Baseline Test\n"
                "   • Actual return exceeds the 95% band of a pure drift+volatility process.\n"
                "   • Confirms the equity curve is NOT explainable by luck alone.\n\n"
                "4. Parameter Perturbation Test (±5% on all params)\n"
                "   • Most parameters show zero sensitivity (same PnL).\n"
                "   • impulse_max_long +5%  → return improves (+457 pp); acceptable.\n"
                "   • breakout_max_short +5% → return falls (~-562 pp); most sensitive param.\n"
                "   • Overall: strategy is robust; breakout_max_short warrants attention.\n\n"
                "FORWARD-LOOKING RISKS\n"
                "---------------------\n"
                "  ⚠ Small sample size (14 round-trips) — difficult to generalise.\n"
                "  ⚠ In-sample only — no walk-forward or out-of-sample validation shown.\n"
                "  ⚠ BTC-specific — performance on other assets is untested.\n"
                "  ⚠ Live slippage / partial fills not modelled (only flat TCS = 0.15%).\n"
                "  ⚠ Regime dependency — strategy may underperform in ranging markets.\n\n"
                "CONCLUSION\n"
                "----------\n"
                "  The strategy passes all four stress tests and shows genuine statistical\n"
                "  edge. Key next steps: walk-forward validation, live paper trading, and\n"
                "  testing on additional crypto pairs (ETH, SOL) to confirm generalisability.\n"
            )
            return risk_report
        except Exception as e:
            return f"Error evaluating risk: {str(e)}"

    # ── 4. Live signal generation from raw OHLC ───────────────────────────────
    async def generate_signal(self, ohlc_data: list[dict]) -> str:
        """
        Run the Impulse Flow Alpha signal engine on supplied OHLC data and
        return the signal for the latest bar.

        Args:
            ohlc_data: List of dicts with keys Date, Open, High, Low, Close
                       (and optionally Volume), sorted oldest-first.

        Returns:
            Signal report string: LONG / SHORT / FLAT + brief rationale.
        """
        try:
            if not ohlc_data:
                return "Error: No OHLC data provided."

            df = pd.DataFrame(ohlc_data)
            required = {"Open", "High", "Low", "Close"}
            if not required.issubset(df.columns):
                missing = required - set(df.columns)
                return f"Error: Missing columns: {missing}"

            # Clean
            for col in ["Open", "High", "Low", "Close"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df.loc[df[col] <= 0, col] = np.nan
            df[["Open","High","Low","Close"]] = df[["Open","High","Low","Close"]].ffill()
            df = df.dropna(subset=["Open","High","Low","Close"]).reset_index(drop=True)

            if len(df) < 5:
                return "Error: Need at least 5 bars to generate a signal."

            p = df["Close"].values
            i = len(p) - 1          # evaluate signal for the latest bar
            signal = 0
            trigger_info = "No pattern matched within lookback window."

            for j in range(max(1, i - WINDOW_THRESHOLD), i - 3):
                r = (p[j] - p[j - 1]) / p[j - 1]

                # LONG
                if IMPULSE_MIN_LONG <= r <= IMPULSE_MAX_LONG:
                    retrace  = np.min(p[j + 1:i]) / p[j] - 1
                    breakout = p[i] / p[j] - 1
                    if retrace >= -RETRACE_MAX_LONG and BREAKOUT_MIN_LONG <= breakout <= BREAKOUT_MAX_LONG:
                        signal = 1
                        trigger_info = (
                            f"Impulse bar index {j} | r={r*100:.3f}% | "
                            f"retrace={retrace*100:.2f}% | breakout={breakout*100:.2f}%"
                        )
                        break

                # SHORT
                if -IMPULSE_MAX_SHORT <= r <= -IMPULSE_MIN_SHORT:
                    retrace  = np.max(p[j + 1:i]) / p[j] - 1
                    breakout = p[i] / p[j] - 1
                    if retrace <= RETRACE_MAX_SHORT and -BREAKOUT_MAX_SHORT <= breakout <= -BREAKOUT_MIN_SHORT:
                        signal = -1
                        trigger_info = (
                            f"Impulse bar index {j} | r={r*100:.3f}% | "
                            f"retrace={retrace*100:.2f}% | breakout={breakout*100:.2f}%"
                        )
                        break

            label  = {1: "LONG ▲", -1: "SHORT ▼", 0: "FLAT —"}[signal]
            latest = p[-1]

            report = (
                "=== Impulse Flow Alpha — Signal Report ===\n\n"
                f"  Bars analysed     : {len(df)}\n"
                f"  Latest Close      : {latest:.4f}\n"
                f"  Signal            : {label}\n"
                f"  Trigger detail    : {trigger_info}\n\n"
                "  Note: This signal is generated from the supplied data only.\n"
                "  Always confirm with live price feeds before execution.\n"
            )
            return report
        except Exception as e:
            return f"Error generating signal: {str(e)}"

    # ── 5. Full backtest on supplied CSV data ─────────────────────────────────
    async def run_backtest(
        self,
        csv_rows: list[dict],
        base_cap: float = 1_000_000.0,
    ) -> str:
        """
        Run the complete Impulse Flow Alpha backtest on user-supplied OHLC data
        and return a full performance report with all key metrics.

        Args:
            csv_rows : List of dicts with at minimum keys:
                       Date, Open, High, Low, Close (Volume optional).
                       Rows must be in chronological order (oldest first).
            base_cap : Starting capital in USD (default 1,000,000).

        Returns:
            Structured backtest report string with all performance metrics,
            trade log summary, and qualitative interpretation.

        Raises:
            Returns an error string (never raises) so the A2A layer stays clean.
        """
        try:
            # ── 5.1  Validate input ───────────────────────────────────────────
            if not csv_rows:
                return "Error: No data provided. Supply a list of OHLC dicts."

            if base_cap <= 0:
                return "Error: base_cap must be a positive number."

            df = pd.DataFrame(csv_rows)

            required_cols = {"Date", "Open", "High", "Low", "Close"}
            missing = required_cols - set(df.columns)
            if missing:
                return f"Error: Missing required columns: {sorted(missing)}"

            # ── 5.2  Clean & prepare ──────────────────────────────────────────
            df = df.sort_values("Date").reset_index(drop=True)

            for col in ["Open", "High", "Low", "Close"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df.loc[df[col] <= 0, col] = np.nan
            df[["Open", "High", "Low", "Close"]] = (
                df[["Open", "High", "Low", "Close"]].ffill()
            )

            if "Volume" in df.columns:
                df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0)
                vol_std = df["Volume"].std()
                df["Volume_norm"] = (
                    (df["Volume"] - df["Volume"].mean()) / vol_std
                    if vol_std > 0 else 0.0
                )

            df = df.dropna(subset=["Open", "High", "Low", "Close"]).reset_index(drop=True)

            n = len(df)
            if n < 10:
                return (
                    f"Error: Only {n} clean bars available after preprocessing. "
                    "Need at least 10 bars to run a meaningful backtest."
                )

            # ── 5.3  Signal engine (identical logic to backtester notebook) ───
            def _daily_signal(prices: np.ndarray, i: int) -> float:
                if i < 5:
                    return 0.0
                for j in range(max(1, i - WINDOW_THRESHOLD), i - 3):
                    r = (prices[j] - prices[j - 1]) / prices[j - 1]

                    # LONG
                    if IMPULSE_MIN_LONG <= r <= IMPULSE_MAX_LONG:
                        retrace  = np.min(prices[j + 1:i]) / prices[j] - 1
                        breakout = prices[i] / prices[j] - 1
                        if (retrace >= -RETRACE_MAX_LONG and
                                BREAKOUT_MIN_LONG <= breakout <= BREAKOUT_MAX_LONG):
                            return 1.0

                    # SHORT
                    if -IMPULSE_MAX_SHORT <= r <= -IMPULSE_MIN_SHORT:
                        retrace  = np.max(prices[j + 1:i]) / prices[j] - 1
                        breakout = prices[i] / prices[j] - 1
                        if (retrace <= RETRACE_MAX_SHORT and
                                -BREAKOUT_MAX_SHORT <= breakout <= -BREAKOUT_MIN_SHORT):
                            return -1.0

                return 0.0

            # ── 5.4  Backtest loop ────────────────────────────────────────────
            p       = df["Close"].values
            dates   = df["Date"].values
            capital = base_cap
            equity  = [capital]

            position   = 0          # 1=long, -1=short, 0=flat
            open_price = None
            open_date  = None
            trades     = []

            for i in range(n):
                price  = p[i]
                signal = _daily_signal(p, i)

                if signal != 0 and signal != position:

                    # Close existing position
                    if position != 0:
                        pnl = (price / open_price - 1) * position - TCS
                        capital *= (1 + pnl)
                        trades.append({
                            "type"     : "CLOSE",
                            "date"     : dates[i],
                            "price"    : round(float(price), 6),
                            "direction": "LONG" if position == 1 else "SHORT",
                            "pnl_pct"  : round(pnl * 100, 4),
                            "capital"  : round(float(capital), 2),
                        })
                        position = 0

                    # Open new position (not on last bar)
                    if i < n - 1:
                        open_price = price
                        open_date  = dates[i]
                        position   = int(signal)
                        trades.append({
                            "type"     : "OPEN",
                            "date"     : open_date,
                            "price"    : round(float(open_price), 6),
                            "direction": "LONG" if position == 1 else "SHORT",
                            "pnl_pct"  : 0.0,
                            "capital"  : round(float(capital), 2),
                        })

                # Track unrealised equity
                if position != 0:
                    unrealised = (price / open_price - 1) * position
                    equity.append(capital * (1 + unrealised))
                else:
                    equity.append(capital)

            # Force-close any open position at end
            if position != 0:
                final_price = p[-1]
                pnl = (final_price / open_price - 1) * position - TCS
                capital *= (1 + pnl)
                trades.append({
                    "type"     : "CLOSE-FINAL",
                    "date"     : dates[-1],
                    "price"    : round(float(final_price), 6),
                    "direction": "LONG" if position == 1 else "SHORT",
                    "pnl_pct"  : round(pnl * 100, 4),
                    "capital"  : round(float(capital), 2),
                })
            equity.append(capital)

            # ── 5.5  Compute metrics ──────────────────────────────────────────
            equity_arr    = np.array(equity)
            daily_returns = equity_arr[1:] / equity_arr[:-1] - 1
            n_days        = len(daily_returns)

            total_return = (capital / base_cap - 1) * 100

            annualised = (
                ((capital / base_cap) ** (365.0 / n_days) - 1) * 100
                if n_days > 0 else float("nan")
            )

            # Max drawdown
            peak   = equity_arr[0]
            max_dd = 0.0
            for val in equity_arr:
                if val > peak:
                    peak = val
                dd = (peak - val) / peak
                if dd > max_dd:
                    max_dd = dd
            max_dd_pct = max_dd * 100

            # Sharpe (rf = 0, annualised with sqrt(365))
            mean_ret = float(np.mean(daily_returns))
            std_ret  = float(np.std(daily_returns, ddof=1))
            sharpe   = (mean_ret / std_ret * np.sqrt(365)) if std_ret > 1e-12 else float("nan")

            # Sortino
            down = daily_returns[daily_returns < 0]
            if len(down) > 1:
                d_std   = float(np.std(down, ddof=1))
                sortino = (mean_ret / d_std * np.sqrt(365)) if d_std > 1e-12 else float("inf")
            elif len(down) == 0:
                sortino = float("inf")
            else:
                sortino = float("nan")

            # Calmar
            calmar = (annualised / max_dd_pct) if max_dd_pct > 1e-12 else float("inf")

            # Trade breakdown
            closed_trades = [t for t in trades if t["type"] in ("CLOSE", "CLOSE-FINAL")]
            n_trades      = len(closed_trades)
            winning       = [t for t in closed_trades if t["pnl_pct"] > 0]
            losing        = [t for t in closed_trades if t["pnl_pct"] <= 0]
            win_rate      = (len(winning) / n_trades * 100) if n_trades > 0 else 0.0
            gross_profit  = sum(t["pnl_pct"] for t in winning)
            gross_loss    = sum(t["pnl_pct"] for t in losing)
            profit_factor = (
                abs(gross_profit / gross_loss) if abs(gross_loss) > 1e-12 else float("inf")
            )
            avg_win  = (gross_profit / len(winning))  if winning else 0.0
            avg_loss = (gross_loss   / len(losing))   if losing  else 0.0

            # Qualitative ratings
            def _rate(val, thresholds, labels):
                for t, l in zip(thresholds, labels):
                    if val >= t:
                        return l
                return labels[-1]

            sharpe_label  = _rate(sharpe,  [2, 1.5, 1], ["Excellent", "Good", "Acceptable", "Poor"])
            sortino_label = _rate(sortino, [3, 2, 1],   ["Excellent", "Good", "Acceptable", "Poor"])
            calmar_label  = _rate(calmar,  [3, 2, 1],   ["Excellent", "Good", "Acceptable", "Poor"])
            dd_label      = _rate(
                100 - max_dd_pct, [80, 70, 60],
                ["Low risk", "Moderate risk", "High risk", "Very high risk"]
            )

            # ── 5.6  Format report ────────────────────────────────────────────
            report = (
                "=== Impulse Flow Alpha — Full Backtest Report ===\n\n"

                "INPUT PARAMETERS\n"
                "----------------\n"
                f"  Bars loaded       : {n}\n"
                f"  Date range        : {dates[0]}  to  {dates[-1]}\n"
                f"  Starting capital  : ${base_cap:,.2f}\n"
                f"  Transaction cost  : {TCS*100:.2f}% per side\n\n"

                "RETURN METRICS\n"
                "--------------\n"
                f"  Net Return        : {total_return:.4f}%\n"
                f"  Final Capital     : ${capital:,.2f}\n"
                f"  Annualised Return : {annualised:.4f}% CAGR\n"
                f"  Total Days        : {n_days}\n\n"

                "RISK-ADJUSTED METRICS\n"
                "---------------------\n"
                f"  Sharpe  Ratio     : {sharpe:.4f}   -> {sharpe_label}\n"
                f"  Sortino Ratio     : {sortino:.4f}   -> {sortino_label}\n"
                f"  Calmar  Ratio     : {calmar:.4f}   -> {calmar_label}\n"
                f"  Max Drawdown      : {max_dd_pct:.4f}%  -> {dd_label}\n\n"

                "TRADE STATISTICS\n"
                "----------------\n"
                f"  Total Trades      : {n_trades}  (round-trips)\n"
                f"  Total Events      : {len(trades)}  (OPEN + CLOSE entries)\n"
                f"  Winning Trades    : {len(winning)}\n"
                f"  Losing  Trades    : {len(losing)}\n"
                f"  Win Rate          : {win_rate:.2f}%\n"
                f"  Gross Profit      : {gross_profit:.4f}%\n"
                f"  Gross Loss        : {gross_loss:.4f}%\n"
                f"  Profit Factor     : {profit_factor:.4f}\n"
                f"  Avg Win           : {avg_win:.4f}%\n"
                f"  Avg Loss          : {avg_loss:.4f}%\n\n"

                "TRADE LOG (last 10 events)\n"
                "--------------------------\n"
            )

            # Append last 10 trade events
            last_trades = trades[-10:] if len(trades) >= 10 else trades
            for t in last_trades:
                report += (
                    f"  [{t['type']:<12}] {t['date']}  {t['direction']:<5} "
                    f"@ {t['price']:>12.4f}  PnL: {t['pnl_pct']:>8.4f}%  "
                    f"Capital: ${t['capital']:>14,.2f}\n"
                )

            report += (
                "\nINTERPRETATION\n"
                "--------------\n"
            )

            # Dynamic interpretation based on actual computed values
            if total_return > 1000:
                report += "  * Exceptional net return — verify for in-sample overfitting.\n"
            elif total_return > 100:
                report += "  * Strong net return relative to buy-and-hold benchmarks.\n"
            else:
                report += "  * Moderate net return; consider further optimisation.\n"

            if sharpe >= 1.5:
                report += "  * Sharpe >= 1.5 confirms robust risk-adjusted performance.\n"
            else:
                report += "  * Sharpe below 1.5; risk-adjusted returns need improvement.\n"

            if max_dd_pct > 40:
                report += "  * Drawdown > 40% is high; position sizing should be reduced.\n"
            elif max_dd_pct > 20:
                report += "  * Drawdown is moderate; acceptable for crypto strategies.\n"
            else:
                report += "  * Low drawdown indicates tight risk management.\n"

            if n_trades < 15:
                report += (
                    f"  * Only {n_trades} round-trips — small sample; "
                    "statistical significance is limited.\n"
                )

            report += (
                "\n  NOTE: All results are in-sample. Out-of-sample validation\n"
                "  and live paper trading are essential before deployment.\n"
            )

            return report

        except Exception as e:
            return f"Error running backtest: {str(e)}"

    # ── Tool registry ─────────────────────────────────────────────────────────
    def get_tools(self) -> dict[str, Any]:
        """Return all callable tools keyed by name."""
        return {
            "explain_strategy"   : self.explain_strategy,
            "analyze_performance": self.analyze_performance,
            "evaluate_risk"      : self.evaluate_risk,
            "generate_signal"    : self.generate_signal,
            "run_backtest"       : self.run_backtest,
        }
