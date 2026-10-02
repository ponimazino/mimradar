"""Vercel Function: GET /api/search -> api_search() (logika di serverlib.py)."""
from serverlib import api_search, make_handler


class handler(make_handler(api_search)):
    pass
