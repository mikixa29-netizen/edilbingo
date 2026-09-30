import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from asgiref.sync import sync_to_async
from bingo_app.models import UserProfile, BotSetting, BotButton
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# የቦትህን ቶከን እዚህ አስገባ
BOT_TOKEN = "8621772695:AAEq4_K8r3JdTJhKHx4b3vmnbuHeP3LFbcs" 

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

@sync_to_async
def get_bot_setting():
    return BotSetting.objects.first()

@sync_to_async
def get_active_buttons():
    return list(BotButton.objects.filter(is_active=True).order_by('order'))

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
    
    await update.message.reply_text("✅ በተሳካ ሁኔታ ተመዝግበዋል!", reply_markup=ReplyKeyboardRemove())
    await main_menu(update, profile)

async def main_menu(update: Update, profile):
    # ከዳታቤዝ አድሚን ያስገባቸውን ሴቲንጎች እና በተኖች ማምጣት
    setting = await get_bot_setting()
    buttons = await get_active_buttons()
    
    admin_welcome_text = setting.welcome_text if setting and setting.welcome_text else "Welcome to Edil Bingo! Choose an option below."
    
    keyboard = []
    row = []
    
    for b in buttons:
        button_url = b.url if b.url else WEB_APP_URL
        if b.is_web_app:
            sep = "&" if "?" in button_url else "?"
            final_url = f"{button_url}{sep}tg_id={profile.telegram_id}"
            btn = InlineKeyboardButton(b.text, web_app=WebAppInfo(url=final_url))
        elif b.url:
            btn = InlineKeyboardButton(b.text, url=b.url)
        else:
            btn = InlineKeyboardButton(b.text, callback_data=f"btn_{b.id}")
        
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
        
    # ተጨማሪ መደበኛ የሂሳብ መቆጣጠሪያ በተኖች ካስፈለጉ እዚህ መጨመር ይቻላል
    
    text = (
        f"👤 ስም: {profile.first_name}\n"
        f"📱 ስልክ: {profile.phone_number}\n"
        f"💰 ቀሪ ሂሳብ: {profile.balance} ብር\n"
        f"🎁 ዴሞ ሂሳብ: {profile.demo_balance} ብር\n\n"
        f"{admin_welcome_text}"
    )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # ሎጎ (ፎቶ) ካለ በፎቶ ከሌለ በጽሑፍ ብቻ መላክ
    logo_path = setting.logo.path if (setting and setting.logo and os.path.exists(setting.logo.path)) else None

    if update.message:
        if logo_path:
            with open(logo_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        if logo_path:
            await update.callback_query.message.reply_photo(photo=open(logo_path, 'rb'), caption=text, reply_markup=reply_markup)
        else:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    profile = await get_profile(user_id)

    if query.data == "deposit":
        await query.message.reply_text("📥 ገንዘብ ለማስገባት፡\n\nበ CBE Birr ወይም Telebirr ወደ 1000123456789 ይላኩ።\nከዚያ የላኩበትን Transaction ID እዚህ ይጻፉ።")
    elif query.data == "withdraw":
        await query.message.reply_text("📤 ገንዘብ ለማውጣት፡\n\nየባንክ አካውንትዎን እና ማውጣት የሚፈልጉትን መጠን ይጻፉ።")
    elif query.data == "profile":
        await main_menu(update, profile)
    elif query.data.startswith("btn_"):
        await query.message.reply_text("መረጡት አማራጭ እየተስተናገደ ነው...")

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Dynamic Edil Bingo Bot is running...")
    app.run_polling()