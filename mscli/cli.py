import argparse
import sys
import time
import json
from .utils import format_mesos, format_full_mesos
from .meowdb import search_items, get_item_listings, get_item_meta
from .mesowatch import search_mesowatch
from .arbitrage import scan_arbitrage

def compare_item(target):
    """Programmatic dual-engine comparison for AI agents and scripts."""
    mw_res = search_mesowatch(target, max_results=1)
    meow_res = search_items(target)
    
    result = {
        'target': target,
        'mesowatch': None,
        'meowdb': None
    }
    
    if mw_res:
        r = mw_res[0]
        cheapest_mw = r['listings'][0] if r['listings'] else None
        result['mesowatch'] = {
            'name': r['name'],
            'medianPrice': r['medianPrice'],
            'p25': r['p25'],
            'p75': r['p75'],
            'sold24h': r['sold24h'],
            'activeShopsCount': r['listingsCount'],
            'cheapestListing': cheapest_mw
        }
        
    if meow_res:
        m_item = meow_res[0]
        meow_listings = get_item_listings(m_item['id'])
        active_meow = [l for l in meow_listings if l.get('price') and l.get('side') == 'sell']
        active_meow.sort(key=lambda x: x['price'])
        result['meowdb'] = {
            'id': m_item['id'],
            'name': m_item['name'],
            'activeListingsCount': len(active_meow),
            'cheapestListing': active_meow[0] if active_meow else None,
            'topListings': active_meow[:5]
        }
        
    return result

def cmd_scan(args):
    t0 = time.time()
    deals = scan_arbitrage(
        budget=args.budget,
        min_profit=args.min_profit,
        min_pct=args.min_pct,
        category=args.category,
        pages=args.pages
    )
    elapsed = round(time.time() - t0, 2)

    if getattr(args, 'json', False):
        payload = {
            'success': True,
            'elapsedSeconds': elapsed,
            'budget': args.budget,
            'minProfit': args.min_profit,
            'minRoiPct': args.min_pct,
            'category': args.category,
            'dealsCount': len(deals),
            'deals': deals[:args.limit]
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"\n=======================================================")
    print(f"  Maple Classic Market Radar — Scanning Arbitrage Deals")
    print(f"=======================================================")
    print(f"Budget: {format_full_mesos(args.budget)} | Min Profit: {format_full_mesos(args.min_profit)} | Min ROI: {args.min_pct}%")
    print(f"Category: {args.category.upper()} | Pages: {args.pages}\n")

    if not deals:
        print(f"No arbitrage deals found matching your filters ({elapsed}s). Try increasing pages or lowering min-profit.")
        return

    print(f"Found {len(deals)} profitable opportunities in {elapsed}s:\n")
    for i, d in enumerate(deals[:args.limit], 1):
        stats_info = f" | Stats: {d['stats']}" if d.get('stats') else ""
        slots_info = f" | Slots: {d['slots_left']}" if d.get('slots_left') is not None else ""
        print(f"[{i}] {d['item_name']} (Ch {d['channel']} FM {d['fm_room']})")
        print(f"    Buy for: {d['buy_price']:,} mesos | Sell target: {d['sell_target']:,} mesos")
        print(f"    Net Profit: +{d['net_profit']:,} mesos ({d['roi_pct']}% ROI after 3% tax)")
        print(f"    Seller: @{d['seller']}{stats_info}{slots_info}")
        print(f"    ---------------------------------------------------")

