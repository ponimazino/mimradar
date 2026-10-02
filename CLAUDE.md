# CLAUDE.md

Project: **Meme Radar** (`mimradar.vercel.app`) — dashboard cari token meme early berbasis narasi social.

## Perintah umum
- Jalankan lokal: `python server.py` → http://127.0.0.1:8765 (atau double-click `start.bat`)
- Logika inti ada di `serverlib.py` — dipakai bersama oleh `server.py` (lokal) dan `api/*.py` (Vercel Python Functions). Ubah logika di `serverlib.py`, BUKAN duplicate ke dua tempat.
- Frontend: `index.html` single-file (vanilla JS, tanpa build step)
- Deploy: `git push` ke `main` → auto-deploy Vercel. Jangan commit `.vercel/`, `tokenly.zip`
- Tidak ada dependensi Python eksternal (stdlib murni) — jangan tambahkan library berat tanpa alasan kuat

## Bahasa & konteks
- User berkomunikasi bahasa Indonesia — balas dalam bahasa Indonesia. Teks UI juga bahasa Indonesia.
- Semua API upstream gratis tanpa key: DexScreener, RugCheck, GoPlus, Google Trends RSS, trends24.in (scrape), 4chan /biz/ (JSON publik)

---

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.