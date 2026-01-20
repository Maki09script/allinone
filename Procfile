web: gunicorn --chdir license_server app:app --bind 0.0.0.0:$PORT --log-file -
worker: python discord_bot/bot.py
