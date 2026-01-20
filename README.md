# All-In-One License System

A complete, production-ready license system with a securely encrypted Client EXE, Flask backend, and Discord Bot management interface.

## 📂 Project Structure
```
license_system/
├── discord_bot/       # Discord Bot for Key Management
├── license_server/    # Flask API & SQLite DB
├── product_client/    # Customer Launcher (Client)
├── string_cleaner/    # The Protected App
└── setup_scripts/     # Automation Scripts
```

## 🚀 Quick Start (Local)

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Secrets**
    *   Edit `license_server/app.py` -> `ADMIN_API_KEY`, `CLIENT_SECRET`
    *   Edit `discord_bot/bot.py` -> `TOKEN`
    *   Edit `product_client/api_client.py` -> `CLIENT_SECRET`

3.  **Run System**
    *   Windows: Double-click `start_system.bat`
    *   Linux: Run `./server_setup.sh`

## ☁️ Deployment (Render)
This project includes a `render.yaml` Blueprint for auto-deployment.

1.  **Push to GitHub** (Use `setup_and_deploy.py`).
2.  Go to **Render Dashboard** -> **New** -> **Blueprint**.
3.  Select your repo.
4.  Render will automatically detect the Server and Bot.
5.  **Input your Secrets** (Discord Token) when prompted.


## 🤖 Discord Commands
*   `/getkey <duration>`: Generate a key (e.g., `lifetime` or `30`).
*   `/resethwid <key>`: Unlock a key for a new PC.
*   `/deletekey <key>`: Ban/Revoke a license.
*   `/status`: Check server health.

## 📦 Building Customer EXE
To build the protected launcher for your customers:

```bash
pyinstaller --noconfirm --onefile --windowed --name "MakiCleaner" --key "YOUR_SECRET_KEY" --add-data "string_cleaner;string_cleaner" product_client/launch_auth.py
```

## 🔗 API Endpoints
*   **GET /status**: Check if online.
*   **POST /validate**: `{key, hwid, signature, timestamp}` -> Validates license.
*   **POST /generate**: Admin only.
*   **POST /reset**: Admin only.
