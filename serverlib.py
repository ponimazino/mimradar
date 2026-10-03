"""
Meme Radar — logika inti (dipakai bersama oleh server.py lokal dan api/*.py Vercel).

Proxy ke API publik gratis (tanpa API key):
  - Google Trends: keyword yang lagi viral mainstream (sinyal PALING early)
  - X/Twitter     : tren hashtag via scraping trends24.in (API resmi X berbayar)
  - 4chan /biz/    : kata/ticker yang lagi di-spam di lantai shill paling awal
  - RSS berita     : CoinDesk/Cointelegraph/Decrypt — narasi crypto-native
  - DexScreener    : search pair, trending/boosted tokens, detail pair
  - RugCheck       : skor keamanan token Solana
  - GoPlus         : cek keamanan kontrak EVM (ETH/Base/BSC/Polygon/Arbitrum)

Dipakai dari dua pintu:
  - server.py  : HTTP server lokal  -> python server.py  -> http://127.0.0.1:8765
  - api/*.py   : Vercel Python Functions (serverless) — tiap file ekspor class
    `handler` via make_handler(fn) di bawah.
"""
import html as html_mod
import inspect
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = 8765
ROOT = Path(__file__).resolve().parent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MemeRadar/1.0",
    "Accept": "application/json",
}

DEX = "https://api.dexscreener.com"
RUGCHECK = "https://api.rugcheck.xyz"
GOPLUS = "https://api.gopluslabs.io"
GECKO = "https://api.geckoterminal.com/api/v2"

# numeric chain id untuk GoPlus (EVM saja)
GOPLUS_CHAIN = {
    "ethereum": 1,
    "bsc": 56,
    "base": 8453,
    "polygon": 137,
    "arbitrum": 42161,
}
# prefix URL GMGN
GMGN_CHAIN = {
    "solana": "solana",
    "base": "base",
    "ethereum": "eth",
    "bsc": "bsc",
}


