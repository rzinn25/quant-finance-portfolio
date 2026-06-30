# =============================================================================
# Derivatives Payoff Visualizer
# =============================================================================
# This script visualizes the profit/loss at expiration for three fundamental
# derivative instruments: Futures, Call Options, and Put Options.
#
# WHY THIS MATTERS:
# Understanding payoff diagrams is the foundation of all derivatives trading.
# Every complex strategy is just a combination of these basic building blocks.
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt


def future_payoff(S, F):
    """
    Calculate the payoff of a LONG futures contract at expiration.

    WHY: A futures contract locks in a price F today for delivery later.
    At expiration, you profit if the asset price S is above F,
    and lose if it's below — you're obligated either way.

    Args:
        S (array): Range of possible asset prices at expiration
        F (float): The agreed futures price (set when contract was made)

    Returns:
        array: Profit/loss at each possible expiration price
    """
    return S - F


def call_option_payoff(S, K, premium):
    """
    Calculate the payoff of a LONG call option at expiration.

    WHY: A call option gives you the RIGHT (not obligation) to BUY
    at price K. If the asset price S is above K, you exercise it
    and profit. If S is below K, you simply don't exercise — your
    only loss is the premium you paid upfront.

    Args:
        S (array): Range of possible asset prices at expiration
        K (float): Strike price — the price you have the right to buy at
        premium (float): The cost of buying the option upfront

    Returns:
        array: Profit/loss at each possible expiration price
    """
    # np.maximum(S - K, 0) means: take the profit if positive, else 0
    # We subtract the premium because that was the cost to enter the trade
    return np.maximum(S - K, 0) - premium


def put_option_payoff(S, K, premium):
    """
    Calculate the payoff of a LONG put option at expiration.

    WHY: A put option gives you the RIGHT (not obligation) to SELL
    at price K. If the asset price S drops below K, you profit
    because you can sell at the higher price K. If S is above K,
    you don't exercise — you only lose the premium.

    Args:
        S (array): Range of possible asset prices at expiration
        K (float): Strike price — the price you have the right to sell at
        premium (float): The cost of buying the option upfront

    Returns:
        array: Profit/loss at each possible expiration price
    """
    # np.maximum(K - S, 0) means: profit if price fell, else 0
    return np.maximum(K - S, 0) - premium


def plot_payoffs(F=100, K=100, call_premium=10, put_premium=10):
    """
    Plot payoff diagrams for futures, call, and put side by side.

    WHY SIDE BY SIDE: Comparing them together makes the key difference
    obvious — futures have unlimited upside AND downside, while options
    cap your downside at the premium paid.

    Args:
        F (float): Futures price
        K (float): Strike price for options
        call_premium (float): Cost of the call option
        put_premium (float): Cost of the put option
    """
    # Create a range of possible stock prices at expiration
    # WHY 50 to 150: Centers around our strike/futures price of 100
    S = np.linspace(50, 150, 500)

    # Calculate payoffs for each instrument
    futures = future_payoff(S, F)
    call = call_option_payoff(S, K, call_premium)
    put = put_option_payoff(S, K, put_premium)

    # --- Plotting ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Derivatives Payoff at Expiration", fontsize=16, fontweight="bold")

    payoffs = [
        (futures, "Long Futures", "blue",  f"Locked in price: ${F}"),
        (call,    "Long Call",    "green", f"Strike: ${K} | Premium: ${call_premium}"),
        (put,     "Long Put",     "red",   f"Strike: ${K} | Premium: ${put_premium}"),
    ]

    for ax, (payoff, title, color, subtitle) in zip(axes, payoffs):
        ax.plot(S, payoff, color=color, linewidth=2)

        # Draw horizontal line at zero to clearly show profit vs loss zones
        ax.axhline(y=0, color="black", linestyle="--", linewidth=0.8)

        # Shade profit zone green, loss zone red — makes it instantly readable
        ax.fill_between(S, payoff, 0, where=(payoff > 0), alpha=0.1, color="green", label="Profit")
        ax.fill_between(S, payoff, 0, where=(payoff < 0), alpha=0.1, color="red",   label="Loss")

        ax.set_title(f"{title}\n{subtitle}", fontsize=11)
        ax.set_xlabel("Asset Price at Expiration ($)")
        ax.set_ylabel("Profit / Loss ($)")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("payoff_diagrams.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Chart saved as payoff_diagrams.png")


# =============================================================================
# Entry point
# WHY __main__: This ensures the code only runs when you execute this file
# directly — not if another script imports it as a module.
# =============================================================================
if __name__ == "__main__":
    plot_payoffs(
        F=100,            # Futures price locked in at $100
        K=100,            # Options strike price at $100
        call_premium=10,  # Paid $10 upfront for the call
        put_premium=10    # Paid $10 upfront for the put
    )