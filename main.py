# main.py
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, DEFAULT_COUNTRY, DEFAULT_SERVICE
from handlers import (
    start_command, balance_command, get_number_command,
    status_command, cancel_command, complete_command,
    countries_command, services_command, help_command,
    button_callback
)

def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("get_number", get_number_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("complete", complete_command))
    app.add_handler(CommandHandler("countries", countries_command))
    app.add_handler(CommandHandler("services", services_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Button callback handler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("=" * 50)
    print("✅ HeroSMS Bot Started Successfully!")
    print(f"🇮🇳 Default Country ID: {DEFAULT_COUNTRY} (India)")
    print(f"📱 Default Service: {DEFAULT_SERVICE} (WhatsApp)")
    print("=" * 50)
    print("Commands: /start, /balance, /get_number, /status, /cancel, /complete")
    print("=" * 50)
    
    app.run_polling()

if __name__ == "__main__":
    main()