import os, asyncio, requests, feedparser, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- 🛰️ CONFIGURATION ---
TOKEN = '8342749669:AAGfsbIGh4Mk8WPpRtviT4yZTmyzC-Eg8Fk'
ADMIN_ID = 7567720140 # သင်၏ ID
is_maintenance = False # ပြုပြင်ထိန်းသိမ်းမှု အခြေအနေ

# --- 🌍 INTELLIGENCE ENGINES ---
def get_crypto():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin,tether&vs_currencies=usd"
        return requests.get(url, timeout=5).json()
    except: return None

def get_news(src):
    urls = {"mm": "https://www.bbc.com/burmese/index.xml", "gl": "https://www.aljazeera.com/xml/rss/all.xml"}
    try:
        resp = requests.get(urls.get(src), timeout=10)
        feed = feedparser.parse(resp.content)
        return feed.entries[:5]
    except: return []

# --- 🎨 UI BUILDER ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Maintenance Check
    if is_maintenance and user_id != ADMIN_ID:
        text = (
            "<b>⚠️ JUICE OMNI-NEXUS - MAINTENANCE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "စနစ်အား ခေတ္တပြုပြင်ထိန်းသိမ်းနေပါသည်။\n"
            "ပိုမိုကောင်းမွန်သော ဝန်ဆောင်မှုပေးနိုင်ရန် ကြိုးစားနေပါသည်။ ✨"
        )
        await update.message.reply_html(text)
        return

    text = (
        "<b>🌌 JUICE OMNI-NEXUS v60.0</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎬 <b>Media:</b> Send link to download.\n"
        "🎬 <b>Media:</b> ဒေါင်းလုဒ်လုပ်ရန် Link ပို့ပါ။\n\n"
        "📰 <b>News:</b> Global & Local Updates.\n"
        "📰 <b>သတင်းများ:</b> ကမ္ဘာ့သတင်းနှင့် ပြည်တွင်းသတင်း။"
    )
    kb = [
        [InlineKeyboardButton("📊 Crypto Prices", callback_data="crypto"),
         InlineKeyboardButton("🇲🇲 Myanmar News", callback_data="news_mm")],
        [InlineKeyboardButton("🌐 World News", callback_data="news_gl"),
         InlineKeyboardButton("🔄 Refresh", callback_data="home")]
    ]
    
    # Admin Panel Button
    if user_id == ADMIN_ID:
        kb.append([InlineKeyboardButton("⚙️ Admin Control Panel", callback_data="admin_panel")])
    
    markup = InlineKeyboardMarkup(kb)
    if update.message:
        await update.message.reply_html(text, reply_markup=markup)
    else:
        await update.callback_query.message.edit_text(text, reply_markup=markup, parse_mode='HTML')

# --- 🕹️ BUTTON & LOGIC HANDLER ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    global is_maintenance
    
    if is_maintenance and user_id != ADMIN_ID:
        await query.answer("Maintenance Mode Active", show_alert=True)
        return

    await query.answer()
    
    if query.data == "home":
        await start(update, context)
        
    elif query.data == "crypto":
        d = get_crypto()
        text = f"<b>📊 LIVE CRYPTO MARKET</b>\n\n₿ BTC: ${d['bitcoin']['usd']:,}\nΞ ETH: ${d['ethereum']['usd']:,}\n☀️ SOL: ${d['solana']['usd']:,}"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="home")]]), parse_mode='HTML')
        
    elif "news_" in query.data:
        src = query.data.split("_")[1]
        ns = get_news(src)
        text = f"<b>📰 {'BURMESE' if src=='mm' else 'WORLD'} NEWS</b>\n\n"
        text += "\n\n".join([f"• <a href='{e.link}'>{e.title}</a>" for e in ns])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="home")]]), parse_mode='HTML', disable_web_page_preview=True)
        
    elif query.data == "admin_panel" and user_id == ADMIN_ID:
        status = "🔴 Active" if is_maintenance else "🟢 Normal"
        text = f"<b>⚙️ ADMIN CONTROL PANEL</b>\n━━━━━━━━━━━━━━━━━━━━\nStatus: <b>{status}</b>"
        kb = [[InlineKeyboardButton("🛠 ON", callback_data="m_on"), InlineKeyboardButton("🚀 OFF", callback_data="m_off")], [InlineKeyboardButton("🔙 Back", callback_data="home")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
        
    elif query.data == "m_on": is_maintenance = True; await query.answer("Maintenance Mode: ON")
    elif query.data == "m_off": is_maintenance = False; await query.answer("Maintenance Mode: OFF")

# --- 🎬 MEDIA DOWNLOADER ---
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_maintenance and update.effective_user.id != ADMIN_ID: return
    url = update.message.text
    if "http" not in url: return
    kb = [[InlineKeyboardButton("🎬 Video", callback_data=f"vid|{url}"), InlineKeyboardButton("🎵 MP3", callback_data=f"aud|{url}")]]
    await update.message.reply_html("✨ <b>Media Detected!</b> Choose format:", reply_markup=InlineKeyboardMarkup(kb))

# --- 🚀 MAIN RUNNER ---
def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_media))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("JUICE v60.0 Ultimate is Online...")
    app.run_polling()

if __name__ == '__main__': main()
