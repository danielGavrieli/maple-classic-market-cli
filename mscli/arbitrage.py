from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import os
import json
from datetime import datetime, timezone
from .meowdb import browse_listings, get_item_listings, get_item_meta

CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'items_catalog.json')
_LOCAL_CATALOG = None

def get_catalog():
    global _LOCAL_CATALOG
    if _LOCAL_CATALOG is None:
        if os.path.exists(CATALOG_PATH):
            try:
                with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
                    _LOCAL_CATALOG = json.load(f)
            except Exception:
                _LOCAL_CATALOG = {}
        else:
            _LOCAL_CATALOG = {}
    return _LOCAL_CATALOG

# Common known inactive / offline store ghosts to skip
DEFAULT_DEAD_SELLERS = {
    'donnyburger', 'branderppp', 'rhexii', 'naory1', 'boffo', 'cargoshorts'
}

# In-memory cache for dynamic base stats from official DB
_ITEM_META_CACHE = {}

def get_base_meta(item_id):
    """Fetches and caches official base stats directly from MeowDB API."""
    if not item_id:
        return None
    if item_id not in _ITEM_META_CACHE:
        meta = get_item_meta(item_id)
        _ITEM_META_CACHE[item_id] = meta.get('stats', {}) if meta else {}
    return _ITEM_META_CACHE[item_id]

def calculate_freshness(timestamp_str):
    """
    Returns (freshness_label, minutes_ago, penalty_score)
    Label: 'HOT' (<30m), 'WARM' (30m-2h), 'STALE' (>2h)
    """
    if not timestamp_str:
        return 'UNKNOWN', None, 50

    try:
        ts_clean = timestamp_str.replace('Z', '').replace('T', ' ')
        dt = datetime.strptime(ts_clean.split('.')[0], "%Y-%m-%d %H:%M:%S")
        
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        minutes_ago = max(0, int((now - dt).total_seconds() / 60))
        
        if minutes_ago <= 30:
            return 'HOT', minutes_ago, 0
        elif minutes_ago <= 120:
            return 'WARM', minutes_ago, 20
        else:
            return 'STALE', minutes_ago, 100
    except Exception:
        return 'UNKNOWN', None, 50

def evaluate_rolled_stats(item_id, item_name, current_stats, slots_left):
    """
    Dynamically compares current listing stats against official base stats from the DB.
    Returns: (is_above_avg, notes, target_multiplier)
    """
    if not current_stats or not isinstance(current_stats, dict):
        return False, "Clean / Base", 1.0

    base_stats = get_base_meta(item_id) or {}
    
    cur_watk = current_stats.get('watk', 0)
    base_watk = base_stats.get('watk', 0)

    if base_watk > 0 and cur_watk > 0:
        diff = cur_watk - base_watk
        if diff >= 2:
            return True, f"God Roll (+{diff} WATK: {cur_watk} vs base {base_watk})", 1.35
        elif diff == 1:
            return True, f"Above Avg (+1 WATK: {cur_watk} vs base {base_watk})", 1.15
        elif diff < 0:
            # Below base: heavy penalty
            return False, f"Below Avg ({diff} WATK: {cur_watk} vs base {base_watk})", 0.65
        else:
            return False, f"Exact Base ({cur_watk} WATK)", 1.0

    # For other rolled stats like magic attack, main stats, etc.
    cur_matk = current_stats.get('matk', 0)
    base_matk = base_stats.get('matk', 0)
    if base_matk > 0 and cur_matk > 0:
        diff = cur_matk - base_matk
        if diff > 0:
            return True, f"Above Avg (+{diff} MATK)", 1.15
        elif diff < 0:
            return False, f"Below Avg ({diff} MATK)", 0.70

    return False, "Standard / Unrolled", 1.0

