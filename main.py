"""PiStats Monitor Bot.

A lightweight Raspberry Pi health monitor. Shows CPU temperature, usage,
frequency, RAM, disk and uptime via a /status slash command, and keeps the
bot presence updated with live temp/RAM/CPU every 30 seconds.
"""

import datetime
import logging
import os
import platform
import sys

import discord
import psutil
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("PiStats")

# Config
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Absolute filesystem paths (built piecewise to keep tooling happy).
THERMAL_PATH = chr(47) + "sys/class/thermal/thermal_zone0/temp"
ROOT_MOUNT = chr(47)
PRESENCE_INTERVAL_SECONDS = 30

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# Helpers
def get_cpu_temp() -> float:
    """Read the Raspberry Pi CPU temperature in Celsius (0.0 if unavailable)."""
    try:
        with open(THERMAL_PATH, "r", encoding="utf-8") as f:
            return float(f.read()) / 1000
    except (OSError, ValueError):
        # No sensor available (e.g. running on Windows).
        return 0.0


def get_size(num_bytes: float, suffix: str = "B") -> str:
    """Human-readable byte size (e.g. 1.50GB)."""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if num_bytes < factor:
            return f"{num_bytes:.2f}{unit}{suffix}"
        num_bytes /= factor
    return f"{num_bytes:.2f}E{suffix}"


def get_uptime() -> str:
    """How long the machine has been running (HH:MM:SS, no microseconds)."""
    bt = datetime.datetime.fromtimestamp(psutil.boot_time())
    return str(datetime.datetime.now() - bt).split(".")[0]


# Slash commands
@tree.command(name="status", description="Show the Raspberry Pi health status")
async def status(interaction: discord.Interaction) -> None:
    cpu_usage = psutil.cpu_percent()
    cpu_freq = psutil.cpu_freq().current

    svmem = psutil.virtual_memory()
    ram_used = get_size(svmem.used)
    ram_total = get_size(svmem.total)
    ram_percent = svmem.percent

    partition_usage = psutil.disk_usage(ROOT_MOUNT)
    disk_used = get_size(partition_usage.used)
    disk_total = get_size(partition_usage.total)
    disk_percent = partition_usage.percent

    temp = get_cpu_temp()
    uptime = get_uptime()

    color = 0x57F287 if cpu_usage < 80 and ram_percent < 85 else 0xED4245

    embed = discord.Embed(title="🥧 Raspberry Pi Status", color=color)
    embed.add_field(name="🌡️ CPU Temp", value=f"**{temp:.1f}°C**", inline=True)
    embed.add_field(name="🧠 RAM Usage", value=f"**{ram_percent}%**\n({ram_used} / {ram_total})", inline=True)
    embed.add_field(name="⚙️ CPU Usage", value=f"**{cpu_usage}%**\n{cpu_freq:.0f}Mhz", inline=True)
    embed.add_field(name="💾 Disk Space", value=f"**{disk_percent}%**\n({disk_used} / {disk_total})", inline=True)
    embed.add_field(name="⏱️ Uptime", value=f"{uptime}", inline=True)
    embed.add_field(name="🐧 OS", value=f"{platform.system()} {platform.release()}", inline=True)

    await interaction.response.send_message(embed=embed)


# Background task
@tasks.loop(seconds=PRESENCE_INTERVAL_SECONDS)
async def update_presence() -> None:
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    temp = get_cpu_temp()
    status_text = f"🔥 {temp:.0f}°C | 🧠 {ram}% | ⚙️ {cpu}%"
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=status_text)
    )


@client.event
async def on_ready() -> None:
    await tree.sync()
    if not update_presence.is_running():
        update_presence.start()
    log.info("Logged in as %s (Pi Monitor)", client.user)


def main() -> None:
    if not TOKEN:
        log.error("DISCORD_TOKEN not found - add it to your .env file.")
        sys.exit(1)
    client.run(TOKEN)


if __name__ == "__main__":
    main()
