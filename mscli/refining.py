import json
import os

CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'items_catalog.json')

def load_catalog():
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

ORE_RECIPES = [
    {'name': 'Iron Ingot', 'ore': 'iron ore', 'product': 'iron ingot', 'fee': 300},
    {'name': 'Bronze Ingot', 'ore': 'bronze ore', 'product': 'bronze ingot', 'fee': 200},
    {'name': 'Mithril Ingot', 'ore': 'mithril ore', 'product': 'mithril ingot', 'fee': 300},
    {'name': 'Silver Ingot', 'ore': 'silver ore', 'product': 'silver ingot', 'fee': 300},
    {'name': 'Gold Ingot', 'ore': 'gold ore', 'product': 'gold ingot', 'fee': 500},
    {'name': 'Steel Ingot', 'ore': 'steel ore', 'product': 'steel ingot', 'fee': 300},
    {'name': 'Black Crystal', 'ore': 'black crystal ore', 'product': 'black crystal', 'fee': 1000},
]

def analyze_refining_profit():
    catalog = load_catalog()
    results = []

    for r in ORE_RECIPES:
        ore_data = catalog.get(r['ore'], {})
        prod_data = catalog.get(r['product'], {})

        ore_price = ore_data.get('medianPrice') or 0
        prod_price = prod_data.get('medianPrice') or 0
        ore_sales = ore_data.get('priceSales24h') or 0
        prod_sales = prod_data.get('priceSales24h') or 0

        cost_to_craft = (ore_price * 10) + r['fee']
        net_sell = int(prod_price * 0.97)
        profit_crafting = net_sell - cost_to_craft

        results.append({
            'recipe': r['name'],
            'ore_name': ore_data.get('name', r['ore'].title()),
            'ore_price': ore_price,
            'ore_sales_24h': ore_sales,
            'ingot_price': prod_price,
            'ingot_sales_24h': prod_sales,
            'crafting_cost': cost_to_craft,
            'net_profit_per_craft': profit_crafting,
            'recommendation': 'REFINE' if profit_crafting > 0 else 'SELL RAW ORE'
        })

    return results

