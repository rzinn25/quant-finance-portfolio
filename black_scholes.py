"""
Black-Scholes Option Pricing Model

The Black-Scholes model (1973) gives a closed-form solution for the fair price
of European-style options, assuming:
  - The underlying follows geometric Brownian motion (log-normal returns)
  - No dividends during the option's life
  - Constant risk-free rate and volatility
  - No transaction costs or arbitrage
  - Continuous trading is possible

Variables:
  S     — current spot price of the underlying asset
  K     — strike price (the agreed price at expiration)
  T     — time to expiration in years (e.g. 0.5 = 6 months)
  r     — continuously compounded risk-free interest rate (annualized)
  sigma — annualized volatility of the underlying's log returns
"""

import argparse
import math
from scipy.stats import norm  # type: ignore


# ---------------------------------------------------------------------------
# Core helper
# ---------------------------------------------------------------------------

def compute_d1_d2(S: float, K: float, T: float, r: float, sigma: float) -> tuple[float, float]:
    """Compute the Black-Scholes d1 and d2 intermediate values.

    d1 captures the risk-adjusted probability that the option ends in-the-money,
    accounting for drift (r + σ²/2) and diffusion (σ√T).
    d2 = d1 - σ√T strips out the variance adjustment, giving the risk-neutral
    probability of finishing in-the-money under the equivalent martingale measure.

    Args:
        S:     Spot price of the underlying.
        K:     Strike price of the option.
        T:     Time to expiration in years (must be > 0).
        r:     Continuously compounded risk-free rate (annualized).
        sigma: Annualized volatility of log returns (must be > 0).

    Returns:
        A tuple (d1, d2).

    Raises:
        ValueError: If T or sigma are non-positive.
    """
    if T <= 0:
        raise ValueError(f"Time to expiration T must be positive, got {T}")
    if sigma <= 0:
        raise ValueError(f"Volatility sigma must be positive, got {sigma}")

    # ln(S/K): the log moneyness — positive when the spot is above the strike.
    log_moneyness = math.log(S / K)

    # (r + σ²/2)·T: drift of the log price over the option's lifetime.
    # The σ²/2 term is the Itô correction that converts arithmetic to log drift.
    drift = (r + 0.5 * sigma ** 2) * T

    # σ√T: the standard deviation of log returns over the option's lifetime.
    vol_sqrt_t = sigma * math.sqrt(T)

    d1 = (log_moneyness + drift) / vol_sqrt_t
    d2 = d1 - vol_sqrt_t

    return d1, d2


# ---------------------------------------------------------------------------
# Option pricing
# ---------------------------------------------------------------------------

def black_scholes_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Price a European call option using the Black-Scholes formula.

    A call gives the holder the right (not obligation) to BUY the underlying
    at strike K at expiration. The BS call price is:

        C = S · N(d1) - K · e^(-rT) · N(d2)

    Intuition:
      - S · N(d1)          : the expected value of receiving the asset,
                             conditional on exercise, discounted to today.
      - K · e^(-rT) · N(d2): the present value of paying the strike K,
                             weighted by the risk-neutral probability of exercise.

    Args:
        S:     Spot price of the underlying.
        K:     Strike price of the option.
        T:     Time to expiration in years.
        r:     Continuously compounded risk-free rate (annualized).
        sigma: Annualized volatility of log returns.

    Returns:
        Theoretical fair value of the call option.
    """
    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    # N(d1), N(d2): cumulative standard normal probabilities
    call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return call_price


def black_scholes_put(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Price a European put option using the Black-Scholes formula.

    A put gives the holder the right (not obligation) to SELL the underlying
    at strike K at expiration. The BS put price is:

        P = K · e^(-rT) · N(-d2) - S · N(-d1)

    This is derived directly from call-put parity:
        P = C - S + K · e^(-rT)

    Equivalently (using N(-x) = 1 - N(x)):
      - K · e^(-rT) · N(-d2): PV of receiving the strike, weighted by
                               probability the put expires in-the-money.
      - S · N(-d1)           : expected cost of delivering the asset,
                               conditional on exercise.

    Args:
        S:     Spot price of the underlying.
        K:     Strike price of the option.
        T:     Time to expiration in years.
        r:     Continuously compounded risk-free rate (annualized).
        sigma: Annualized volatility of log returns.

    Returns:
        Theoretical fair value of the put option.
    """
    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price


# ---------------------------------------------------------------------------
# Greeks (first-order sensitivities)
# ---------------------------------------------------------------------------

