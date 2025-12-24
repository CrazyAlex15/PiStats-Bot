# 🥧 PiStats Monitor Bot

A lightweight and efficient Discord Bot designed specifically for **Raspberry Pi**. It monitors system health (Temperature, CPU, RAM) and displays it in real-time.

🔗 **[Click here to add the Bot to your Server](https://discord.com/oauth2/authorize?client_id=1453181396955959429&permissions=84992&integration_type=0&scope=bot+applications.commands)**

---

## 📊 Features

* **Live Status:** The bot automatically updates its status every 30 seconds, displaying:
    * 🔥 CPU Temperature
    * 🧠 RAM Usage
    * ⚙️ CPU Load
* **Slash Command `/status`:** Displays a detailed, color-coded Embed containing:
    * 🌡️ Exact Temperature (Celsius)
    * 💾 Disk/SD Card Capacity & Usage
    * ⏱️ Uptime (How long the Pi has been running)
    * 🐧 Operating System Information
* **Smart Colors:** The Embed turns **Red** if the system is under heavy load and **Green** if everything is healthy.

---

## 🛠️ Installation

If you want to host this bot on your own Raspberry Pi:

### 1. Clone Repository
```bash
git clone [https://github.com/CrazyAlex15/PiStats-Bot.git](https://github.com/CrazyAlex15/PiStats-Bot.git)
cd PiStats-Bot
2. Environment Setup
Bash

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
3. Configuration (.env)
Create a .env file and add your Bot Token:

Ini, TOML

DISCORD_TOKEN=your_bot_token_here
4. Run
Bash

python main.py
🚀 Hosting (24/7 on Raspberry Pi)
To keep the bot running in the background, use PM2:

Bash

# Start the process
pm2 start main.py --name "PiMonitor" --interpreter ./venv/bin/python3

# Save process list (for auto-start after reboot)
pm2 save
pm2 startup
📝 Permissions
The bot requires minimal permissions to function:

Send Messages

Embed Links (Required for statistics display)

Use Application Commands (Required for /status)

Developed with ❤️ by CrazyAlex