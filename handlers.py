# handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import DEFAULT_COUNTRY, DEFAULT_SERVICE, STATUS_CODES, SERVICES, COUNTRIES
from utils import (
    make_api_request, parse_balance_response, 
    parse_number_v2_response, get_country_name, 
    get_service_name, format_phone_number
)

user_activations = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("📱 Get Number", callback_data="get_number")],
        [InlineKeyboardButton("🌍 Countries", callback_data="countries")],
        [InlineKeyboardButton("📋 Services", callback_data="services")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 **HeroSMS Bot**\n\n"
        "I help you buy virtual numbers and receive SMS verification codes.\n\n"
        f"🇮🇳 **Default Country:** India (ID: {DEFAULT_COUNTRY})\n"
        f"📱 **Default Service:** WhatsApp (wa)\n\n"
        "Use the buttons below 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔄 Checking balance...")
    
    response = make_api_request("getBalance")
    balance = parse_balance_response(response)
    
    if balance is not None:
        await msg.edit_text(
            f"💰 **Your Balance:** `${balance}` USD\n\n"
            f"🔹 Price per number: `$0.05` - `$0.50` USD\n"
            f"🔹 WhatsApp numbers: `$0.15` - `$0.35` USD",
            parse_mode="Markdown"
        )
    else:
        await msg.edit_text(f"❌ Failed to get balance!\nResponse: {response}")

