@echo off
title Maki License Server & Bot
echo --- Installing Dependencies ---
pip install -r requirements.txt
echo.
echo --- Starting License Server (Port 5000) ---
start "Maki License Server" python license_server/app.py
echo Server started in new window...
echo.
echo --- Starting Discord Bot ---
echo NOTE: Bot will crash if TOKEN is not set in discord_bot/bot.py
start "Maki Discord Bot" python discord_bot/bot.py
echo Bot started in new window...
echo.
echo Setup Complete. Do not close the other windows.
pause
