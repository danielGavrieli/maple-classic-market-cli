import argparse
import sys
import time
from .utils import format_mesos, format_full_mesos
from .meowdb import search_items, get_item_listings, get_item_meta
from .mesowatch import search_mesowatch
from .arbitrage import scan_arbitrage

def cmd_scan(args):
    print(f"\n=======================================================")
    print(f"  Maple Classic Market Radar — Scanning Arbitrage Deals")
    print(f"=======================================================")
    print(f"Budget: {format_full_mesos(args.budget)} | Min Profit: {format_full_mesos(args.min_profit)} | Min ROI: {args.min_pct}%")
    print(f"Category: {args.category.upper()} | Pages: {args.pages}\n")

    t0 = time.time()
    deals = scan_arbitrage(
        budget=args.budget,
        min_profit=args.min_profit,
        min_pct=args.min_pct,
        category=args.category,
        pages=args.pages
    )
    elapsed = round(time.time() - t0, 2)

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
    
    # Check if target is numeric itemId
    if target.isdigit():
        item_id = int(target)
        listings = get_item_listings(item_id)
        meta = get_item_meta(item_id)
        item_name = meta.get('name', f"Item #{item_id}") if meta else f"Item #{item_id}"
    else:
        results = search_items(target)
        if not results:
            print(f"Item '{target}' not found on MeowDB.")
            return
        item_id = results[0]['id']
        item_name = results[0]['name']
        listings = get_item_listings(item_id)

    elapsed = round(time.time() - t0, 2)
    active = [l for l in listings if l.get('price') and l.get('side') == 'sell']
    active.sort(key=lambda x: x['price'])

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
    print(f"\n=======================================================")
    print(f"  Dual-Engine Market Cross-Reference: '{target}'")
    print(f"=======================================================")
    
    t0 = time.time()
    mw_res = search_mesowatch(target, max_results=1)
    meow_res = search_items(target)
    
    # 1. MesoWatch metrics
    if mw_res:
        r = mw_res[0]
        print(f"\n[MesoWatch Global Benchmark: {r['name']}]")
        print(f"  24h Median Price: {format_full_mesos(r['medianPrice'])}")
        print(f"  24h Range: [{format_mesos(r['p25'])} to {format_mesos(r['p75'])}]")
        print(f"  24h Total Sales: {r['sold24h'] or 'N/A'} units traded")
        print(f"  Active MesoWatch Shops: {r['listingsCount']}")
        if r['listings']:
            cheapest_mw = r['listings'][0]
            loc = f"Ch {cheapest_mw['channel']} FM {cheapest_mw['fmRoom']}" if cheapest_mw['channel'] and cheapest_mw['fmRoom'] else cheapest_mw['location']
            print(f"  Cheapest on MesoWatch: {cheapest_mw['price']:,} mesos ({loc} @{cheapest_mw['seller']})")
    else:
        print("\n[MesoWatch]: No match found.")

    # 2. MeowDB listings
    if meow_res:
        m_item = meow_res[0]
        meow_listings = get_item_listings(m_item['id'])
        active_meow = [l for l in meow_listings if l.get('price') and l.get('side') == 'sell']
        active_meow.sort(key=lambda x: x['price'])
        print(f"\n[MeowDB Real-Time Radar: {m_item['name']}]")
        print(f"  Active MeowDB Listings: {len(active_meow)}")
        if active_meow:
            cheapest_meow = active_meow[0]
            loc_m = f"Ch {cheapest_meow.get('channel')} FM {cheapest_meow.get('fmRoom')}"
            stats = f" | Stats: {cheapest_meow.get('stats')}" if cheapest_meow.get('stats') else ""
            print(f"  Cheapest on MeowDB: {cheapest_meow['price']:,} mesos ({loc_m} @{cheapest_meow.get('username')}{stats})")
    else:
        print("\n[MeowDB]: No match found.")

    elapsed = round(time.time() - t0, 2)
    print(f"\nCross-engine analysis completed in {elapsed}s.")

def main():
    parser = argparse.ArgumentParser(
        prog="mscli",
        description="Maple Classic Market CLI — Open Arbitrage Radar & Price Tracker for MapleStory Classic World"
    )
    sub = parser.add_subparsers(dest='command')

    # scan
    p_scan = sub.add_parser('scan', help='Scan Free Market for high-yield arbitrage opportunities')
    p_scan.add_argument('--budget', type=int, default=150000, help='Max mesos to spend per item')
    p_scan.add_argument('--min-profit', type=int, default=5000, help='Minimum net profit in mesos')
    p_scan.add_argument('--min-pct', type=float, default=20.0, help='Minimum net ROI percentage')
    p_scan.add_argument('--category', type=str, default='all', choices=['all', 'equip', 'etc', 'scroll'])
    p_scan.add_argument('--pages', type=int, default=6, help='Number of browse pages to scan')
    p_scan.add_argument('--limit', type=int, default=10, help='Max deals to display')
    p_scan.set_defaults(func=cmd_scan)

    # audit
    p_audit = sub.add_parser('audit', help='Audit specific item listings and rolled stats on MeowDB')
    p_audit.add_argument('target', type=str, help='Item name or ID')
    p_audit.add_argument('--limit', type=int, default=10, help='Number of listings to show')
    p_audit.set_defaults(func=cmd_audit)

    # mesowatch
    p_mw = sub.add_parser('mesowatch', help='Query MesoWatch live shops, channel/room and macro stats')
    p_mw.add_argument('target', type=str, help='Item name to search on MesoWatch')
    p_mw.add_argument('--results', type=int, default=3, help='Max matching items to inspect')
    p_mw.add_argument('--limit', type=int, default=10, help='Max shop listings to display')
    p_mw.set_defaults(func=cmd_mesowatch)

    # compare
    p_cmp = sub.add_parser('compare', help='Cross-reference both MeowDB and MesoWatch in one call')
    p_cmp.add_argument('target', type=str, help='Item name to compare across platforms')
    p_cmp.set_defaults(func=cmd_compare)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)

if __name__ == '__main__':
    main()
