import urllib.request
import urllib.parse
import json
from .utils import DEFAULT_HEADERS, SSL_CTX

BASE_URL = "https://meowdb.com/msclassic/api"

def fetch_json(url, timeout=5):
    try:
        req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8', 'ignore'))
    except Exception:
        return None

def browse_listings(page=1, max_price=None, item_type=None, sort="newest"):
    params = [("offers", "1"), ("side", "sell"), ("sort", sort), ("page", str(page))]
    if max_price:
        params.append(("maxPrice", str(max_price)))
    if item_type:
        params.append(("itemType", item_type))
    
    url = f"{BASE_URL}/market-listings/browse?{urllib.parse.urlencode(params)}"
    data = fetch_json(url)
    return data.get('rows', []) if data else []

def get_item_listings(item_id, include_meta=False):
    url = f"{BASE_URL}/market-listings?itemId={item_id}&offers=1"
    data = fetch_json(url)
    if not data:
        return [] if not include_meta else {'listings': [], 'completed': [], 'summary': {}}
    if isinstance(data, list):
        return data if not include_meta else {'listings': data, 'completed': [], 'summary': {}}
    if include_meta:
        return {
            'listings': data.get('listings', data.get('rows', [])),
            'completed': data.get('completed', []),
            'summary': data.get('summary', {})
        }
    return data.get('listings', data.get('rows', []))

def get_item_meta(item_id):
    url = f"{BASE_URL}/items/{item_id}"
    return fetch_json(url)

def search_items(query):
    url = f"{BASE_URL}/market-listings/browse?q={urllib.parse.quote(query)}&offers=1&side=sell"
    data = fetch_json(url)
    if not data or not data.get('rows'):
        return []
    
    unique_items = {}
    q_lower = query.lower()
    for r in data['rows']:
        iid = r.get('itemId')
        name = r.get('itemName')
        if iid and name and iid not in unique_items:
            unique_items[iid] = {'id': iid, 'name': name}
            
    # Prefer exact or closest match
    items = list(unique_items.values())
    items.sort(key=lambda x: (0 if x['name'].lower() == q_lower else (1 if q_lower in x['name'].lower() else 2)))
    return items
