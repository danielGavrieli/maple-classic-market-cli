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

def cmd_sync_store(args):
    import os
    inv_file = args.inventory
    if not os.path.exists(inv_file):
        sample = [
            {"name": "Meba", "itemId": 688, "price": 12000, "quantity": 1, "condition": "clean", "stats": {}, "note": "Clean Lv.25 Meba"},
            {"name": "Fireman's Axe", "itemId": 581, "price": 25000, "quantity": 1, "condition": "clean", "stats": {"watk": 51}, "note": "51 WATK Max Roll"}
        ]
        with open(inv_file, 'w', encoding='utf-8') as f:
            json.dump(sample, f, indent=2, ensure_ascii=False)
        print(f"Created sample inventory file at '{inv_file}'. Edit it and run sync-store again.")
        return

    with open(inv_file, 'r', encoding='utf-8') as f:
        items = json.load(f)

    ign = args.ign or "MyMerchant"
    ch = args.channel
    room = args.room
    loc = args.location or f"Ch {ch} FM {room}"

    js_code = f"""/**
 * MeowDB MapleStory Classic - Clean Store Sync & Auto-Wipe
 * Generated by mscli sync-store
 * Target: Ch {ch} FM {room} ({loc})
 * IGN: {ign}
 */

(async () => {{
  const TARGET_CHANNEL = {ch};
  const TARGET_FM_ROOM = {room};
  const TARGET_LOCATION = "{loc}";
  const IGN = "{ign}";
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  const NEW_ITEMS = {json.dumps(items, indent=2, ensure_ascii=False)};

  console.log(`%c🚀 Synchronizing store to ${{TARGET_LOCATION}} for ${{IGN}}...`, "color: #00ffcc; font-size: 15px; font-weight: bold;");

  // Step 1: Wipe / Cancel old and sold listings not in the new inventory
  console.log(`%c🧹 [Step 1] Wiping obsolete / sold listings from MeowDB...`, "color: #ffcc00; font-weight: bold;");
  try {{
    const browseRes = await fetch(`/msclassic/api/market-listings/browse?username=${{IGN}}&offers=1`);
    if (browseRes.ok) {{
      const bData = await browseRes.json();
      const existing = bData.rows || [];
      console.log(`Found ${{existing.length}} existing listings for ${{IGN}}.`);
      
      let cancelled = 0;
      for (const oldRow of existing) {{
        const stillActive = NEW_ITEMS.some(n => n.itemId === oldRow.itemId && n.price === oldRow.price && oldRow.channel === TARGET_CHANNEL && oldRow.fmRoom === TARGET_FM_ROOM);
        if (!stillActive) {{
          try {{
            const pRes = await fetch(`/msclassic/api/market-listings/${{oldRow.id}}`, {{
              method: "PATCH",
              headers: {{ "Content-Type": "application/json" }},
              body: JSON.stringify({{ action: "cancel" }})
            }});
            if (pRes.ok) {{
              console.log(`  🗑️ Removed old listing: ${{oldRow.itemName}} (${{oldRow.price.toLocaleString()}} mesos)`);
              cancelled++;
            }}
          }} catch (e) {{}}
          await sleep(250);
        }}
      }}
      console.log(`%c✨ Cleaned up ${{cancelled}} outdated listings!`, "color: #33cc33; font-weight: bold;");
    }}
  }} catch (err) {{
    console.warn("Failed to check existing listings:", err);
  }}

  // Step 2: Upload new store items
  console.log(`%c📦 [Step 2] Publishing ${{NEW_ITEMS.length}} fresh store items...`, "color: #ffcc00; font-weight: bold;");
  let posted = 0;
  for (let i = 0; i < NEW_ITEMS.length; i++) {{
    const it = NEW_ITEMS[i];
    try {{
      const payload = {{
        side: "sell",
        price: it.price,
        pricingMode: "fixed",
        quantity: it.quantity || 1,
        condition: it.condition || "clean",
        stats: it.stats || {{}},
        slotsLeft: it.slotsLeft || null,
        tradeMethod: "personal_store",
        location: TARGET_LOCATION,
        channel: TARGET_CHANNEL,
        fmRoom: TARGET_FM_ROOM,
        ign: IGN,
        contact: "",
        note: it.note || ""
      }};

      const res = await fetch(`/msclassic/api/market-listings?itemId=${{it.itemId}}`, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(payload)
      }});

      if (res.ok) {{
        console.log(`  ✅ [${{i+1}}/${{NEW_ITEMS.length}}] Published: ${{it.name}} (${{it.quantity > 1 ? it.quantity + "x " : ""}}${{it.price.toLocaleString()}} mesos)`);
        posted++;
      }} else {{
        console.warn(`  ⚠️ Failed to publish ${{it.name}}: HTTP ${{res.status}}`);
      }}
    }} catch (e) {{
      console.error(`  ❌ Error on ${{it.name}}:`, e);
    }}
    await sleep(350);
  }}

  console.log(`%c🎉 Complete! ${{posted}}/${{NEW_ITEMS.length}} items live at Channel ${{TARGET_CHANNEL}} FM ${{TARGET_FM_ROOM}}!`, "color: #00ffcc; font-size: 15px; font-weight: bold;");
}})();"""

    out_file = args.out or "sync_store.js"
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(js_code)

    if getattr(args, 'json', False):
        print(json.dumps({
            'success': True,
            'scriptFile': out_file,
            'channel': ch,
            'fmRoom': room,
            'itemsCount': len(items)
        }, indent=2))
        return

    print(f"\n=======================================================")
    print(f"  Store Synchronizer Script Generated Successfully!")
    print(f"=======================================================")
    print(f"Output File: {out_file}")
    print(f"Channel: {ch} | FM Room: {room} | Items: {len(items)}")
    print(f"\nInstructions:")
    print(f"1. Open https://meowdb.com/msclassic in your browser.")
    print(f"2. Press F12 -> Console.")
    print(f"3. Paste the contents of '{out_file}' and press Enter.")
    print(f"4. The script will automatically cancel all old listings and publish the new ones!")

def main():
    parser = argparse.ArgumentParser(
        prog="mscli",
        description="Maple Classic Market CLI — Open Arbitrage Radar & Price Tracker for MapleStory Classic World"
    )
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

    # sync-store
    p_sync = subparsers.add_parser('sync-store', help='Generate MeowDB store sync script with automatic old-listing cleanup')
    p_sync.add_argument('--channel', type=int, default=34, help='Channel number of your store')
    p_sync.add_argument('--room', type=int, default=12, help='FM Room number of your store')
    p_sync.add_argument('--location', type=str, default='', help='Optional spot title (e.g. Entrance)')
    p_sync.add_argument('--ign', type=str, default='', help='In-game merchant name')
    p_sync.add_argument('--inventory', type=str, default='store.json', help='Path to store inventory JSON file')
    p_sync.add_argument('--out', type=str, default='sync_store.js', help='Output javascript file name')
    p_sync.add_argument('--json', action='store_true', help='Output raw JSON confirmation')
    p_sync.set_defaults(func=cmd_sync_store)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)

if __name__ == '__main__':
    main()