def delta(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """Compute option delta — sensitivity of price to a $1 move in the underlying.

    Delta is the hedge ratio: holding delta shares of the underlying per short
    option creates a locally risk-free portfolio (the Black-Scholes replication).
      - Call delta ∈ (0, 1): rises toward 1 as the call goes deeper in-the-money.
      - Put  delta ∈ (-1, 0): rises toward 0 as the put goes deeper out-of-the-money.

    Args:
        S:           Spot price.
        K:           Strike price.
        T:           Time to expiration in years.
        r:           Risk-free rate (annualized).
        sigma:       Volatility (annualized).
        option_type: 'call' or 'put'.

    Returns:
        Delta of the option.

    Raises:
        ValueError: If option_type is not 'call' or 'put'.
    """
    d1, _ = compute_d1_d2(S, K, T, r, sigma)

    if option_type == "call":
        return norm.cdf(d1)
    elif option_type == "put":
        # Put-call delta parity: delta_put = delta_call - 1
        return norm.cdf(d1) - 1
    else:
        raise ValueError(f"option_type must be 'call' or 'put', got '{option_type}'")


def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Compute option gamma — rate of change of delta per $1 move in the underlying.

    Gamma is identical for calls and puts (put-call parity). High gamma means
    delta hedges need frequent rebalancing (higher replication cost). Gamma peaks
    when the option is at-the-money and close to expiration.

    Args:
        S:     Spot price.
        K:     Strike price.
        T:     Time to expiration in years.
        r:     Risk-free rate (annualized).
        sigma: Volatility (annualized).

    Returns:
        Gamma of the option.
    """
    d1, _ = compute_d1_d2(S, K, T, r, sigma)

    # N'(d1): standard normal PDF evaluated at d1
    return norm.pdf(d1) / (S * sigma * math.sqrt(T))


def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Compute option vega — sensitivity of price to a 1-point (100 bp) move in vol.

    Vega is identical for calls and puts. Long options are always long vega
    (rising volatility increases option value, since it widens the payoff distribution
    without capping the upside). Returned per 1% move in sigma for readability.

    Args:
        S:     Spot price.
        K:     Strike price.
        T:     Time to expiration in years.
        r:     Risk-free rate (annualized).
        sigma: Volatility (annualized).

    Returns:
        Vega per 1% change in volatility.
    """
    d1, _ = compute_d1_d2(S, K, T, r, sigma)

    # Raw vega is per unit sigma; divide by 100 to express per 1% vol move
    return S * norm.pdf(d1) * math.sqrt(T) / 100


def theta(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """Compute option theta — time decay (value lost per calendar day).

    Theta is almost always negative for long options: as time passes, the option
    has less time for the underlying to move in the desired direction, so the
    time-value component erodes. This is the cost of holding the optionality.

    Args:
        S:           Spot price.
        K:           Strike price.
        T:           Time to expiration in years.
        r:           Risk-free rate (annualized).
        sigma:       Volatility (annualized).
        option_type: 'call' or 'put'.

    Returns:
        Theta expressed per calendar day (divide annualized value by 365).

    Raises:
        ValueError: If option_type is not 'call' or 'put'.
    """
    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    # Common term: the rate at which diffusion erodes value
    diffusion_decay = -(S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
    discount_factor = K * math.exp(-r * T)

    if option_type == "call":
        annual_theta = diffusion_decay - r * discount_factor * norm.cdf(d2)
    elif option_type == "put":
        annual_theta = diffusion_decay + r * discount_factor * norm.cdf(-d2)
    else:
        raise ValueError(f"option_type must be 'call' or 'put', got '{option_type}'")

    # Convert from per-year to per-day
    return annual_theta / 365


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Black-Scholes European option pricer with Greeks",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-S", type=float, required=True, help="Spot price of the underlying")
    parser.add_argument("-K", type=float, required=True, help="Strike price of the option")
    parser.add_argument("-T", type=float, required=True, help="Time to expiration in years")
    parser.add_argument("-r", type=float, required=True, help="Risk-free rate (e.g. 0.05 for 5%%)")
    parser.add_argument("--sigma", type=float, required=True, help="Volatility (e.g. 0.2 for 20%%)")
    return parser


def main() -> None:
    """Run the Black-Scholes pricer from the command line and print a summary."""
    parser = _build_parser()
    args = parser.parse_args()

    S, K, T, r, sigma = args.S, args.K, args.T, args.r, args.sigma

    call = black_scholes_call(S, K, T, r, sigma)
    put  = black_scholes_put(S, K, T, r, sigma)

    # Verify put-call parity: C - P = S - K·e^(-rT)
    # This must hold in any arbitrage-free market.
    parity_lhs = call - put
    parity_rhs = S - K * math.exp(-r * T)

    print(f"\n{'='*50}")
    print(f"  Black-Scholes Option Pricing")
    print(f"{'='*50}")
    print(f"  Inputs:")
    print(f"    Spot (S)        : {S:.4f}")
    print(f"    Strike (K)      : {K:.4f}")
    print(f"    Expiry (T)      : {T:.4f} years")
    print(f"    Risk-free (r)   : {r*100:.2f}%")
    print(f"    Volatility (σ)  : {sigma*100:.2f}%")
    print(f"{'='*50}")
    print(f"  Prices:")
    print(f"    Call            : {call:.4f}")
    print(f"    Put             : {put:.4f}")
    print(f"{'='*50}")
    print(f"  Greeks (Call):")
    print(f"    Delta           : {delta(S, K, T, r, sigma, 'call'):.4f}")
    print(f"    Gamma           : {gamma(S, K, T, r, sigma):.4f}")
    print(f"    Vega (per 1%)   : {vega(S, K, T, r, sigma):.4f}")
    print(f"    Theta (per day) : {theta(S, K, T, r, sigma, 'call'):.4f}")
    print(f"  Greeks (Put):")
    print(f"    Delta           : {delta(S, K, T, r, sigma, 'put'):.4f}")
    print(f"    Gamma           : {gamma(S, K, T, r, sigma):.4f}")
    print(f"    Vega (per 1%)   : {vega(S, K, T, r, sigma):.4f}")
    print(f"    Theta (per day) : {theta(S, K, T, r, sigma, 'put'):.4f}")
    print(f"{'='*50}")
    print(f"  Put-Call Parity check (C - P = S - Ke^(-rT)):")
    print(f"    C - P           : {parity_lhs:.6f}")
    print(f"    S - Ke^(-rT)    : {parity_rhs:.6f}")
    print(f"    Satisfied       : {math.isclose(parity_lhs, parity_rhs, rel_tol=1e-9)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
