# 🧾 HawaHisaab (`@HawaHisaab`)

![Automated Twice Daily](https://img.shields.io/badge/Automated-08%3A30%20%26%2018%3A30%20IST-black?style=flat-square)
![License: MIT](https://img.shields.io/badge/License-MIT-red.svg?style=flat-square)
![Stack](https://img.shields.io/badge/Stack-Python%20%7C%20Remotion%20%7C%20GitHub%20Actions-blue?style=flat-square)

**HawaHisaab** is a zero-server automated bot that translates live Indian Air Quality Index (AQI) telemetry into an itemized **"Involuntary Smoking Receipt"** twice a day. 

Instead of abstract AQI numbers that people scroll past, HawaHisaab calculates how many cigarettes your lungs passively smoked over the last 6 and 24 hours across **Delhi, Noida, Gurgaon, Mumbai, and Bangalore**, renders a thermal-paper challan via **Remotion**, and posts it to X and Instagram.

---

## 🔬 The Math: How AQI Becomes Cigarettes

A common error in AQI bots is dividing the US-EPA AQI score directly by 22. According to the **Berkeley Earth Study** (*Air Pollution and Cigarette Equivalence* by Richard A. Muller & Elizabeth A. Muller), **1 cigarette per day is equivalent to a raw $\text{PM}_{2.5}$ concentration of $22\text{ }\mu\text{g/m}^3$** inhaled over 24 hours.

1. **Telemetry Fetch:** `scripts/fetcher.py` queries the WAQI API (`api.waqi.info`) for the live $\text{PM}_{2.5}$ sub-index (`iaqi.pm25.v`).
2. **Piecewise Inversion:** Since WAQI returns the US-EPA sub-index rather than raw concentration, we invert the EPA piecewise linear function to recover the raw $\text{PM}_{2.5}$ density in $\mu\text{g/m}^3$.
3. **Cigarette Equivalence:**
   $$\text{Cigarettes Smoked (24h)} = \frac{\text{Raw PM}_{2.5}\text{ }(\mu\text{g/m}^3)}{22}$$

---

## 🏗️ Architecture

This project runs **100% serverless on GitHub Actions** (`ubuntu-latest`) at $0/month cost:

```text
[GitHub Actions Cron] (08:30 AM & 06:30 PM IST)
        │
        ├──► 1. scripts/fetcher.py     (Polls WAQI API -> builds receipt_props.json)
        ├──► 2. Remotion CLI           (Renders out/receipt.png & out/receipt.mp4)
        └──► 3. scripts/publisher.py   (Pushes receipt + 5-city leaderboard to X & IG)