def cmd_audit(args):
    target = args.target.strip()
    t0 = time.time()
    
    if target.isdigit():
        item_id = int(target)
        listings = get_item_listings(item_id)
        meta = get_item_meta(item_id)
        item_name = meta.get('name', f"Item #{item_id}") if meta else f"Item #{item_id}"
    else:
        results = search_items(target)
        if not results:
            if getattr(args, 'json', False):
                print(json.dumps({'success': False, 'error': f"Item '{target}' not found on MeowDB."}, indent=2))
            else:
                print(f"Item '{target}' not found on MeowDB.")
            return
        item_id = results[0]['id']
        item_name = results[0]['name']
        listings = get_item_listings(item_id)

    elapsed = round(time.time() - t0, 2)
    active = [l for l in listings if l.get('price') and l.get('side') == 'sell']
    active.sort(key=lambda x: x['price'])

    if getattr(args, 'json', False):
        payload = {
            'success': True,
            'source': 'MeowDB',
            'elapsedSeconds': elapsed,
            'itemId': item_id,
            'itemName': item_name,
            'listingsCount': len(active),
            'listings': active[:args.limit]
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"\n=======================================================")
    print(f"  MeowDB Live Audit: {item_name} (ID: {item_id})")
    print(f"=======================================================")
    print(f"Active listings: {len(active)} | Query time: {elapsed}s\n")

    if not active:
        print("No active sell listings currently available on MeowDB.")
        return

    for l in active[:args.limit]:
        ch = l.get('channel')
        fm = l.get('fmRoom')
        loc = f"Ch {ch} FM {fm}" if ch and fm else (l.get('location') or "FM")
        stats = f" | Stats: {l.get('stats')}" if l.get('stats') else ""
        slots = f" | Slots: {l.get('slotsRemaining')}" if l.get('slotsRemaining') is not None else ""
        print(f"  {l.get('price'):>10,} mesos | {loc:<15} | @{l.get('username')}{stats}{slots}")

