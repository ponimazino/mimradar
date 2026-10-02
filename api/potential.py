"""Vercel Function: GET /api/potential -> api_potential() (logika di serverlib.py)."""
from serverlib import api_potential, make_handler


class handler(make_handler(api_potential)):
    pass
