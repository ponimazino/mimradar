"""Vercel Function: GET /api/safety -> api_safety() (logika di serverlib.py)."""
from serverlib import api_safety, make_handler


class handler(make_handler(api_safety)):
    pass
