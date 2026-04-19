import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)

# ------------------- কনফিগারেশন -------------------
# Render এর এনভায়রনমেন্ট থেকে টোকেন নেওয়া হবে
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    logging.error("TELEGRAM_TOKEN environment variable not set!")
    exit(1)

# API endpoint for country data
REST_COUNTRIES_API = "https://restcountries.com/v3.1/all?fields=name,flags,cca2"

# ------------------- ডেটা প্রসেসিং -------------------
def fetch_top_countries():
    """API থেকে সব দেশ এনে জনসংখ্যা অনুযায়ী সাজিয়ে Top 20 রিটার্ন করে"""
    try:
        response = requests.get(REST_COUNTRIES_API, timeout=10)
        response.raise_for_status()
        countries = response.json()
        
        # জনসংখ্যা নেই এমন দেশ বাদ দিয়ে সাজানো
        valid_countries = [c for c in countries if 'population' in c and c['population'] > 0]
        sorted_countries = sorted(valid_countries, key=lambda x: x['population'], reverse=True)
        
        top_20 = []
        for c in sorted_countries[:20]:
            name = c['name']['common']
            flag = c.get('flags', {}).get('emoji', '🏳️')
            top_20.append(f"{flag} {name}")
        return top_20
    except Exception as e:
        logging.error(f"API Error: {e}")
        return ["🇺🇸 United States", "🇨🇳 China", "🇮🇳 India", "🇯🇵 Japan", "🇩🇪 Germany"] # Fallback

# ------------------- বট কমান্ডস -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start কমান্ড হ্যান্ডলার। কাস্টম কিবোর্ড দেখাবে"""
    # কাস্টম কীবোর্ড তৈরি (প্রতি লাইনে ২ বাটন)
    keyboard = [["📊 Show Top 20 Countries"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        "🌟 **Welcome to World Ranking Bot** 🌟\n\n"
        "I have the list of the world's largest countries by population.\n"
        "Click the button below to see the Top 20:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_countries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বাটন প্রেস বা টেক্সট কমান্ড হ্যান্ডল করে"""
    # টাইপিং ইন্ডিকেটর দেখান (ইউজার এক্সপেরিয়েন্স ভালো করার জন্য)
    await update.message.chat.send_action(action="typing")
    
    # ডাটা fetch করুন
    top_20_list = fetch_top_countries()
    
    # সুন্দর মেসেজ ফরম্যাটিং
    message = "*🌍 Global Power Rankings (Top 20 by Population)*\n\n"
    for idx, country in enumerate(top_20_list, start=1):
        message += f"{idx}. {country}\n"
    
    message += "\n📊 *Source:* World Population Review"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """টেক্সট মেসেজ হ্যান্ডলার (বাটন কাজ না করলে ব্যাকআপ)"""
    text = update.message.text
    if "Show Top 20" in text or "countries" in text.lower():
        await show_countries(update, context)
    else:
        await update.message.reply_text("Please use the button below to see the list.")

# ------------------- মেইন ফাংশন -------------------
def main():
    """বট রান করার মূল ফাংশন"""
    # অ্যাপ্লিকেশন তৈরি
    app = Application.builder().token(TOKEN).build()
    
    # হ্যান্ডলার রেজিস্ট্রি
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("top", show_countries))
    app.add_handler(CommandHandler("countries", show_countries))
    app.add_handler(CommandHandler("list", show_countries))
    app.add_handler(CommandHandler("show", show_countries))
    app.add_handler(CommandHandler("world", show_countries))
    app.add_handler(CommandHandler("rank", show_countries))
    app.add_handler(CommandHandler("global", show_countries))
    app.add_handler(CommandHandler("population", show_countries))
    app.add_handler(CommandHandler("largest", show_countries))
    app.add_handler(CommandHandler("biggest", show_countries))
    app.add_handler(CommandHandler("top20", show_countries))
    app.add_handler(CommandHandler("top_20", show_countries))
    app.add_handler(CommandHandler("ranking", show_countries))
    app.add_handler(CommandHandler("leaderboard", show_countries))
    
    # মেসেজ হ্যান্ডলার (বাটনের জন্য)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # পোলিং শুরু করুন (Render এ এটি কাজ করবে, বা লোকালি)
    print("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
