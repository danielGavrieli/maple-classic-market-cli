import urllib.request
import urllib.parse
import json
from .utils import DEFAULT_HEADERS, SSL_CTX

BASE_DATA_URL = "https://meso.watch/data"

MESOWATCH_HEADERS = {
    **DEFAULT_HEADERS,
    'Referer': 'https://meso.watch/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

_list_cache = None

def fetch_json(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=MESOWATCH_HEADERS)
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8', 'ignore'))
    except Exception:
        return None

def get_market_list(force_refresh=False):
    global _list_cache
    if _list_cache and not force_refresh:
        return _list_cache
    url = f"{BASE_DATA_URL}/list.json"
    data = fetch_json(url)
    if data and 'items' in data:
        _list_cache = data
        return data
    return None

def search_mesowatch(query_name, max_results=5):
    market_list = get_market_list()
    if not market_list or 'items' not in market_list:
        return []

    q = query_name.lower().strip()
    matches = [it for it in market_list['items'] if q in it.get('name', '').lower()]
    
    results = []
    for item in matches[:max_results]:
        cat_id = item.get('id', '').replace(':', '_')
        item_name = item.get('name')
        item_file = f"{BASE_DATA_URL}/markets/Classic%20World/item/{cat_id}.json"
        detail = fetch_json(item_file)
        
        listings = []
        if detail and 'listings' in detail:
            for l in detail['listings']:
                listings.append({
                    'seller': l.get('seller'),
                    'price': l.get('price'),
                    'qty': l.get('qty', 1),
                    'channel': l.get('channel'),
                    'fmRoom': l.get('channelRoom'),
                    'location': l.get('location'),
                    'lastSeen': l.get('lastSeen')
                })
        
        # Sort lowest price first
        listings.sort(key=lambda x: (x['price'] if x['price'] is not None else float('inf')))

        results.append({
            'name': item_name,
            'id': item.get('id'),
            'medianPrice': item.get('price'),
            'p25': item.get('p25'),
            'p75': item.get('p75'),
            'low': item.get('low'),
            'high': item.get('high'),
            'askMedian': item.get('askMedian'),
            'sold24h': item.get('priceSales'),
            'lastSold': item.get('lastSold'),
            'listingsCount': len(listings),
            'listings': listings
        })
        
    return results
