"""
Maple Classic Market CLI (mscli)
Cross-Platform Free Market Radar, Price Tracker & Arbitrage Scanner for MapleStory Classic.
Designed for both human merchants and autonomous AI Agents (Claude, Cursor, Codex).
"""

__version__ = "1.2.0"

from .arbitrage import scan_arbitrage
from .mesowatch import search_mesowatch, get_market_list
from .meowdb import browse_listings, get_item_listings, get_item_meta, search_items
from .cli import compare_item
from .refining import analyze_refining_profit

__all__ = [
    "scan_arbitrage",
    "search_mesowatch",
    "get_market_list",
    "browse_listings",
    "get_item_listings",
    "get_item_meta",
    "search_items",
    "compare_item",
    "analyze_refining_profit",
]
