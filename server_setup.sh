#!/bin/bash
# Maki License System - Production Setup Script (Ubuntu)
# Usage: sudo ./deploy.sh

echo "--- 1. System Update & Dependencies ---"
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx ufw

echo "--- 2. Python Environment Setup ---"
# Creating a dedicated user for security
if id "maki" &>/dev/null; then
    echo "User maki already exists"
else
    useradd -m -s /bin/bash maki
fi

# Clone/Copy code placeholder (User must upload files first!)
APP_DIR="/home/maki/bago"
mkdir -p $APP_DIR

echo "PLEASE NOTE: Upload your 'bago' folder content to $APP_DIR before making services live."
echo "Assuming files are present for setup..."

# Install Deps
pip3 install -r $APP_DIR/requirements.txt
pip3 install gunicorn

echo "--- 3. Systemd Service: License Server ---"
cat > /etc/systemd/system/maki-server.service <<EOL
[Unit]
Description=Gunicorn instance to serve Maki License Server
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=$APP_DIR/license_server
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/gunicorn --workers 3 --bind unix:maki.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
EOL

echo "--- 4. Systemd Service: Discord Bot ---"
cat > /etc/systemd/system/maki-bot.service <<EOL
[Unit]
Description=Maki Discord Bot
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR/discord_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

echo "--- 5. Nginx Reverse Proxy Setup ---"
cat > /etc/nginx/sites-available/maki <<EOL
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/license_server/maki.sock;
    }
}
EOL

ln -s /etc/nginx/sites-available/maki /etc/nginx/sites-enabled
rm /etc/nginx/sites-enabled/default
systemctl restart nginx

echo "--- 6. Security & Firewall ---"
ufw allow 'Nginx Full'
ufw allow ssh
ufw enable

echo "--- 7. Start Services ---"
systemctl daemon-reload
systemctl start maki-server
systemctl enable maki-server
systemctl start maki-bot
systemctl enable maki-bot

echo "=== DEPLOYMENT SETUP COMPLETE ==="
echo "1. Upload your code to /home/maki/bago"
echo "2. Update /etc/nginx/sites-available/maki with your Domain/IP"
echo "3. Run: systemctl restart nginx maki-server maki-bot"
