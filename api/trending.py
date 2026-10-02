"""Vercel Function: GET /api/trending -> api_trending() (logika di serverlib.py)."""
from serverlib import api_trending, make_handler


class handler(make_handler(api_trending)):
    pass