def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_text(url, timeout=15, headers=None):
    req = urllib.request.Request(url, headers=headers or HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def gmgn_url(chain, address):
    prefix = GMGN_CHAIN.get(chain)
    return f"https://gmgn.ai/{prefix}/token/{address}" if prefix else None


def pair_item(p, meta=None):
    """Normalisasi satu pair DexScreener jadi item untuk frontend."""
    now = time.time() * 1000
    created = p.get("pairCreatedAt") or 0
    liq = (p.get("liquidity") or {}).get("usd") or 0
    vol = p.get("volume") or {}
    chg = p.get("priceChange") or {}
    tx = p.get("txns") or {}
    t24 = tx.get("h24") or {}
    base = p.get("baseToken") or {}
    info = p.get("info") or {}
    item = {
        "chain": p.get("chainId"),
        "address": base.get("address"),
        "name": base.get("name"),
        "symbol": base.get("symbol"),
        "pairUrl": p.get("url"),
        "dexId": p.get("dexId"),
        "created": created,
        "ageHours": round((now - created) / 3600000, 1) if created else None,
        "priceUsd": p.get("priceUsd"),
        "mc": p.get("marketCap") or p.get("fdv"),
        "liq": liq,
        "vol24h": vol.get("h24") or 0,
        "vol6h": vol.get("h6") or 0,
        "vol1h": vol.get("h1") or 0,
        "volRecent": vol.get("m5") or 0,
        "chg1h": chg.get("h1"),
        "chg6h": chg.get("h6"),
        "chg24h": chg.get("h24"),
        "buys24h": t24.get("buys"),
        "sells24h": t24.get("sells"),
        "image": info.get("imageUrl"),
        "socials": info.get("socials") or [],
        "gmgn": gmgn_url(p.get("chainId"), base.get("address") or ""),
    }
    if meta is not None:
        item["description"] = meta.get("description") or ""
    return item


def api_search(qs):
    q = (qs.get("q") or [""])[0].strip()
    if not q:
        return {"error": "query 'q' wajib diisi"}
    chains = set(filter(None, (qs.get("chains") or [""])[0].split(",")))
    try:
        max_age = float((qs.get("maxAgeH") or ["0"])[0])
        min_liq = float((qs.get("minLiq") or ["0"])[0])
        min_vol = float((qs.get("minVol") or ["0"])[0])
    except ValueError:
        return {"error": "parameter filter harus berupa angka"}
    sort = (qs.get("sort") or ["new"])[0]

    data = fetch_json(DEX + "/latest/dex/search?q=" + urllib.parse.quote(q))
    pairs = data.get("pairs") or []

    # satu token bisa punya banyak pair — ambil pair dengan likuiditas terbesar
    best = {}
    for p in pairs:
        base = p.get("baseToken") or {}
        addr = base.get("address")
        if not addr:
            continue
        key = (p.get("chainId"), addr)
        liq = (p.get("liquidity") or {}).get("usd") or 0
        cur = best.get(key)
        if cur is None or liq > cur[1]:
            best[key] = (p, liq)

    items = []
    for p, _liq in best.values():
        it = pair_item(p)
        if chains and it["chain"] not in chains:
            continue
        if max_age and (it["ageHours"] is None or it["ageHours"] > max_age):
            continue
        # liq 0/None = masih bonding curve (mis. pump.fun), bukan likuiditas kecil —
        # jangan disaring min likuiditas; kualitasnya diukur lewat volume
        if min_liq and (it["liq"] or 0) > 0 and it["liq"] < min_liq:
            continue
        if (it["vol24h"] or 0) < min_vol:
            continue
        items.append(it)

    sorters = {
        "new": lambda x: x["created"] or 0,
        "vol": lambda x: x["vol24h"] or 0,
        "liq": lambda x: x["liq"] or 0,
        "mc": lambda x: x["mc"] or 0,
        "mom": lambda x: x["chg1h"] if x["chg1h"] is not None else -9999,
    }
    items.sort(key=sorters.get(sort, sorters["new"]), reverse=True)
    # "found" = token yang cocok narasi SEBELUM filter — supaya UI bisa bedakan
    # "belum ada tokennya" vs "ada tapi tersaring"
    return {"query": q, "found": len(best), "total": len(items), "items": items}


def api_social():
    """Sinyal narasi PALING EARLY, sebelum token ada / muncul di dex.

    - Google Trends (RSS publik): momen viral mainstream — politisi ngomong,
      hewan viral, event. Tiap item bawa link berita sebagai bukti viral.
    - X/Twitter (scraping trends24.in): tren AS, tiap item bawa link search X.
    - 4chan /biz/ (API JSON publik): lantai shill paling awal; tiap item bawa
      link thread terbaru yang menyebutnya + waktu post terakhir.
    - RSS berita crypto (CoinDesk/Cointelegraph/Decrypt): istilah yang paling
      sering muncul di judul — narasi crypto-native, bukan tren politik AS.
    Tiap keyword dilacak kapan pertama & terakhir terlihat di radar
    (riwayat di memori server, selama server jalan).
    Satu sumber gagal tidak mematikan sumber lain.
    """
    out = {"fetchedAt": {}, "google": [], "x": [], "biz": [], "news": [], "errors": []}

    try:
        out["google"] = google_trends()
        out["fetchedAt"]["google"] = int(time.time())
    except Exception as e:
        out["errors"].append(f"google trends gagal: {e}")

    try:
        out["x"] = x_trends()
        out["fetchedAt"]["x"] = int(time.time())
    except Exception as e:
        out["errors"].append(f"X trends gagal: {e}")

    try:
        out["biz"] = biz_items()
        out["fetchedAt"]["biz"] = int(time.time())
    except Exception as e:
        out["errors"].append(f"/biz/ gagal: {e}")

    try:
        out["news"] = news_items()
        out["fetchedAt"]["news"] = int(time.time())
    except Exception as e:
        out["errors"].append(f"berita crypto gagal: {e}")

    return out


# riwayat radar: kapan sebuah keyword pertama & terakhir terlihat
SEEN = {}  # (source, word) -> {"first": epoch, "last": epoch}


def track_seen(source, word):
    e = SEEN.setdefault((source, word), {"first": int(time.time()), "last": 0})
    e["last"] = int(time.time())
    return e["first"]


def google_trends():
    """Tren pencarian Google AS — tiap item: judul, volume pencarian,
    dan link berita teratas sebagai bukti momennya baru saja viral."""
    raw = fetch_text("https://trends.google.com/trending/rss?geo=US", timeout=20)
    items = []
    for block in re.findall(r"<item>(.*?)</item>", raw, re.S):
        def pick(pat):
            m = re.search(pat, block)
            return html_mod.unescape(m.group(1)).strip() if m else None
        title = pick(r"<title>(.*?)</title>")
        if not title:
            continue
        items.append({
            "title": title,
            "traffic": pick(r"<ht:approx_traffic>(.*?)</ht:approx_traffic>"),
            "url": pick(r"<ht:news_item_url>(.*?)</ht:news_item_url>"),
            "firstSeen": track_seen("google", title.lower()),
        })
    return items[:15]


# trends24 kadang menolak UA non-browser
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,*/*",
}


def x_trends():
    """Tren X (Twitter) AS via trends24.in — tanpa API key.
    Tiap item bawa link search X sebagai bukti trennya.
    '#' dibuang supaya keyword bisa langsung dipakai query dex."""
    raw = fetch_text("https://trends24.in/united-states/", timeout=20, headers=BROWSER_HEADERS)
    out, seen = [], set()
    for href, label in re.findall(
        r'<a href="(https://twitter\.com/search\?q=[^"]+)"[^>]*class=trend-link>([^<]+)</a>', raw
    ):
        t = html_mod.unescape(label).strip()
        while t.startswith("#"):
            t = t[1:].strip()
        low = t.lower()
        if not t or low in seen:
            continue
        seen.add(low)
        out.append({
            "word": t,
            "url": html_mod.unescape(href),
            "firstSeen": track_seen("x", low),
        })
    return out[:20]


def biz_items():
    """Kata/ticker yang paling sering disebut di katalog /biz/ —
    dengan waktu post terakhir + thread terbaru sebagai bukti shill."""
    pages = fetch_json("https://a.4cdn.org/biz/catalog.json") or []
    words = {}

    def scan(text, ts, thread_no):
        text = html_mod.unescape(re.sub(r"<[^>]+>", " ", text))
        for w in re.findall(r"\b([A-Z]{2,8})\b", text):
            if w in BIZ_STOP:
                continue
            e = words.setdefault(w, {"word": w, "count": 0, "lastSeen": 0, "thread": None})
            e["count"] += 1
            if ts > e["lastSeen"]:
                e["lastSeen"] = ts
                e["thread"] = thread_no

    for page in pages:
        for th in page.get("threads") or []:
            no = th.get("no")
            scan(" ".join(str(th.get(k) or "") for k in ("sub", "com")), th.get("time") or 0, no)
            for rep in th.get("last_replies") or []:
                scan(str(rep.get("com") or ""), rep.get("time") or 0, no)

    items = sorted(words.values(), key=lambda x: -x["count"])[:24]
    for it in items:
        it["firstSeen"] = track_seen("biz", it["word"])
    return items


# kata kapital yang BUKAN narasi: kata bahasa Inggris umum, jargon chan,
# istilah finansial, saturan umum — supaya yang tersisa benar-benar ticker/narasi
BIZ_STOP = frozenset("""
THE AND ARE BUT NOT FOR IT WITH THIS THAT FROM HAVE WILL THEY WHAT WHEN ALL CAN OUT
GET WAS HAS WERE ONE HOW WHY WHO YES OK NO LOL LMAO WTF ROFL KEK IS TO OF WE SO UP
OVER UNDER SHORT LONG STOP LOSS TAKE FOMO FUD RISK CASH DEBT LOAN JOBS JOB
RATE DATA NEWS INFO FREE MAKE MADE JUST LIKE ONLY MORE MOST THAN THEN THEM
THOSE HERE THERE BEEN BEING DOES DONE GOING WANT NEED KNOW SAID SAY BEST REAL
TRUE FULL HALF EACH EVER NEVER ALWAYS STILL YET TOO ITS ALSO ACROSS AFTER
BEFORE AGAIN BECAUSE WHILE WHERE WHICH WOULD COULD SHOULD MUST MIGHT SHALL MAY
AM PM ID PD NEW OLD BIG HUGE MASSIVE INSANE CRAZY GAIN GAINS CALL CALLS PUT
PUTS APE APES BOOM BUST RETARD NORMIE ANON MODS OP TFW IIRC IMO IMHO AFAIK
TIL TLDR ELI5 SMH BTW FTFY BASED KEKW COPE SEETHE PROOF PUMP DUMP HODL MOON
BAG BAGS FIAT BANK BANKS RICH POOR POORFAG BROKE SPENT SPEND PAID PAY BUY
SELL SOLD BOUGHT TRADED TRADE TRADES MARKET MARKETS PRICE PRICES DOLLAR
DOLLARS MONEY CRYPTO BITCOIN ETHEREUM CHAIN TOKEN TOKENS COIN COINS WALL
CHART CHARTS CRASH MOONING ANTI SEMI POST POSTS THREAD REPLY QUOTE LINK
BOTH EACH YOUR YOUS YOU MY ME HIM HER NOW TODAY TONIGHT WEEK MONTH YEAR YEARS DAYS HOURS MIN
UTC EST PST CST GMT ET PT US EU UK UN TV PM CTX WAGMI NGMI FREN SIRS SER
FUCKING SHIT FUCK DAMN CRAP PISS HELL AHAHA KYS NIGGER FAG RETARDED DUMB IDIOT
BTC ETH USD EUR GBP SATS WEI DAO NFT NFTS DEFI DEX CEX ICO IDO ATH ATL APR
APY TVL PNL MC GDP ETF IRS FED IMF CEO CFO CTO COO VP IPO SEC DOJ FBI CIA
NYSE DTCC SWIFT REIT IRA FICA AUM ROE ROA ROI CAGR EBITDA YOY QOQ H1 H2
Q1 Q2 Q3 Q4 OTC W2 W4 K1 401K ROTH AGI CPA CPA CTA ACH PIN SSN
""".split())


# ---------- sumber ke-4: judul berita crypto (narasi crypto-native) ----------

NEWS_FEEDS = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
    ("Decrypt", "https://decrypt.co/feed"),
]

# kata yang BUKAN narasi: kata umum bahasa Inggris, jargon berita, istilah
# crypto generik, dan coin besar yang selalu ada tiap hari (bukan sinyal baru)
NEWS_STOP = frozenset("""
THE AND ARE BUT NOT FOR IT WITH THIS THAT FROM HAVE WILL THEY WHAT WHEN
ALL CAN OUT WAS HAS ONE HOW WHY WHO ITS ALSO MORE MOST THAN THEN THEM
THOSE HERE THERE BEEN BEING DOES DONE GOING WANT NEED KNOW SAID SAY BEST
REAL FULL EACH EVER NEVER ALWAYS STILL YET TOO AFTER BEFORE AGAIN BECAUSE
WHILE WHERE WHICH WOULD COULD SHOULD MUST MIGHT OVER UNDER ABOUT INTO
AFTER AGAIN AMID BETWEEN THROUGH DURING SINCE UPON EVERY SOME JUST LIKE
ONLY NEXT FIRST SECOND THIRD LAST LATEST NEW NEWS REPORT REPORTS REPORTED
SAYS SAYING TELLS TOLD ACCORDING AMONG ACROSS BASED USING USE USED MAKE
MADE TAKE TAKEN LOOK LOOKING SHOW SHOWS SHOWED SEEM SEEMS BIG HUGE HUGE
MASSIVE MAJOR TOP LIST GUIDE ANALYSIS ANALYST EXPERT EXPERTS EXPLAINER
HERE EVERYTHING THINGS WAYS NEED KNOW WATCH DAILY WEEKLY MONTH QUARTER
YEAR YEARS TODAY TONIGHT WEEK MONTHS PRICE PRICES MARKET MARKETS TRADING
TRADE TRADED INVEST INVESTOR INVESTORS CRYPTO CRYPTOCURRENCY BLOCKCHAIN
EXCHANGE EXCHANGES LAUNCH LAUNCHES LAUNCHED LAUNCHPAD PLATFORM SERVICE
SERIES FUNDING FIRM FIRMS COMPANY COMPANIES BANK BANKS MONEY DOLLAR DATA
BITCOIN BTC ETHEREUM ETH ETHEREUMS SOLANA SOL TOKEN TOKENS COIN COINS
YOUR YOU YOURS THEIR OUR THEY THEM THESE THOSE WHATS DONT DOESNT CANT
WONT ISNT HERES WHYS WHY JOBS JOB RULES RULE UPDATE UPDATES LIVE
HIT HITS PLAN PLANS SET SETS RISE RISES FELL FALL FALLS DROPS JUMP
JUMPS SURGE SURGES WIN WINS LOSS LOSSES GAINS GAIN GROWTH GROW RAISE
RAISES BOOST BOOSTS POTENTIAL EARLY BILLION MILLION TRILLION THOUSAND
HUNDRED TRILLION FIGURE FIGURES LEVEL LEVELS TERM TERMS BACK BACKS
GROUP GROUPS AHEAD DOWN ANOTHER OTHER OTHERS INTERVIEW INTERVIEWS
ADVISERS ADVISER INVESTMENT INVESTMENTS REGULATOR REGULATORS CUSTODY
SMALL TOP TOPS CROSSES CROSS SPEECH DINNER BANNED TWICE BUILT BUILD
BUILDS GIVES GAVE GLIMPSE CHANGE CHANGES SUE SUES SUED GRANT GRANTS
GRANTED BANS BAN MOVES MOVE MOVED
""".split())
NEWS_STOP = frozenset(w.lower() for w in NEWS_STOP)


def _cdata(s):
    """buang pembungkus CDATA kalau ada"""
    s = s.strip()
    if s.startswith("<![CDATA["):
        s = s[9:]
    if s.endswith("]]>"):
        s = s[:-3]
    return s.strip()


def news_items():
    """Istilah yang paling sering muncul di judul berita crypto 3 media —
    sumber narasi yang crypto-native (kebalikan tren politik/selebriti di
    Google/X). Tiap keyword bawa judul + link berita terakhir sebagai bukti."""
    words = {}
    for _name, url in NEWS_FEEDS:
        try:
            raw = fetch_text(url, timeout=15)
        except Exception:
            continue
        for block in re.findall(r"<item>(.*?)</item>", raw, re.S):
            m = re.search(r"<title>(.*?)</title>", block, re.S)
            title = html_mod.unescape(_cdata(m.group(1))) if m else ""
            title = re.sub(r"\s*[-–|]\s*(CoinDesk|Cointelegraph|Decrypt)\s*$", "", title).strip()
            if not title:
                continue
            m = re.search(r"<link>(.*?)</link>", block, re.S)
            link = _cdata(m.group(1)) if m else ""
            for w in re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", title):
                low = w.lower()
                if low in NEWS_STOP:
                    continue
                e = words.setdefault(low, {"word": w, "count": 0, "title": title, "url": link})
                e["count"] += 1
    items = sorted(words.values(), key=lambda x: -x["count"])[:20]
    for it in items:
        it["firstSeen"] = track_seen("news", it["word"])
    return items


# ---------- token potensial: muda + aman + terkait topik panas ----------

SOCIAL_CACHE = {"ts": 0.0, "data": None}

# pool BARU dibuat (umur 1-2 menit) via GeckoTerminal — satu-satunya sumber
# yang lebih early dari profil/boost DexScreener. Cache 2 menit biar hemat rate limit.
GECKO_CACHE = {"ts": 0.0, "pools": None}


def gecko_new_pools():
    """[(chain, token_addr, attrs, pool_addr)] dari feed new_pools, dedup per token
    (reserve terbesar). Token seumur 90 detik pun bisa muncul di sini."""
    if GECKO_CACHE["pools"] is not None and time.time() - GECKO_CACHE["ts"] < 120:
        return GECKO_CACHE["pools"]
    best = {}
    for network in ("solana", "base", "bsc", "ethereum"):
        try:
            d = fetch_json(f"{GECKO}/networks/{network}/new_pools", timeout=12)
        except Exception:
            continue
        for p in d.get("data") or []:
            attrs = p.get("attributes") or {}
            tok_id = ((p.get("relationships") or {}).get("base_token") or {}).get("data") or {}
            tok_id = tok_id.get("id") or ""
            addr = tok_id.split("_", 1)[1] if "_" in tok_id else ""
            if not addr:
                continue
            key = (network, addr)
            reserve = float(attrs.get("reserve_in_usd") or 0)
            if key not in best or reserve > best[key][2]:
                best[key] = (attrs, attrs.get("address") or "", reserve)
    pools = [(c, a, v[0], v[1]) for (c, a), v in best.items()]
    GECKO_CACHE["pools"] = pools
    GECKO_CACHE["ts"] = time.time()
    return pools


# trending ORGANIK (algoritma vol/likuiditas nyata — bukan boost bayaran)
GECKO_TREND_CACHE = {"ts": 0.0, "keys": None}


def gecko_trending_pools():
    """[(chain, token_addr)] dari trending_pools GeckoTerminal, 4 chain.
    Ini sinyal trending yang lebih proven: berdasarkan aktivitas pasar nyata."""
    if GECKO_TREND_CACHE["keys"] is not None and time.time() - GECKO_TREND_CACHE["ts"] < 300:
        return GECKO_TREND_CACHE["keys"]
    keys = []
    for network in ("solana", "base", "bsc", "ethereum"):
        try:
            d = fetch_json(f"{GECKO}/networks/{network}/trending_pools?page=1", timeout=12)
        except Exception:
            continue
        for p in d.get("data") or []:
            tok_id = ((p.get("relationships") or {}).get("base_token") or {}).get("data") or {}
            tok_id = tok_id.get("id") or ""
            addr = tok_id.split("_", 1)[1] if "_" in tok_id else ""
            if addr:
                keys.append((network, addr))
    GECKO_TREND_CACHE["keys"] = keys
    GECKO_TREND_CACHE["ts"] = time.time()
    return keys


def gecko_item(chain, address, a, pool_address):
    """Bangun item kompatibel pair_item langsung dari atribut pool GeckoTerminal —
    dipakai untuk token yang BELUM terindeks DexScreener (umur 1-2 menit)."""
    created = None
    try:
        created = int(time.mktime(time.strptime(a.get("pool_created_at") or "", "%Y-%m-%dT%H:%M:%SZ")) * 1000)
    except ValueError:
        pass
    symbol = (a.get("name") or "").split(" / ")[0] or address[:4]
    vol = a.get("volume_usd") or {}
    tx = a.get("transactions") or {}
    t24 = tx.get("h24") or {}
    chg = a.get("price_change_percentage") or {}

    def fnum(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    return {
        "chain": chain,
        "address": address,
        "name": symbol,
        "symbol": symbol,
        "pairUrl": f"https://www.geckoterminal.com/{chain}/pools/{pool_address}",
        "dexId": "pool baru",
        "created": created,
        "ageHours": round((time.time() * 1000 - created) / 3.6e6, 2) if created else None,
        "priceUsd": a.get("base_token_price_usd"),
        "mc": a.get("market_cap_usd") or a.get("fdv_usd"),
        "liq": float(a.get("reserve_in_usd") or 0) or None,
        "vol24h": fnum(vol.get("h24")) or 0,
        "vol6h": fnum(vol.get("h6")) or 0,
        "vol1h": fnum(vol.get("h1")) or 0,
        "volRecent": fnum(vol.get("m15")) or 0,
        "chg1h": fnum(chg.get("h1")),
        "chg6h": fnum(chg.get("h6")),
        "chg24h": fnum(chg.get("h24")),
        "buys24h": t24.get("buys"),
        "sells24h": t24.get("sells"),
        "image": None,
        "socials": [],
        "gmgn": gmgn_url(chain, address),
    }


def social_cached():
    """api_social scrape 3 sumber — potential/section lain pakai cache 5 menit."""
    if SOCIAL_CACHE["data"] is None or time.time() - SOCIAL_CACHE["ts"] > 300:
        SOCIAL_CACHE["data"] = api_social()
        SOCIAL_CACHE["ts"] = time.time()
    return SOCIAL_CACHE["data"]


def match_topics(item, social):
    """Keyword radar yang cocok dengan nama/simbol/deskripsi token.
    Minimal 4 huruf supaya kata pendek ('AI', 'oil') tidak menabrak sembarangan."""
    kws = []
    for t in social.get("biz") or []:
        kws.append(t.get("word"))
    for t in social.get("news") or []:
        kws.append(t.get("word"))
    for t in social.get("x") or []:
        kws.append(t.get("word"))
    for t in social.get("google") or []:
        kws.append(t.get("title"))
    text = " ".join(filter(None, [
        item.get("name") or "", item.get("symbol") or "", item.get("description") or "",
    ])).lower()
    hits = []
    for kw in dict.fromkeys(k for k in kws if k):
        k = kw.lower().strip()
        if len(k) >= 4 and k in text:
            hits.append(kw)
    return hits[:3]


def momentum_score(it):
    """Skor 'seberapa HIDUP token ini sekarang' — bukan seberapa muda.
    Volume jendela pendek (5-15 menit) bobot terbesar, lalu vol 1 jam,
    tekanan beli (buy dominan), dan bonus kalau nyambung topik radar.
    Kalau cuma urut umur, pool 2 menit yang sepi selalu nangkring di atas."""
    v_now = it.get("volRecent") or 0
    v1h = it.get("vol1h") or 0
    v24 = it.get("vol24h") or 0
    buys = it.get("buys24h") or 0
    sells = it.get("sells24h") or 0
    buy_pressure = (buys - sells) / (buys + sells) if buys + sells else 0.0
    return round(
        3.0 * math.log10(v_now + 1)
        + 2.0 * math.log10(v1h + 1)
        + 1.0 * math.log10(v24 + 1)
        + 4.0 * max(0.0, buy_pressure)
        + 2.0 * len(it.get("topics") or []),
    1)


def api_potential():
    """Token POTENSIAL untuk early entry:
    - kandidat = pool BARU GeckoTerminal (umur 1-2 menit — paling early)
      + token yang BARU dibuat profil/di-boost (dev lagi aktif)
      + hasil search keyword topik radar yang lagi panas (news crypto dulu,
        baru /biz/, X, Google — keyword crypto-native lebih relevan)
    - WAJIB lolos verifikasi RugCheck/GoPlus (level good/warning; unknown tidak masuk —
      token 90 detik yang belum terindeks rugcheck jujur tampil sebagai belum terverifikasi)
    - umur <= 72 jam; token < 30 menit diukur lewat volume 15-menit, sisanya vol 24 jam
    - diurut MOMEMTUM tertinggi dulu (bukan paling muda) — token sepi
      walau baru lahir tenggelam, token yang lagi bergerak naik ke atas.
    """
    social = social_cached()

    # 1) kandidat: profil/boost terbaru — sinyal token yang baru dipromosikan
    cands, seen = [], set()
    desc_of = {}
    for path in ("/token-boosts/latest/v1", "/token-profiles/latest/v1"):
        try:
            res = fetch_json(DEX + path) or []
        except Exception:
            continue
        for e in res:
            k = (e.get("chainId"), e.get("tokenAddress"))
            if k[0] and k[1] and k not in seen:
                seen.add(k)
                desc_of[k] = e.get("description") or ""
                cands.append(k)

    # 2) kandidat dari topik radar yang lagi panas — keyword berita crypto
    #    didahulukan (crypto-native), baru lantai shill / tren mainstream
    hot = []
    for t in (social.get("news") or [])[:5]:
        hot.append(t.get("word"))
    for t in (social.get("biz") or [])[:4]:
        hot.append(t.get("word"))
    for t in (social.get("x") or [])[:2]:
        hot.append(t.get("word"))
    for t in (social.get("google") or [])[:3]:
        words = (t.get("title") or "").split()
        if words:
            hot.append(words[0])
    for q in list(dict.fromkeys(h for h in hot if h and len(h) >= 4))[:5]:
        try:
            data = fetch_json(DEX + "/latest/dex/search?q=" + urllib.parse.quote(q))
        except Exception:
            continue
        for p in data.get("pairs") or []:
            base = p.get("baseToken") or {}
            k = (p.get("chainId"), base.get("address"))
            if k[0] and k[1] and k not in seen:
                seen.add(k)
                cands.append(k)

    # 3) pool BARU (umur bisa 1-2 menit) via GeckoTerminal — paling early
    gecko = {}
    for chain, addr, attrs, pool_addr in gecko_new_pools():
        k = (chain, addr)
        if k not in seen:
            seen.add(k)
            cands.append(k)
        gecko[k] = (attrs, pool_addr)

    # 4) statistik pair per chain (endpoint tokens/v1, maks 30 alamat per call)
    by_chain = {}
    for chain, addr in cands:
        by_chain.setdefault(chain, []).append(addr)
    best = {}
    for chain, addrs in by_chain.items():
        for i in range(0, len(addrs), 30):
            chunk = addrs[i : i + 30]
            try:
                arr = fetch_json(f"{DEX}/tokens/v1/{chain}/" + ",".join(chunk)) or []
            except Exception:
                continue
            for p in arr:
                a = (p.get("baseToken") or {}).get("address")
                liq = (p.get("liquidity") or {}).get("usd") or 0
                k = (chain, a)
                if k not in best or liq > best[k][1]:
                    best[k] = (p, liq)

    items = []
    for (chain, addr), (p, _liq) in best.items():
        items.append(pair_item(p, {"description": desc_of.get((chain, addr), "")}))
    # token yang belum terindeks DexScreener (terlalu baru) -> bangun dari data gecko
    for k, (attrs, pool_addr) in gecko.items():
        if k not in best:
            items.append(gecko_item(k[0], k[1], attrs, pool_addr))

    # 5) verifikasi paralel (cache 10 menit) — gagal guard = tidak tampil;
    #    terlalu baru untuk diverifikasi = tampil, tapi ditandai belum verif
    with ThreadPoolExecutor(max_workers=6) as ex:
        levels = list(ex.map(lambda it: safety_level(it["chain"], it["address"]), items))
    checkable = {"solana"} | set(GOPLUS_CHAIN)  # chain yang punya pemeriksa otomatis
    out = []
    for it, s in zip(items, levels):
        lvl = s.get("level")
        if lvl in ("serious", "critical"):
            continue  # gagal guard — jangan tampilkan (aturan wajib)
        if it["ageHours"] is None or it["ageHours"] > 168:
            continue  # lebih tua dari 1 minggu — bukan lagi "early"
        if lvl == "unknown" and it["chain"] not in checkable:
            continue  # chain tanpa pemeriksa selamanya — "belum verif" abadi, cuma noise
        if it["ageHours"] < 0.5:
            # token < 30 menit: volume 24j belum bermakna — ukur lewat vol 15 menit
            if (it.get("volRecent") or it.get("vol24h") or 0) < 100:
                continue
        elif (it["vol24h"] or 0) < 500:
            continue
        it["safe"] = s
        it["verified"] = lvl in ("good", "warning")
        it["topics"] = match_topics(it, social)
        it["score"] = momentum_score(it)
        out.append(it)

    out.sort(key=lambda x: (-(x["score"] or 0), -(x["created"] or 0)))
    return {"total": len(out), "items": out[:40]}


def api_trending():
    """Trending dari DUA sumber, ditandai asalnya:
    - 'organik': trending_pools GeckoTerminal — vol/likuiditas NYATA (bukan bayaran)
    - 'boost'  : profil/boost DexScreener — dev bayar biar tampil (sinyal terlambat)
    Deskripsi token dibawa sebagai teks narasi."""
    entries = []
    for path in ("/token-boosts/top/v1", "/token-profiles/latest/v1"):
        try:
            res = fetch_json(DEX + path)
            if isinstance(res, list):
                entries += res
        except Exception:
            continue

    meta, order = {}, []
    for e in entries:
        key = (e.get("chainId"), e.get("tokenAddress"))
        if not key[0] or not key[1]:
            continue
        if key not in meta:
            meta[key] = e
            order.append(key)
        elif e.get("description") and not meta[key].get("description"):
            meta[key]["description"] = e.get("description")

    keys = order[:36]

    # trending organik GeckoTerminal — ranking dari vol/likuiditas nyata
    organic = set()
    for k in gecko_trending_pools():
        if k not in meta:
            meta[k] = {}
            keys.append(k)
        organic.add(k)

    # ambil statistik pair: endpoint tokens/v1 menerima maks 30 alamat per chain
    by_chain = {}
    for k in keys:
        by_chain.setdefault(k[0], []).append(k[1])
    detail = {}
    for chain, addrs in by_chain.items():
        for i in range(0, len(addrs), 30):
            chunk = addrs[i : i + 30]
            url = f"{DEX}/tokens/v1/{chain}/" + ",".join(chunk)
            try:
                arr = fetch_json(url) or []
            except Exception:
                continue
            for p in arr:
                a = (p.get("baseToken") or {}).get("address")
                liq = (p.get("liquidity") or {}).get("usd") or 0
                key = (chain, a)
                cur = detail.get(key)
                if cur is None or liq > cur[1]:
                    detail[key] = (p, liq)

    items = []
    for k in keys:
        if k in detail:
            it = pair_item(detail[k][0], meta.get(k))
            it["origin"] = "organik" if k in organic else "boost"
            items.append(it)
    items.sort(key=lambda x: x["vol24h"] or 0, reverse=True)
    return {"items": items[:30]}


def rugcheck_safety(address):
    d = fetch_json(f"{RUGCHECK}/v1/tokens/{address}/report/summary")
    risks = []
    for r in d.get("risks") or []:
        risks.append(
            {
                "name": r.get("name"),
                "level": r.get("level"),
                "value": str(r.get("value") or ""),
                "desc": r.get("description") or "",
            }
        )
    return {
        "source": "rugcheck",
        "score": d.get("score"),
        "scoreNorm": d.get("score_normalised"),
        "lpLockedPct": d.get("lpLockedPct"),
        "risks": risks,
    }


def goplus_risks(t):
    risks = []

    def flag(cond, name, level, value="", desc=""):
        if cond:
            risks.append({"name": name, "level": level, "value": value, "desc": desc})

    def fnum(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    flag(t.get("is_honeypot") == "1", "Honeypot — bisa beli, TIDAK bisa jual", "critical")
    flag(t.get("cannot_sell_all") == "1", "Ada pembatasan jual", "critical")
    flag(t.get("owner_change_balance") == "1", "Owner bisa utak-atik saldo", "critical")
    buy_tax, sell_tax = fnum(t.get("buy_tax")), fnum(t.get("sell_tax"))
    flag(sell_tax > 0.1, "Pajak jual tinggi", "serious", f"{sell_tax * 100:.0f}%")
    flag(buy_tax > 0.1, "Pajak beli tinggi", "serious", f"{buy_tax * 100:.0f}%")
    flag(t.get("slippage_modifiable") == "1", "Pajak bisa diubah kapan saja", "serious")
    flag(t.get("is_blacklisted") == "1", "Ada fungsi blacklist", "serious")
    flag(t.get("hidden_owner") == "1", "Owner tersembunyi", "serious")
    flag(t.get("is_open_source") != "1", "Kode kontrak tidak terverifikasi", "serious")
    flag(t.get("is_proxy") == "1", "Kontrak proxy — bisa di-upgrade", "warning")
    flag(t.get("trading_cooldown") == "1", "Ada cooldown trading", "warning")
    flag(
        t.get("is_anti_whale") == "1" and t.get("anti_whale_modifiable") == "1",
        "Batas anti-whale bisa diubah",
        "warning",
    )
    creator_pct = fnum(t.get("creator_percent"))
    flag(creator_pct > 5, "Creator pegang porsi besar", "warning", f"{creator_pct:.1f}%")
    return risks


def goplus_safety(chain, address):
    cid = GOPLUS_CHAIN.get(chain)
    if not cid:
        return {"source": None, "risks": [], "error": f"cek otomatis belum tersedia untuk chain '{chain}' — cek manual via explorer"}
    d = fetch_json(f"{GOPLUS}/api/v1/token_security/{cid}?contract_addresses={address}")
    res = (d.get("result") or {})
    t = res.get(address.lower()) or res.get(address) or {}
    if not t:
        return {"source": "goplus", "risks": [], "error": "token tidak ditemukan di GoPlus"}
    risks = goplus_risks(t)
    return {
        "source": "goplus",
        "risks": risks,
        "holders": t.get("holder_count"),
        "openSource": t.get("is_open_source") == "1",
        "renounced": (t.get("owner_address") or "").lower() == "0x0000000000000000000000000000000000000000",
        "buyTax": t.get("buy_tax"),
        "sellTax": t.get("sell_tax"),
    }


def api_verify(qs):
    """Verifikasi CA yang ditempel user: deteksi chain otomatis dari pair-nya,
    ambil data pair terbesar + cek keamanan penuh. Satu pintu sebelum entry."""
    raw = (qs.get("address") or [""])[0].strip()
    if not raw:
        return {"error": "parameter 'address' wajib"}
    addr = extract_address(raw)
    if not addr:
        return {"error": "alamat kontrak tidak dikenali — tempel alamat Solana (base58 32-44 karakter) atau EVM (0x + 40 hex)"}
    try:
        data = fetch_json(f"{DEX}/latest/dex/tokens/{urllib.parse.quote(addr)}")
    except Exception:
        return {"error": "gagal menghubungi DexScreener — coba lagi"}
    pairs = data.get("pairs") or []
    if not pairs:
        return {"error": "tidak ada pair dex untuk alamat ini — token belum punya pool, salah alamat, atau sudah mati"}
    best = max(pairs, key=lambda p: (p.get("liquidity") or {}).get("usd") or 0)
    item = pair_item(best)
    s = safety_level(item["chain"], item["address"])
    return {"token": item, "safe": s}


def extract_address(raw):
    """Ambil alamat kontrak dari teks tempelan apa pun (alamat polos atau URL
    gmgn/dexscreener). EVM dicek dulu supaya base58 tidak memotong hex."""
    m = re.search(r"0x[a-fA-F0-9]{40}", raw)
    if m:
        return m.group(0)
    m = re.search(r"[1-9A-HJ-NP-Za-km-z]{32,44}", raw)
    if m:
        return m.group(0)
    return None


def api_safety(qs):
    chain = (qs.get("chain") or [""])[0]
    address = (qs.get("address") or [""])[0]
    if not chain or not address:
        return {"error": "parameter 'chain' dan 'address' wajib"}
    if chain == "solana":
        return rugcheck_safety(address)
    return goplus_safety(chain, address)


# ---------- verifikasi batch: level ringkas per token, paralel + cache ----------

RANK = {"good": 0, "warning": 1, "serious": 2, "critical": 3}
SAFETY_CACHE = {}   # (chain, address) -> (timestamp, hasil)
SAFETY_TTL = 600    # 10 menit — skor rug jarang berubah lebih cepat dari itu


def level_from_safety(d):
    """Ringkas data keamanan jadi satu level — port dari logika frontend."""
    if d.get("error") and not d.get("risks"):
        return "unknown"
    if d.get("source") == "rugcheck":
        sc = d.get("scoreNorm")
        base = "warning" if sc is None else ("good" if sc < 30 else "warning" if sc < 60 else "critical")
    else:
        base = "good"
    lvl = base
    for r in d.get("risks") or []:
        rl = {"danger": "serious", "warn": "warning"}.get(r.get("level"))
        if rl is None and r.get("level") in RANK:
            rl = r["level"]
        if rl and RANK[rl] > RANK[lvl]:
            lvl = rl
    return lvl


def safety_level(chain, address):
    """Data keamanan satu token + level ringkas; hasil di-cache 10 menit."""
    key = (chain, address)
    hit = SAFETY_CACHE.get(key)
    if hit and time.time() - hit[0] < SAFETY_TTL:
        return hit[1]
    try:
        d = rugcheck_safety(address) if chain == "solana" else goplus_safety(chain, address)
    except Exception as e:
        d = {"source": None, "risks": [], "error": str(e)}
    d["level"] = level_from_safety(d)
    SAFETY_CACHE[key] = (time.time(), d)
    return d


def api_safety_batch(qs):
    """Verifikasi banyak token sekaligus: ?t=chain:addr,chain:addr,... (maks 40).
    Paralel 6 worker supaya N token tidak diperiksa berurutan belasan detik."""
    spec = (qs.get("t") or [""])[0]
    if not spec:
        return {"error": "parameter 't' wajib: chain:address,chain:address,..."}
    tokens = []
    for part in spec.split(","):
        chain, _, addr = part.strip().partition(":")
        if chain and addr:
            tokens.append((chain, addr))
    tokens = tokens[:40]
    if not tokens:
        return {"error": "tidak ada token valid di parameter 't'"}
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda ca: safety_level(*ca), tokens))
    return {"items": {f"{c}:{a}": d for (c, a), d in zip(tokens, results)}}




# ---------- pintu Vercel: bungkus fungsi api_* jadi serverless handler ----------
# Vercel Python runtime menjalankan class `handler(BaseHTTPRequestHandler)`
# per file di api/ — lewat ini satu logika dipakai lokal maupun serverless.
def make_handler(fn):
    # sebagian api_* menerima qs (search/safety/...), sebagian tidak
    # (social/trending/potential) — deteksi lewat signature supaya dua-duanya cocok
    takes_qs = bool(inspect.signature(fn).parameters)

    class ApiHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass  # sunyi supaya log Vercel bersih

        def do_GET(self):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                body, code = (fn(qs) if takes_qs else fn()), 200
            except urllib.error.HTTPError as e:
                body, code = {"error": f"API upstream error {e.code}"}, 502
            except Exception as e:
                body, code = {"error": f"{type(e).__name__}: {e}"}, 500
            payload = json.dumps(body).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

    return ApiHandler
