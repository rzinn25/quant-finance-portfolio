# Quant Finance Portfolio

A portfolio of quantitative finance projects built while learning derivatives, 
algorithmic trading, and financial modeling.

---

## Project 01 — Derivatives Payoff Visualizer

### What it does
Visualizes the profit/loss at expiration for three fundamental derivative instruments:
- **Futures contracts** — locked-in price, unlimited upside and downside
- **Call options** — right to buy, downside capped at premium paid
- **Put options** — right to sell, downside capped at premium paid

### Why it matters
Payoff diagrams are the foundation of all derivatives trading. Every complex 
strategy is just a combination of these basic building blocks. Understanding 
them visually and mathematically is step one for any quant.

### Key concepts
| Instrument | Your right | Max loss | Profits when |
|------------|-----------|----------|--------------|
| Futures | Obligation to buy/sell | Unlimited | Price moves your way |
| Call Option | Right to buy | Premium paid | Price goes up |
| Put Option | Right to sell | Premium paid | Price goes down |

### How to run
```bash
pip install -r requirements.txt
python payoff_visualizer.py
```

### Output
![Payoff Diagrams](payoff_diagrams.png)

---

*Built while working through Hull's Options, Futures & Other Derivatives*