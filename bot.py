import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from asgiref.sync import sync_to_async
from bingo_app.models import UserProfile
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# የቦትህን ቶከን እዚህ አስገባ
BOT_TOKEN = "8621772695:AAEq4_K8r3JdTJhKHx4b3vmnbuHeP3LFbcs" 

# ከኋላ የነበረው '/' ተወግዷል (double slash እንዳይፈጥር)
WEB_APP_URL = "https://edilbingo-qmd2.onrender.com" 

# ዳታቤዙን ከቦቱ ጋር የሚያግባቡ ፈንክሽኖች
@sync_to_async
def get_or_create_profile(user_id, first_name):
    return UserProfile.objects.get_or_create(telegram_id=user_id, defaults={'first_name': first_name})

@sync_to_async
def get_profile(user_id):
    return UserProfile.objects.get(telegram_id=user_id)

@sync_to_async
def save_phone_number(user_id, phone):
    profile = UserProfile.objects.get(telegram_id=user_id)
    profile.phone_number = phone
    profile.save()
    return profile

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    profile, created = await get_or_create_profile(user.id, user.first_name)

    if not profile.phone_number:
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(text="📱 ስልክ ቁጥር አጋራ (Register)", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"ሰላም {user.first_name}፣ ወደ እደል ቢንጎ እንኳን በደህና መጡ!\n\nለመመዝገብ ከታች ያለውን 'ስልክ ቁጥር አጋራ' የሚለውን ይጫኑ፡", reply_markup=keyboard)
    else:
        await main_menu(update, profile)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone = update.message.contact.phone_number
    profile = await save_phone_number(user_id, phone)
    
    # የስልክ መላኪያ በተኑን ከስክሪኑ ላይ ያጠፋዋል
    await update.message.reply_text("✅ በተሳካ ሁኔታ ተመዝግበዋል!", reply_markup=ReplyKeyboardRemove())
    await main_menu(update, profile)

async def main_menu(update: Update, profile):
    keyboard = [
        [InlineKeyboardButton("🎮 Demo Mode (በነፃ መሞከሪያ)", web_app=WebAppInfo(url=f"{WEB_APP_URL}/?stake=0&tg_id={profile.telegram_id}"))],
        [
            InlineKeyboardButton("🎲 5 ብር ጨዋታ", web_app=WebAppInfo(url=f"{WEB_APP_URL}/?stake=5&tg_id={profile.telegram_id}")),
            InlineKeyboardButton("🎲 10 ብር ጨዋታ", web_app=WebAppInfo(url=f"{WEB_APP_URL}/?stake=10&tg_id={profile.telegram_id}"))
        ],
        [
            InlineKeyboardButton("💰 Deposit (ገንዘብ አስገባ)", callback_data="deposit"),
            InlineKeyboardButton("💸 Withdraw (ገንዘብ አውጣ)", callback_data="withdraw")
        ],
        [InlineKeyboardButton("👤 የኔ አካውንት (Profile)", callback_data="profile")]
    ]
    
    text = f"👤 ስም: {profile.first_name}\n📱 ስልክ: {profile.phone_number}\n💰 ቀሪ ሂሳብ: {profile.balance} ብር\n🎁 ዴሞ ሂሳብ: {profile.demo_balance} ብር\n\nየሚፈልጉትን አገልግሎት ይምረጡ:"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    profile = await get_profile(user_id)

    if query.data == "deposit":
        await query.message.reply_text("📥 ገንዘብ ለማስገባት፡\n\nበ CBE Birr ወይም Telebirr ወደ 1000123456789 ይላኩ።\nከዚያ የላኩበትን Transaction ID እዚህ ይጻፉ (ወደፊት በአድሚን አፕሩቭ ይደረጋል)።")
    elif query.data == "withdraw":
        await query.message.reply_text("📤 ገንዘብ ለማውጣት፡\n\nየባንክ አካውንትዎን እና ማውጣት የሚፈልጉትን መጠን ይጻፉ።")
    elif query.data == "profile":
        await main_menu(update, profile)

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()