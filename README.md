# 🍁 Maple Classic Market CLI (`mscli`)

[**English Guide**](#-english-documentation) | [**מדריך בעברית**](#-מדריך-למשתמש-בעברית) | [**🤖 Agentic Guide (AGENT.md)**](AGENT.md)

---

## 🇮🇱 מדריך למשתמש בעברית

כלי שורת פקודה (CLI) ו-SDK עצמאי, מהיר ומודולרי למסחר ב-**MapleStory Classic World**.  
הכלי נבנה במיוחד לשימוש של בני אדם ושל **סוכני בינה מלאכותית (AI Agents כגון Claude Code, Cursor, Codex, Windsurf)**.  
הוא מצליב בזמן אמת נתונים ציבוריים משני מאגרי המידע המובילים של המשחק: **MeowDB** ו-**MesoWatch**.

---

### ⚠️ הצהרת אחריות ואי-מעורבות במשחק (Disclaimer)
* **השימוש הינו באחריות המשתמש בלבד (Use at your own risk):** כלי זה נבנה לצורכי מידע בלבד. היוצרים והתורמים אינם נושאים באחריות על עסקאות, שינויי מחירים או פעולות בחשבון.
* **אפס התערבות במשחק (Non-Invasive):** הכלי **אינו מתחבר לקליינט המשחק**, אינו קורא או משנה זיכרון (No Memory Injection), אינו נוגע בקובצי המשחק, ואינו מבצע אוטומציה או בוטים.
* **מידע ציבורי בלבד:** כל הנתונים נמשכים מקריאות רשת פומביות של אתרי הקהילה ([MeowDB](https://meowdb.com/msclassic) ו-[MesoWatch](https://meso.watch)).
* **ללא שיוך רשמי:** הפרויקט עצמאי לחלוטין ואינו קשור או נתמך ע"י חברת Nexon או MapleStory Worlds.

---

### 🚀 יתרונות ופיצ'רים מרכזיים
1. **מנוע כפול (Dual-Engine):** חיפוש משולב גם ב-MeowDB וגם ב-MesoWatch במקביל בפחות משנייה אחת.
2. **איתור חנויות מדויק:** חשיפת הצ'אנל (`Channel`) ומספר החדר ב-FM (`FM Room`) שבו נמצא החפץ והמוכר.
3. **סורק ארביטראז' חכם:** סריקה מהירה של חנויות שנפתחו לאחרונה, איתור חפצים במחירי רצפה, וחישוב רווח נקי אוטומטי (כולל ניכוי 3% מס FM).
4. **תמיכה מלאה באייג'נטים (Agent-Ready):** פלט מובנה ב-`--json` וייבוא ישיר ב-Python ללא צורך בהרצת תהליכים נפרדים.
5. **אפס התקנות כבדות:** פועל על בסיס ספריית הסטנדרט של Python בלבד.

---

### 🤖 הפעלה ע"י סוכני AI (Cursor, Claude, Codex)
סוכני AI יכולים להפעיל את הכלי ישירות בשתי צורות:

#### 1. ייבוא ישיר כספריית Python (הכי מהיר לאייג'נטים):
```python
from mscli import compare_item, scan_arbitrage

# הצלבת מחירים מיידית
data = compare_item("Meba")
print(data['mesowatch']['medianPrice'])

# סריקת מציאות שוק
deals = scan_arbitrage(budget=150000, min_profit=5000)
```

#### 2. קבלת פלט JSON נקי ב-CLI באמצעות דגל `--json`:
```bash
python main.py compare "Meba" --json
python main.py scan --budget 100000 --json
python main.py mesowatch "Work Gloves" --json
python main.py audit "Steel Titans" --json
```
📘 **למדריך המלא לסוכני AI, סכמות ה-JSON והוראות Prompting ראו: [AGENT.md](AGENT.md)**.

---

### 📥 הוראות התקנה והפעלה (צעד אחר צעד)

#### שלב 1: דרישות מקדימות
* ודא שמותקן אצלך **Python 3.9 ומעלה** ([להורדה מאתר פייתון הרשמי](https://www.python.org/downloads/)).
  *(חשוב לסמן ב-V את האפשרות "Add Python to PATH" בעת ההתקנה).*

#### שלב 2: הורדת הפרויקט
פתח את הטרמינל והרץ:
```bash
git clone https://github.com/danielGavrieli/maple-classic-market-cli.git
cd maple-classic-market-cli
```
*(אם אין לך Git, תוכל להוריד כקובץ ZIP דרך כפתור **Code -> Download ZIP** באתר ולחלץ את התיקייה).*

#### שלב 3: הפעלה ראשונה
אין צורך בהתקנת ספריות מיוחדות! פשוט הרץ:
```bash
python main.py --help
```

---

### 🛠️ מדריך הפקודות והשימוש

#### 1. `compare` — הצלבת מחירים כפולה בין שני האתרים
```bash
python main.py compare "Meba"
```
**דוגמת פלט:**
```text
=======================================================
  Dual-Engine Market Cross-Reference: 'Meba'
=======================================================

[MesoWatch Global Benchmark: Meba]
  24h Median Price: 12,000 mesos
  24h Range: [11k to 14k]
  24h Total Sales: 669 units traded
  Active MesoWatch Shops: 100
  Cheapest on MesoWatch: 9,999 mesos (Ch 18 FM 5 @xHighTemplar)

[MeowDB Real-Time Radar: Meba]
  Active MeowDB Listings: 20
  Cheapest on MeowDB: 11,000 mesos (Ch 4 FM None @AtomicPanda)

Cross-engine analysis completed in 0.49s.
```

#### 2. `scan` — סורק מציאות וארביטראז' ב-Free Market
```bash
# סריקת ברירת מחדל (תקציב עד 150k, רווח מינימלי 5k, תשואה 20%)
python main.py scan

# סריקה ממוקדת לחפצים זולים (עד 50,000 מזוס)
python main.py scan --budget 50000 --min-profit 3000 --min-pct 25 --category equip
```

#### 3. `mesowatch` — בדיקת חנויות וטווחי מחירים ב-MesoWatch
```bash
python main.py mesowatch "Claw Attack"
python main.py mesowatch "Pan Lid"
```

#### 4. `audit` — בדיקת סטטים מדויקים ומגילות ב-MeowDB
```bash
python main.py audit "Steel Titans"
python main.py audit "Mithril Titans"
```

---

<br>

---

## 🇬🇧 English Documentation

An autonomous, ultra-fast, modular Command Line Interface (CLI) and Python SDK for **MapleStory Classic World** trading and market analysis.  
Engineered for both human merchants and **autonomous AI agents (Claude Code, Cursor, Codex, Windsurf)**.  
It cross-references real-time market streams from both **MeowDB** and **MesoWatch** in parallel.

---

### ⚠️ Disclaimer & Terms of Use
* **Use at your own risk:** This software is provided "as is" for informational and educational purposes only. Creators and contributors assume no responsibility for in-game trades, economy shifts, or account penalties.
* **Non-Invasive Architecture:** This tool **does NOT interact with the MapleStory client**, does NOT hook or inject into memory, does NOT alter game files, and does NOT perform in-game bots or automation.
* **Public Data Only:** All data is fetched strictly via public HTTP endpoints provided by independent community platforms ([MeowDB](https://meowdb.com/msclassic) and [MesoWatch](https://meso.watch)).
* **Independent Project:** This project is not affiliated with, endorsed, or sponsored by Nexon or MapleStory Worlds.

---

### 🚀 Key Features
* **Dual-Engine Architecture:** Real-time cross-referencing between MeowDB and MesoWatch in sub-second responses.
* **FM Location Finder:** Pinpoint the exact **Channel & FM Room** for any listed item and seller.
* **Automated Arbitrage Radar:** Multi-threaded parallel scanner that spots undervalued items in recently opened shops and computes net profits (including 3% FM merchant tax deduction).
* **Agent-Ready Design:** Pure machine-parseable `--json` mode + clean Python SDK interface for direct imports.
* **Zero Heavy Dependencies:** Runs entirely on the Python Standard Library.

---

### 🤖 Agentic & Autonomous Integration (AI Agents)

AI coding and gaming agents (Claude Code, Cursor, Codex, Windsurf) can interact with this repository in two ways:

#### Option 1: Direct Python Import (Zero Overhead)
```python
from mscli import compare_item, scan_arbitrage

res = compare_item("Work Gloves")
print(res["mesowatch"]["medianPrice"])
```

#### Option 2: CLI Structured JSON (`--json`)
```bash
python main.py compare "Meba" --json
python main.py scan --budget 150000 --json
python main.py mesowatch "Pan Lid" --json
python main.py audit "Steel Titans" --json
```

📘 **For the full Agentic Specification, prompt snippets, and JSON schemas, see: [AGENT.md](AGENT.md)**.

---

### 📥 Installation & Setup

#### Step 1: Requirements
* Python 3.9 or higher ([Download Python](https://www.python.org/downloads/)).
  *(Make sure "Add Python to PATH" is checked during setup).*

#### Step 2: Download & Clone
```bash
git clone https://github.com/danielGavrieli/maple-classic-market-cli.git
cd maple-classic-market-cli
```
*(Or click **Code -> Download ZIP** on GitHub and extract the folder).*

#### Step 3: Run
```bash
python main.py --help
```

---

### 🛠️ Commands & Examples

#### 1. Cross-Reference Platforms (`compare`)
```bash
python main.py compare "Meba"
```

#### 2. Arbitrage Deal Radar (`scan`)
```bash
python main.py scan --budget 150000 --min-profit 5000
```

#### 3. MesoWatch Deep Lookup (`mesowatch`)
```bash
python main.py mesowatch "Claw Attack"
```

#### 4. MeowDB Rolled Stats Audit (`audit`)
```bash
python main.py audit "Steel Titans"
```

---

## 📄 License
Distributed under the open-source [MIT License](LICENSE).
