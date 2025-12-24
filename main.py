import discord
from discord import app_commands
from discord.ext import tasks
import psutil
import os
import platform
import time
import datetime
from dotenv import load_dotenv

# Load Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup Bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# --- HELPER FUNCTIONS ---

def get_cpu_temp():
    """Διαβάζει τη θερμοκρασία του Raspberry Pi"""
    try:
        # Μέθοδος για Raspberry Pi / Linux
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read()) / 1000
        return temp
    except:
        # Αν δεν βρει αισθητήρα (π.χ. Windows)
        return 0.0

def get_size(bytes, suffix="B"):
    """Μετατρέπει τα bytes σε MB/GB"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_uptime():
    """Υπολογίζει πόση ώρα είναι ανοιχτό το Pi"""
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
    now = datetime.datetime.now()
    uptime = now - bt
    return str(uptime).split('.')[0] # Αφαιρεί τα milliseconds

# --- SLASH COMMANDS ---

@tree.command(name="status", description="Δες την κατάσταση υγείας του Raspberry Pi")
async def status(interaction: discord.Interaction):
    # CPU
    cpu_usage = psutil.cpu_percent()
    cpu_freq = psutil.cpu_freq().current
    
    # RAM
    svmem = psutil.virtual_memory()
    ram_used = get_size(svmem.used)
    ram_total = get_size(svmem.total)
    ram_percent = svmem.percent
    
    # DISK
    partition_usage = psutil.disk_usage('/')
    disk_used = get_size(partition_usage.used)
    disk_total = get_size(partition_usage.total)
    disk_percent = partition_usage.percent
    
    # TEMP & UPTIME
    temp = get_cpu_temp()
    uptime = get_uptime()

    # Χρώμα Embed (Πράσινο αν όλα καλά, Κόκκινο αν ζορίζεται)
    color = 0x57F287 if cpu_usage < 80 and ram_percent < 85 else 0xED4245

    embed = discord.Embed(title="🥧 Raspberry Pi Status", color=color)
    embed.add_field(name="🌡️ CPU Temp", value=f"**{temp:.1f}°C**", inline=True)
    embed.add_field(name="🧠 RAM Usage", value=f"**{ram_percent}%**\n({ram_used} / {ram_total})", inline=True)
    embed.add_field(name="⚙️ CPU Usage", value=f"**{cpu_usage}%**\n{cpu_freq:.0f}Mhz", inline=True)
    embed.add_field(name="💾 Disk Space", value=f"**{disk_percent}%**\n({disk_used} / {disk_total})", inline=True)
    embed.add_field(name="⏱️ Uptime", value=f"{uptime}", inline=True)
    embed.add_field(name="🐧 OS", value=f"{platform.system()} {platform.release()}", inline=True)
    
    await interaction.response.send_message(embed=embed)

# --- BACKGROUND TASK ---

@tasks.loop(seconds=30)
async def update_presence():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    temp = get_cpu_temp()
    
    status_text = f"🔥 {temp:.0f}°C | 🧠 {ram}% | ⚙️ {cpu}%"
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_text))

@client.event
async def on_ready():
    await tree.sync()
    update_presence.start()
    print(f"✅ Logged in as {client.user} (Pi Monitor)")

client.run(TOKEN)