"""Vercel Function: GET /api/verify -> api_verify() (logika di serverlib.py)."""
from serverlib import api_verify, make_handler


class handler(make_handler(api_verify)):
    pass
