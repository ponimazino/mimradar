"""Vercel Function: GET /api/dev?address=... -> api_dev(qs) (logika di serverlib.py)."""
from serverlib import api_dev, make_handler


class handler(make_handler(api_dev)):
    pass