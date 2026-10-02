"""Vercel Function: GET /api/safety_batch -> api_safety_batch() (logika di serverlib.py)."""
from serverlib import api_safety_batch, make_handler


class handler(make_handler(api_safety_batch)):
    pass
