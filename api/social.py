"""Vercel Function: GET /api/social -> social_cached() (logika di serverlib.py)."""
from serverlib import social_cached, make_handler


class handler(make_handler(social_cached)):
    pass