async def get_number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country = context.args[0] if context.args else DEFAULT_COUNTRY
    service = context.args[1] if len(context.args) > 1 else DEFAULT_SERVICE
    
    msg = await update.message.reply_text(
        f"🔄 Requesting number...\n"
        f"🇮🇳 Country: {get_country_name(country)}\n"
        f"📱 Service: {get_service_name(service)}"
    )
    
    response = make_api_request("getNumberV2", {
        "country": country,
        "service": service
    })
    
    data = parse_number_v2_response(response)
    
    if data and "activationId" in data:
        user_activations[update.effective_user.id] = data["activationId"]
        
        keyboard = [[
            InlineKeyboardButton("🔄 Check Status", callback_data=f"status_{data['activationId']}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{data['activationId']}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        phone_formatted = format_phone_number(data['phoneNumber'])
        
        await msg.edit_text(
            f"✅ **Number Received!**\n\n"
            f"📱 **Number:** `{phone_formatted}`\n"
            f"🆔 **Activation ID:** `{data['activationId']}`\n"
            f"💰 **Cost:** `${data.get('activationCost', 'N/A')}` USD\n"
            f"🇮🇳 **Country:** {get_country_name(data.get('countryCode', country))}\n"
            f"⏰ **Expires:** {data.get('activationEndTime', 'N/A')}\n\n"
            f"📌 Send SMS to this number. The code will appear here.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await msg.edit_text(f"❌ No numbers available!\nResponse: {response}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activation_id = context.args[0] if context.args else user_activations.get(update.effective_user.id)
    
    if not activation_id:
        await update.message.reply_text(
            "❌ No activation ID found!\n"
            "Usage: `/status <activation_id>`",
            parse_mode="Markdown"
        )
        return
    
    msg = await update.message.reply_text(f"🔄 Checking status for ID: {activation_id}")
    
    response = make_api_request("getStatus", {"id": activation_id})
    
    if response.startswith("STATUS_OK"):
        code = response.split(":")[1] if ":" in response else "Not found"
        await msg.edit_text(
            f"✅ **Code Received!**\n\n"
            f"🔑 **Verification Code:** `{code}`\n\n"
            f"Use this code to verify your account.",
            parse_mode="Markdown"
        )
    elif response in STATUS_CODES:
        await msg.edit_text(f"📊 **Status:** {STATUS_CODES[response]}")
    else:
        await msg.edit_text(f"📊 Response: {response}")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activation_id = context.args[0] if context.args else user_activations.get(update.effective_user.id)
    
    if not activation_id:
        await update.message.reply_text(
            "❌ No activation ID found!\n"
            "Usage: `/cancel <activation_id>`",
            parse_mode="Markdown"
        )
        return
    
    msg = await update.message.reply_text(f"🔄 Canceling activation {activation_id}...")
    
    response = make_api_request("setStatus", {"id": activation_id, "status": 8})
    
    if response == "ACCESS_CANCEL":
        await msg.edit_text(
            f"✅ Activation `{activation_id}` successfully canceled!\n"
            f"Your money will be refunded.",
            parse_mode="Markdown"
        )
    else:
        await msg.edit_text(f"❌ Failed to cancel!\nResponse: {response}")

async def complete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activation_id = context.args[0] if context.args else user_activations.get(update.effective_user.id)
    
    if not activation_id:
        await update.message.reply_text(
            "❌ No activation ID found!\n"
            "Usage: `/complete <activation_id>`",
            parse_mode="Markdown"
        )
        return
    
    msg = await update.message.reply_text(f"🔄 Completing activation {activation_id}...")
    
    response = make_api_request("setStatus", {"id": activation_id, "status": 6})
    
    if response == "ACCESS_ACTIVATION":
        await msg.edit_text(
            f"✅ Activation `{activation_id}` completed!\n"
            f"Thank you for using our service.",
            parse_mode="Markdown"
        )
    else:
        await msg.edit_text(f"❌ Failed to complete!\nResponse: {response}")

async def countries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🌍 **Supported Countries:**\n\n"
    for cid, name in COUNTRIES.items():
        default = " (Default)" if cid == DEFAULT_COUNTRY else ""
        text += f"🔹 **{name}** (ID: {cid}){default}\n"
    
    text += "\n📌 Usage: `/get_number <country_id> <service>`\n"
    text += "Example: `/get_number 4 wa` (India - WhatsApp)"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 **Supported Services:**\n\n"
    
    for code, name in SERVICES.items():
        default = " (Default)" if code == DEFAULT_SERVICE else ""
        text += f"🔹 **{name}** (Code: `{code}`){default}\n"
    
    text += "\n📌 **WhatsApp (wa) is now default!**\n"
    text += "Usage: `/get_number <country_id> <service_code>`\n"
    text += "Example: `/get_number 4 wa` (India - WhatsApp)\n"
    text += "Example: `/get_number 4 tg` (India - Telegram)"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 **HeroSMS Bot Help**

🔹 **Commands:**
/start - Start the bot
/balance - Check your balance
/get_number <country_id> <service> - Get a new number
/status <activation_id> - Check activation status
/cancel <activation_id> - Cancel activation
/complete <activation_id> - Complete activation
/countries - List all countries
/services - List all services

🔹 **Examples:**
`/get_number 4 wa` - Get WhatsApp number from India
`/get_number 4 tg` - Get Telegram number from India
`/status 123456789` - Check activation status

🔹 **Popular Country IDs:**
- 4: India (Cheapest - Default)
- 5: USA
- 0: Russia
- 6: UK

🔹 **Service Codes:**
- wa: WhatsApp (Default)
- tg: Telegram
- fb: Facebook
- ig: Instagram

💰 **Add Funds:** [HeroSMS.com](https://hero-sms.com)
"""
    await update.message.reply_text(help_text, parse_mode="Markdown", disable_web_page_preview=True)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "balance":
        await balance_command(update, context)
    elif data == "get_number":
        keyboard = [
            [InlineKeyboardButton("🇮🇳 India (ID: 4) - WhatsApp", callback_data="quick_4_wa")],
            [InlineKeyboardButton("🇮🇳 India (ID: 4) - Telegram", callback_data="quick_4_tg")],
            [InlineKeyboardButton("🇺🇸 USA (ID: 5) - WhatsApp", callback_data="quick_5_wa")],
            [InlineKeyboardButton("🇬🇧 UK (ID: 6) - WhatsApp", callback_data="quick_6_wa")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select an option or use custom command:\n"
            "`/get_number <country_id> <service>`\n\n"
            "Example: `/get_number 4 wa`",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    elif data == "countries":
        await countries_command(update, context)
    elif data == "services":
        await services_command(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data.startswith("quick_"):
        parts = data.split("_")
        country = parts[1]
        service = parts[2]
        # Create a mock message object
        class MockMessage:
            def __init__(self, chat_id, text):
                self.chat_id = chat_id
                self.text = text
        class MockUpdate:
            def __init__(self, chat_id, user_id):
                self.message = MockMessage(chat_id, "")
                self.effective_user = type('obj', (object,), {'id': user_id})()
                self.callback_query = query
        mock_update = MockUpdate(query.message.chat_id, query.from_user.id)
        context.args = [country, service]
        await get_number_command(mock_update, context)
    elif data.startswith("status_"):
        activation_id = data.split("_")[1]
        context.args = [activation_id]
        await status_command(update, context)
    elif data.startswith("cancel_"):
        activation_id = data.split("_")[1]
        context.args = [activation_id]
        await cancel_command(update, context)