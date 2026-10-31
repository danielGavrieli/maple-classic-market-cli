# 🍁 Maple Classic Market CLI (`mscli`)

> **Autonomous Free Market Radar, Price Tracker & Arbitrage Scanner for MapleStory Classic World.**  
> Powered by public community market streams from **MeowDB** and **MesoWatch**.

---

## ⚠️ Disclaimer & Terms of Use (הצהרת שימוש ואחריות)

* **Use at your own risk (השימוש הינו באחריות המשתמש בלבד):**  
  This software is provided "as is" for informational and educational purposes only. The creators and contributors assume no liability for in-game trades, market fluctuations, or account actions.
* **Non-Invasive Architecture:**  
  This tool **does NOT interact with the MapleStory game client**, does NOT hook into game memory, does NOT modify game files, and does NOT automate in-game actions or gameplay.
* **Public Data Only:**  
  All market information is fetched strictly from public, web-accessible community tracking endpoints provided by third-party databases ([MeowDB](https://meowdb.com/msclassic) and [MesoWatch](https://meso.watch)).
* **Affiliation:**  
  This project is independent and is neither affiliated with nor endorsed by Nexon, MapleStory, or MapleStory Worlds.

---

## 🚀 Key Features

* **Dual-Engine Coverage:** Queries both **MeowDB** (for individual room stats and item rolls) and **MesoWatch** (for global server medians, 24h ranges, and trade volumes) simultaneously.
* **Zero Configuration:** Works out-of-the-box using the Python standard library. No complex database setup or heavy dependencies required.
* **Instant Free Market Room Locator:** Instantly reveals the exact **Channel and FM Room** for any item listed across the server.
* **Multi-Class Arbitrage Scanner:** Parallelized multi-threaded scanner that detects mispriced items across all jobs (Warrior, Mage, Thief, Bowman, Common, Scrolls, and ETC materials) with automatic 3% FM merchant tax deduction.
* **Dual-Platform Comparator:** Cross-reference any item across both platforms with a single command (`compare`).

---

## 📦 Installation & Quickstart

### Prerequisites
* Python 3.9 or higher.

### Clone & Run
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/maple-classic-market-cli.git
cd maple-classic-market-cli

# Run the CLI
python main.py --help
```

---

## 🛠️ Commands & Usage

### 1. `compare` — Dual-Engine Cross-Reference
Compare live pricing, benchmarks, and cheapest active rooms on both platforms at once:
```bash
python main.py compare "Meba"
```
**Sample Output:**
```text
=======================================================
  Dual-Engine Market Cross-Reference: 'Meba'
=======================================================

[MesoWatch Global Benchmark: Meba]
  24h Median Price: 12,000 mesos
  24h Range: [11k to 14k]
  24h Total Sales: 661 units traded
  Active MesoWatch Shops: 100
  Cheapest on MesoWatch: 9,999 mesos (Ch 18 FM 5 @xHighTemplar)

[MeowDB Real-Time Radar: Meba]
  Active MeowDB Listings: 18
  Cheapest on MeowDB: 12,000 mesos (Ch 7 FM 4 @MerchantCat)

Cross-engine analysis completed in 0.62s.
```

---

### 2. `scan` — Arbitrage Deal Radar
Scans recently opened Free Market shops for underpriced items with guaranteed profit margins:
```bash
# Scan with default filters (150k budget, 5k min profit, 20% ROI)
python main.py scan

# Scan for budget items under 50,000 mesos with high turnover
python main.py scan --budget 50000 --min-profit 3000 --min-pct 25 --category equip
```
* **Options:**
  * `--budget <mesos>`: Maximum purchase price per item (default: 150,000).
  * `--min-profit <mesos>`: Minimum net profit after 3% FM tax (default: 5,000).
  * `--min-pct <roi>`: Minimum percentage return on investment (default: 20%).
  * `--category <all|equip|etc|scroll>`: Filter by item category (default: all).
  * `--pages <num>`: Number of recent market pages to parse (default: 6).

---

### 3. `mesowatch` — Live MesoWatch Shop & Range Lookup
Lookup the lowest active shops and 24h market stats on MesoWatch:
```bash
python main.py mesowatch "Work Gloves"
python main.py mesowatch "Claw Attack"
```

---

### 4. `audit` — MeowDB Deep Item Audit
Inspect active listings, individual item rolls (WATK, STR, DEX, INT, LUK), remaining scroll slots, and seller names on MeowDB:
```bash
python main.py audit "Steel Titans"
python main.py audit "Mithril Titans"
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