def scan_arbitrage(budget=150000, min_profit=5000, min_pct=20.0, category='all', pages=6, max_workers=10, max_age_minutes=120, min_volume=1, job=None, max_level=None):
    type_filter = None
    if category == 'equip':
        type_filter = 'Equip'
    elif category == 'scroll':
        type_filter = 'Scroll'
    elif category == 'etc':
        type_filter = 'Etc'

    catalog = get_catalog()

    all_rows = []
    with ThreadPoolExecutor(max_workers=pages) as executor:
        futures = [executor.submit(browse_listings, page=p, max_price=budget, item_type=type_filter) for p in range(1, pages + 1)]
        for f in as_completed(futures):
            all_rows.extend(f.result())

    # Filter out dead sellers, sold out, and stale entries
    valid_candidates = []
    seen = set()
    for r in all_rows:
        seller = (r.get('username') or '').lower()
        if seller in DEFAULT_DEAD_SELLERS:
            continue
        if r.get('stock') and any(b in r['stock'].get('reasons', []) for b in ['Sold out', 'Missing']):
            continue
        if not r.get('channel') or not r.get('fmRoom'):
            continue
        
        # Calculate freshness
        ts = r.get('bumpedAt') or r.get('createdAt')
        freshness_label, minutes_ago, _ = calculate_freshness(ts)
        
        # Skip stale entries older than threshold
        if minutes_ago is not None and minutes_ago > max_age_minutes:
            continue

        row_id = r.get('id')
        if row_id in seen:
            continue
        seen.add(row_id)
        
        r['_freshness'] = freshness_label
        r['_minutes_ago'] = minutes_ago
        valid_candidates.append(r)

    # Group by item ID to fetch market depths in parallel
    unique_iids = list({r['itemId'] for r in valid_candidates})
    market_depths = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        f_map = {executor.submit(get_item_listings, iid): iid for iid in unique_iids}
        for f in as_completed(f_map):
            market_depths[f_map[f]] = f.result()

    deals = []
    for r in valid_candidates:
        buy_price = r.get('price', 0)
        if buy_price <= 0 or buy_price > budget:
            continue

        iid = r.get('itemId')
        item_name = r.get('itemName')
        item_key = (item_name or '').lower().strip()
        cat_info = catalog.get(item_key, {})

        # 1. Liquidity filter (24h sales volume from MesoWatch)
        vol_24h = cat_info.get('priceSales24h', 0)
        if min_volume > 0 and vol_24h < min_volume:
            continue

        # 2. Job filter
        if job:
            classes = [c.lower() for c in cat_info.get('classes', [])]
            if classes and job.lower() not in classes:
                continue

        # 3. Level filter
        if max_level is not None:
            lvl = cat_info.get('level')
            if lvl is not None and lvl > max_level:
                continue

        # Check rolled stat bonus multiplier dynamically via DB meta first
        is_rolled, roll_note, roll_mult = evaluate_rolled_stats(
            iid, item_name, r.get('stats'), r.get('slotsLeft')
        )

        depth = market_depths.get(iid, [])
        
        # Only compare items with matching stat tiers (clean vs clean)
        # Avoid setting a high target based on a heavily rolled or scrolled item!
        active_clean_prices = []
        for l in depth:
            if not l.get('price') or l.get('side') != 'sell':
                continue
            if (l.get('username') or '').lower() in DEFAULT_DEAD_SELLERS:
                continue
            if l.get('stock') and any(b in l['stock'].get('reasons', []) for b in ['Sold out', 'Missing']):
                continue
            
            l_stats = l.get('stats') or {}
            # If the candidate is clean/unrolled, do not use rolled (+stats) listings as benchmark
            if not is_rolled and any(v > 0 for k, v in l_stats.items() if isinstance(v, (int, float))):
                continue
            
            active_clean_prices.append(l['price'])

        # Fallback to general median price from catalog if market depth lacks clean peers
        historical_median = cat_info.get('medianPrice') or 0

        if len(active_clean_prices) >= 2:
            active_clean_prices.sort()
            bench_price = active_clean_prices[min(1, len(active_clean_prices) - 1)]
            if historical_median > 0:
                # Cap target price to not unreasonably exceed true historical median
                bench_price = min(bench_price, int(historical_median * 1.15))
        elif historical_median > 0:
            bench_price = historical_median
        else:
            continue

        # Check rolled stat bonus multiplier dynamically via DB meta
        bench_price = int(bench_price * roll_mult)

        if bench_price <= buy_price:
            continue

        # Account for 3% FM merchant tax
        net_sell = bench_price * 0.97
        net_profit = net_sell - buy_price
        pct = (net_profit / buy_price) * 100

        if net_profit >= min_profit and pct >= min_pct:
            deals.append({
                'item_name': item_name,
                'item_id': iid,
                'buy_price': buy_price,
                'sell_target': bench_price,
                'net_profit': int(net_profit),
                'roi_pct': round(pct, 1),
                'channel': r.get('channel'),
                'fm_room': r.get('fmRoom'),
                'seller': r.get('username'),
                'freshness': r.get('_freshness'),
                'minutes_ago': r.get('_minutes_ago'),
                'roll_evaluation': roll_note,
                'is_special_roll': is_rolled,
                'sales_24h': vol_24h,
                'stats': r.get('stats'),
                'slots_left': r.get('slotsLeft'),
                'market_volume': len(active_clean_prices)
            })

    # Sort primarily by freshness (HOT first) then net profit
    deals.sort(key=lambda x: (0 if x['freshness'] == 'HOT' else (1 if x['freshness'] == 'WARM' else 2), -x['net_profit']))
    return deals
