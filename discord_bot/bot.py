import discord
from discord import app_commands
from discord.ext import commands
import requests
import os
import logging

# LOGGING SETUP
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# CONFIGURATION
TOKEN = os.environ.get("DISCORD_TOKEN")
SERVER_URL = os.environ.get("SERVER_URL", "http://127.0.0.1:5000")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "CHANGE_THIS_IN_PROD")

if not TOKEN:
    logging.warning("DISCORD_TOKEN not set! Bot will fail to login.")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

@bot.tree.command(name="getkey", description="Generate a license key")
@app_commands.describe(duration="Duration in days or 'lifetime'")
async def getkey(interaction: discord.Interaction, duration: str):
    await interaction.response.defer(ephemeral=True)
    
    headers = {'X-API-KEY': ADMIN_API_KEY}
    payload = {'duration': duration}
    
    try:
        response = requests.post(f"{SERVER_URL}/generate", json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            await interaction.followup.send(f"✅ Generated Key: `{data['key']}`\nType: {data['type']}")
        else:
            await interaction.followup.send(f"❌ Error: {response.text}")
    except Exception as e:
        await interaction.followup.send(f"❌ Connection Error: {e}")

@bot.tree.command(name="resethwid", description="Reset HWID for a key")
async def resethwid(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    
    headers = {'X-API-KEY': ADMIN_API_KEY}
    payload = {'key': key}
    
    try:
        response = requests.post(f"{SERVER_URL}/reset", json=payload, headers=headers)
        if response.status_code == 200:
            await interaction.followup.send(f"✅ HWID Reset for key: `{key}`")
        else:
            await interaction.followup.send(f"❌ Error: {response.text}")
    except Exception as e:
        await interaction.followup.send(f"❌ Connection Error: {e}")

@bot.tree.command(name="deletekey", description="Delete a license key")
async def deletekey(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    
    headers = {'X-API-KEY': ADMIN_API_KEY}
    payload = {'key': key}
    
    try:
        response = requests.post(f"{SERVER_URL}/delete", json=payload, headers=headers)
        if response.status_code == 200:
            await interaction.followup.send(f"✅ Deleted key: `{key}`")
        else:
            await interaction.followup.send(f"❌ Error: {response.text}")
    except Exception as e:
        await interaction.followup.send(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    if TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("ERROR: Please put your Discord Bot Token in bot.py")
    else:
        bot.run(TOKEN)
