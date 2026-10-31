# 🍁 Maple Classic Market CLI (`mscli`)

[**English Guide**](#-english-documentation) | [**מדריך בעברית**](#-מדריך-למשתמש-בעברית)

---

## 🇮🇱 מדריך למשתמש בעברית

כלי שורת פקודה (CLI) עצמאי, מהיר ומודולרי למסחר ב-**MapleStory Classic World**.  
הכלי מצליב בזמן אמת נתונים ציבוריים משני מאגרי המידע המובילים של המשחק: **MeowDB** ו-**MesoWatch**.

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
3. **סורק ארביטראז' חכם:** סריקה מהירה של חנויות שנפתחו לאחרונה, איתור חפצים שנמכרים במחירי רצפה מתחת למחיר השוק, וחישוב רווח נקי אוטומטי (כולל ניכוי 3% מס FM).
4. **אפס התקנות כבדות:** פועל על בסיס ספריית הסטנדרט של Python בלבד. ללא צורך בהתקנת חבילות צד שלישי או בסיסי נתונים.

---

### 📥 הוראות התקנה והפעלה (צעד אחר צעד)

#### שלב 1: דרישות מקדימות
* ודא שמותקן אצלך **Python 3.9 ומעלה** ([להורדה מאתר פייתון הרשמי](https://www.python.org/downloads/)).
  *(חשוב לסמן ב-V את האפשרות "Add Python to PATH" בעת ההתקנה).*

#### שלב 2: הורדת הפרויקט
פתח את הטרמינל (Command Prompt / PowerShell / Terminal) והרץ:
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
משווה בין נתוני MesoWatch ל-MeowDB ומציג את החדר והמחיר הכי זול שקיים:
```bash
python main.py compare "Meba"
python main.py compare "Work Gloves"
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
סורק את כל החנויות האחרונות שנפתחו ומאתר חפצים שנמכרים במחיר זול משמעותית ממחיר השוק:
```bash
# סריקת ברירת מחדל (תקציב עד 150k, רווח מינימלי 5k, תשואה 20%)
python main.py scan

# סריקה ממוקדת לחפצים זולים (עד 50,000 מזוס)
python main.py scan --budget 50000 --min-profit 3000 --min-pct 25 --category equip
```
* **פרמטרים לבחירה:**
  * `--budget <מספר>`: תקציב מקסימלי לקניית חפץ (ברירת מחדל: 150,000).
  * `--min-profit <מספר>`: רווח נקי מינימלי במזוס לאחר מס (ברירת מחדל: 5,000).
  * `--min-pct <אחוז>`: אחוז רווח מינימלי להשקעה (ROI).
  * `--category <all|equip|etc|scroll>`: סינון לפי סוג חפץ (ציוד, מגילות, חומרי Etc).
  * `--pages <מספר>`: כמות עמודי שוק לסריקה מהירה (ברירת מחדל: 6).

#### 3. `mesowatch` — בדיקת חנויות וטווחי מחירים ב-MesoWatch
מציג את החנויות הפעילות ביותר, מיקומים ומחירי חציון:
```bash
python main.py mesowatch "Claw Attack"
python main.py mesowatch "Pan Lid"
```

#### 4. `audit` — בדיקת סטטים מדויקים ומגילות ב-MeowDB
בודק סטטים ספציפיים שגולגלו על נשקים ושריונות (WATK, STR, DEX, INT, LUK וסלוטים פנויים):
```bash
python main.py audit "Steel Titans"
python main.py audit "Mithril Titans"
```

---

<br>

---

## 🇬🇧 English Documentation

An autonomous, ultra-fast, modular Command Line Interface (CLI) for **MapleStory Classic World** trading and market analysis.  
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
* **Zero Heavy Dependencies:** Runs entirely on the Python Standard Library. No external packages or SQL databases required.

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
python main.py compare "Work Gloves"
```

#### 2. Arbitrage Deal Radar (`scan`)
```bash
# Default scan (150k budget, 5k min net profit, 20% ROI)
python main.py scan

# Targeted scan for items under 50,000 mesos
python main.py scan --budget 50000 --min-profit 3000 --min-pct 25 --category equip
```

#### 3. MesoWatch Deep Lookup (`mesowatch`)
```bash
python main.py mesowatch "Claw Attack"
python main.py mesowatch "Pan Lid"
```

#### 4. MeowDB Rolled Stats Audit (`audit`)
```bash
python main.py audit "Steel Titans"
python main.py audit "Mithril Titans"
```

---

## 📄 License
Distributed under the open-source [MIT License](LICENSE).
