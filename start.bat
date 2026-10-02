@echo off
rem Meme Radar - jalankan dashboard lalu buka browser
cd /d %~dp0
start "" http://127.0.0.1:8765
python server.py