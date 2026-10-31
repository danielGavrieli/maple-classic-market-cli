from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
from .meowdb import browse_listings, get_item_listings

# Common known inactive / offline store ghosts to skip
DEFAULT_DEAD_SELLERS = {
    'donnyburger', 'branderppp', 'rhexii', 'naory1', 'boffo', 'cargoshorts'
}

def scan_arbitrage(budget=150000, min_profit=5000, min_pct=20.0, category='all', pages=6, max_workers=10):
    type_filter = None
    if category == 'equip':
        type_filter = 'Equip'
    elif category == 'scroll':
        type_filter = 'Scroll'
    elif category == 'etc':
        type_filter = 'Etc'

    all_rows = []
    with ThreadPoolExecutor(max_workers=pages) as executor:
        futures = [executor.submit(browse_listings, page=p, max_price=budget, item_type=type_filter) for p in range(1, pages + 1)]
        for f in as_completed(futures):
            all_rows.extend(f.result())

    # Filter out dead sellers and sold out
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
        
        row_id = r.get('id')
        if row_id in seen:
            continue
        seen.add(row_id)
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
        depth = market_depths.get(iid, [])
        active_prices = [
            l['price'] for l in depth
            if l.get('price') and l.get('side') == 'sell'
            and (l.get('username') or '').lower() not in DEFAULT_DEAD_SELLERS
            and not (l.get('stock') and any(b in l['stock'].get('reasons', []) for b in ['Sold out', 'Missing']))
        ]

        if len(active_prices) < 2:
            continue

        active_prices.sort()
        # Realistic sell target: slightly below median or second lowest active
        bench_price = active_prices[min(2, len(active_prices) - 1)]
        if bench_price <= buy_price:
            continue

        # Account for 3% FM merchant tax
        net_sell = bench_price * 0.97
        net_profit = net_sell - buy_price
        pct = (net_profit / buy_price) * 100

        if net_profit >= min_profit and pct >= min_pct:
            deals.append({
                'item_name': r.get('itemName'),
                'item_id': iid,
                'buy_price': buy_price,
                'sell_target': bench_price,
                'net_profit': int(net_profit),
                'roi_pct': round(pct, 1),
                'channel': r.get('channel'),
                'fm_room': r.get('fmRoom'),
                'seller': r.get('username'),
                'stats': r.get('stats'),
                'slots_left': r.get('slotsRemaining'),
                'market_volume': len(active_prices)
            })

    deals.sort(key=lambda x: x['net_profit'], reverse=True)
    return deals