def cmd_mesowatch(args):
    target = args.target.strip()
    t0 = time.time()
    results = search_mesowatch(target, max_results=args.results)
    elapsed = round(time.time() - t0, 2)

    if getattr(args, 'json', False):
        payload = {
            'success': True,
            'source': 'MesoWatch',
            'elapsedSeconds': elapsed,
            'target': target,
            'resultsCount': len(results),
            'results': results
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if not results:
        print(f"Item '{target}' not found on MesoWatch.")
        return

    for r in results:
        med_str = format_mesos(r['medianPrice'])
        p25_str = format_mesos(r['p25'])
        p75_str = format_mesos(r['p75'])

        print(f"\n=======================================================")
        print(f"  MesoWatch: {r['name']}")
        print(f"=======================================================")
        print(f"Market Median: {med_str} | 24h Range: [{p25_str} - {p75_str}] | Active Shops: {r['listingsCount']}")
        print(f"Query time: {elapsed}s\n")

        if not r['listings']:
            print("  No active shops currently indexed.")
            continue

        for l in r['listings'][:args.limit]:
            ch = l.get('channel')
            fm = l.get('fmRoom')
            loc = f"Ch {ch} FM {fm}" if ch and fm else (l.get('location') or "FM")
            seen = l.get('lastSeen', '').split('T')[1].replace('Z', ' UTC') if 'T' in l.get('lastSeen', '') else ''
            print(f"  {l.get('price'):>10,} mesos | {loc:<15} | @{l.get('seller'):<14} | Seen: {seen}")

def cmd_compare(args):
    target = args.target.strip()
    t0 = time.time()
    res = compare_item(target)
    elapsed = round(time.time() - t0, 2)
    res['elapsedSeconds'] = elapsed

    if getattr(args, 'json', False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    print(f"\n=======================================================")
    print(f"  Dual-Engine Market Cross-Reference: '{target}'")
    print(f"=======================================================")

    mw = res.get('mesowatch')
    if mw:
        print(f"\n[MesoWatch Global Benchmark: {mw['name']}]")
        print(f"  24h Median Price: {format_full_mesos(mw['medianPrice'])}")
        print(f"  24h Range: [{format_mesos(mw['p25'])} to {format_mesos(mw['p75'])}]")
        print(f"  24h Total Sales: {mw['sold24h'] or 'N/A'} units traded")
        print(f"  Active MesoWatch Shops: {mw['activeShopsCount']}")
        if mw['cheapestListing']:
            ch_item = mw['cheapestListing']
            loc = f"Ch {ch_item['channel']} FM {ch_item['fmRoom']}" if ch_item['channel'] and ch_item['fmRoom'] else ch_item['location']
            print(f"  Cheapest on MesoWatch: {ch_item['price']:,} mesos ({loc} @{ch_item['seller']})")
    else:
        print("\n[MesoWatch]: No match found.")

    m_db = res.get('meowdb')
    if m_db:
        print(f"\n[MeowDB Real-Time Radar: {m_item_name if 'm_item_name' in locals() else m_db['name']}]")
        print(f"  Active MeowDB Listings: {m_db['activeListingsCount']}")
        if m_db['cheapestListing']:
            c_l = m_db['cheapestListing']
            loc_m = f"Ch {c_l.get('channel')} FM {c_l.get('fmRoom')}"
            stats = f" | Stats: {c_l.get('stats')}" if c_l.get('stats') else ""
            print(f"  Cheapest on MeowDB: {c_l['price']:,} mesos ({loc_m} @{c_l.get('username')}{stats})")
    else:
        print("\n[MeowDB]: No match found.")

    print(f"\nCross-engine analysis completed in {elapsed}s.")

def main():
    parser = argparse.ArgumentParser(
        prog="mscli",
        description="Maple Classic Market CLI — Open Arbitrage Radar & Price Tracker for MapleStory Classic World"
    )
    sub = parser.parse_known_args()[0]
    subparsers = parser.add_subparsers(dest='command')

    # scan
    p_scan = subparsers.add_parser('scan', help='Scan Free Market for high-yield arbitrage opportunities')
    p_scan.add_argument('--budget', type=int, default=150000, help='Max mesos to spend per item')
    p_scan.add_argument('--min-profit', type=int, default=5000, help='Minimum net profit in mesos')
    p_scan.add_argument('--min-pct', type=float, default=20.0, help='Minimum net ROI percentage')
    p_scan.add_argument('--category', type=str, default='all', choices=['all', 'equip', 'etc', 'scroll'])
    p_scan.add_argument('--pages', type=int, default=6, help='Number of browse pages to scan')
    p_scan.add_argument('--limit', type=int, default=10, help='Max deals to display')
    p_scan.add_argument('--json', action='store_true', help='Output raw JSON for agent / programmatic consumption')
    p_scan.set_defaults(func=cmd_scan)

    # audit
    p_audit = subparsers.add_parser('audit', help='Audit specific item listings and rolled stats on MeowDB')
    p_audit.add_argument('target', type=str, help='Item name or ID')
    p_audit.add_argument('--limit', type=int, default=10, help='Number of listings to show')
    p_audit.add_argument('--json', action='store_true', help='Output raw JSON for agent / programmatic consumption')
    p_audit.set_defaults(func=cmd_audit)

    # mesowatch
    p_mw = subparsers.add_parser('mesowatch', help='Query MesoWatch live shops, channel/room and macro stats')
    p_mw.add_argument('target', type=str, help='Item name to search on MesoWatch')
    p_mw.add_argument('--results', type=int, default=3, help='Max matching items to inspect')
    p_mw.add_argument('--limit', type=int, default=10, help='Max shop listings to display')
    p_mw.add_argument('--json', action='store_true', help='Output raw JSON for agent / programmatic consumption')
    p_mw.set_defaults(func=cmd_mesowatch)

    # compare
    p_cmp = subparsers.add_parser('compare', help='Cross-reference both MeowDB and MesoWatch in one call')
    p_cmp.add_argument('target', type=str, help='Item name to compare across platforms')
    p_cmp.add_argument('--json', action='store_true', help='Output raw JSON for agent / programmatic consumption')
    p_cmp.set_defaults(func=cmd_compare)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)

if __name__ == '__main__':
    main()
