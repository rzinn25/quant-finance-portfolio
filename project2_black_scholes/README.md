# Project 2 — Black-Scholes Options Pricer

A command-line tool that prices European call and put options using the Black-Scholes model and outputs the four main Greeks. Includes a built-in put-call parity check to verify results.

---

## The Finance

### What is an option?

An option is a contract giving the buyer the **right, but not the obligation**, to buy (call) or sell (put) an asset at a fixed price (the strike) on a fixed date (expiration). Unlike a futures contract, the buyer can simply walk away — their maximum loss is the premium paid upfront.

### What does Black-Scholes do?

The Black-Scholes model (Fischer Black & Myron Scholes, 1973) gives a **closed-form formula** for what that option is worth today, given five inputs:

| Input | Symbol | Meaning |
|-------|--------|---------|
| Spot price | S | Current market price of the underlying |
| Strike price | K | The price at which the option can be exercised |
| Time to expiry | T | Years until expiration (0.5 = 6 months) |
| Risk-free rate | r | Continuously compounded rate (e.g. US Treasury yield) |
| Volatility | σ | Annualized standard deviation of log returns |

It assumes the underlying follows **geometric Brownian motion** — log returns are normally distributed, volatility is constant, and no dividends are paid.

### The formula

Two intermediate values do the heavy lifting:

```
d1 = [ ln(S/K) + (r + σ²/2)·T ] / (σ√T)
d2 = d1 - σ√T
```

- `ln(S/K)` — log moneyness: how far above/below the strike the spot is
- `(r + σ²/2)·T` — expected drift of the log price; the σ²/2 is an Itô correction converting arithmetic to geometric drift
- `σ√T` — total uncertainty over the option's life

The prices are:

```
Call = S·N(d1) − K·e^(−rT)·N(d2)
Put  = K·e^(−rT)·N(−d2) − S·N(−d1)
```

`N(·)` is the cumulative standard normal distribution. Intuitively: each price is the present value of what you receive minus what you pay, weighted by the risk-neutral probability of exercise.

### The Greeks

Greeks measure how sensitive the option price is to each input — essential for hedging:

| Greek | Measures | Call range | Put range |
|-------|----------|------------|-----------|
| **Delta** | Price change per $1 move in S | 0 to 1 | −1 to 0 |
| **Gamma** | Delta change per $1 move in S | same for both | same |
| **Vega** | Price change per 1% move in σ | same for both | same |
| **Theta** | Price lost per calendar day | negative | negative |

### Put-Call Parity

Any arbitrage-free market must satisfy:

```
C − P = S − K·e^(−rT)
```

This relationship holds regardless of the model used — it follows purely from no-arbitrage. The pricer checks this as a built-in sanity test.

---

## How to Run

### Install dependencies

```bash
pip install scipy
```

### CLI usage

```bash
python black_scholes.py -S <spot> -K <strike> -T <years> -r <rate> --sigma <vol>
```

All rates and volatilities are expressed as decimals (`0.05` = 5%).

### Example

```bash
python black_scholes.py -S 100 -K 100 -T 1.0 -r 0.05 --sigma 0.2
```

### Example output

```
==================================================
  Black-Scholes Option Pricing
==================================================
  Inputs:
    Spot (S)        : 100.0000
    Strike (K)      : 100.0000
    Expiry (T)      : 1.0000 years
    Risk-free (r)   : 5.00%
    Volatility (σ)  : 20.00%
==================================================
  Prices:
    Call            : 10.4506
    Put             : 5.5735
==================================================
  Greeks (Call):
    Delta           : 0.6368
    Gamma           : 0.0188
    Vega (per 1%)   : 0.3752
    Theta (per day) : -0.0176
  Greeks (Put):
    Delta           : -0.3632
    Gamma           : 0.0188
    Vega (per 1%)   : 0.3752
    Theta (per day) : -0.0045
==================================================
  Put-Call Parity check (C - P = S - Ke^(-rT)):
    C - P           : 4.877058
    S - Ke^(-rT)    : 4.877058
    Satisfied       : True
==================================================
```

### Import as a module

All functions are importable for use in other scripts:

```python
from black_scholes import black_scholes_call, black_scholes_put, delta, gamma, vega, theta

call_price = black_scholes_call(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
d = delta(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='call')
```

---

*Reference: Black, F. & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities. Journal of Political Economy, 81(3), 637–654.*
