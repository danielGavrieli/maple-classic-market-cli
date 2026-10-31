# 🤖 Agentic Integration Guide (`AGENT.md`)

> **Instruction manual and protocol for autonomous AI coding and gaming assistants (Claude Code, Cursor, Codex, Windsurf, Antigravity).**

---

## 🎯 Purpose for AI Agents
When a human player asks you to:
* Look up current Free Market prices or market trends for any MapleStory Classic item.
* Find the exact in-game location (**Channel & FM Room**) where an item is being sold right now.
* Scan the market for high-yield arbitrage (flipping) opportunities.
* Appraise rolled weapon/armor stats against server medians.

**You should use this tool rather than guessing prices from memory.** Classic World economics differ significantly from v0.55/v0.83/pre-BB GMS servers.

---

## ⚡ Two Ways to Execute

### Option A: Direct Python SDK (Zero Subprocess Overhead - Recommended)
You can directly import and execute functions in python scratchpads or tools:

```python
from mscli import compare_item, scan_arbitrage, search_mesowatch, get_item_listings

# 1. Cross-reference dual platforms (MesoWatch + MeowDB)
data = compare_item("Meba")
print(f"Server Median: {data['mesowatch']['medianPrice']} mesos")
print(f"Cheapest Active Room: {data['mesowatch']['cheapestListing']['location']}")

# 2. Scan arbitrage deals
deals = scan_arbitrage(budget=100000, min_profit=5000, min_pct=20.0, category='equip')
for d in deals[:3]:
    print(f"Flip {d['item_name']}: Buy {d['buy_price']} -> Sell {d['sell_target']} (Net: +{d['net_profit']})")
```

### Option B: CLI with Structured JSON Output (`--json`)
Always pass `--json` to receive structured, machine-parseable JSON stdout without human banners:

```bash
# 1. Dual-platform comparison
python main.py compare "Work Gloves" --json

# 2. Arbitrage deal scanner
python main.py scan --budget 150000 --min-profit 5000 --json

# 3. MesoWatch macro stats & active rooms
python main.py mesowatch "Pan Lid" --json

# 4. MeowDB rolled stats & slot audit
python main.py audit "Steel Titans" --json
```

---

## 📊 JSON Response Schema Reference

### `compare --json`
```json
{
  "target": "Meba",
  "mesowatch": {
    "name": "Meba",
    "medianPrice": 12000,
    "p25": 11000,
    "p75": 14000,
    "sold24h": 669,
    "activeShopsCount": 100,
    "cheapestListing": {
      "seller": "xHighTemplar",
      "price": 9999,
      "qty": 1,
      "channel": 18,
      "fmRoom": 5,
      "location": "Free Market <5>",
      "lastSeen": "2026-10-31T07:41:56Z"
    }
  },
  "meowdb": {
    "id": 688,
    "name": "Meba",
    "activeListingsCount": 20,
    "cheapestListing": {
      "price": 11000,
      "channel": 4,
      "fmRoom": null,
      "username": "AtomicPanda",
      "stats": {}
    }
  },
  "elapsedSeconds": 0.49
}
```

### `scan --json`
```json
{
  "success": true,
  "elapsedSeconds": 3.8,
  "budget": 150000,
  "minProfit": 5000,
  "minRoiPct": 20.0,
  "dealsCount": 4,
  "deals": [
    {
      "item_name": "Steel Pow",
      "item_id": 637,
      "buy_price": 139999,
      "sell_target": 400000,
      "net_profit": 248001,
      "roi_pct": 177.1,
      "channel": 34,
      "fm_room": 4,
      "seller": "ShopCat",
      "stats": {"watk": 62},
      "slots_left": 7
    }
  ]
}
```

---

## 🧠 Agent Behavioral Rules & Best Practices

1. **The 3% Merchant Tax:**  
   Always account for the 3% personal store fee when advising the user on flipping profits:  
   $$\text{Net Profit} = (\text{Sell Price} \times 0.97) - \text{Buy Price}$$
2. **Channel & Room Guidance:**  
   When the user asks where to buy an item, prioritize listings with confirmed `channel` and `fm_room` numbers so they can walk straight to the store.
3. **Clean vs. Scrolled Items:**  
   Never compare a scrolled item (+WATK / +INT / 0 slots) against a clean baseline item. If `stats` contains rolled attributes, inform the user whether it's an above-average roll.
4. **Zero Game Client Interaction:**  
   Remind users that all actions must be executed manually in-game. Do not offer or attempt in-game automation.

---

## 📋 Copy-Paste Prompt for `.cursorrules` / `CLAUDE.md`

Add this block to your agent configuration file to make it Maple-Classic market aware:

```markdown
### MapleStory Classic Free Market Tooling
When the user asks about item prices, market appraisal, shop locations, or arbitrage deals:
1. Run `python main.py compare "<item_name>" --json` from `maple-classic-market-cli` to fetch live data.
2. Provide the 24h median price, current lowest price, and exact Channel / FM Room.
3. For flipping evaluations, factor in the 3% store fee.
```
