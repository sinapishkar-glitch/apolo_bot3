import csv
import os
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ==== توکن بات: یا اینجا مستقیم بنویسید، یا از متغیر محیطی BOT_TOKEN بخوانید ====
BOT_TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")

# ==== آیدی عددی تلگرام شما (ادمین) — فقط همین آیدی می‌تواند /export را اجرا کند ====
# برای گرفتن آیدی عددی خودتان، به بات @userinfobot پیام بدهید.
ADMIN_ID = os.environ.get("ADMIN_ID", "")

# مراحل مکالمه
NAME, GRADE, FIELD, PHONE = range(4)

DATA_FILE = "registrations.csv"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "برای ثبت‌نام در وبینار آپولو، نام و نام خانوادگی خود را وارد کنید:"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("پایه تحصیلی خود را وارد کنید:")
    return GRADE


async def get_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    await update.message.reply_text("رشته تحصیلی خود را وارد کنید:")
    return FIELD


async def get_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["field"] = update.message.text
    await update.message.reply_text("شماره همراه خود برای ورود به وبینار را وارد کنید:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    user = update.effective_user

    # ذخیره در فایل CSV
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                ["تاریخ", "آیدی تلگرام", "یوزرنیم", "نام", "پایه", "رشته", "شماره همراه"]
            )
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            user.id,
            user.username or "-",
            context.user_data["name"],
            context.user_data["grade"],
            context.user_data["field"],
            context.user_data["phone"],
        ])

    await update.message.reply_text(
        "ثبت‌نام شما با موفقیت انجام شد! ✅\n\n"
        "برای دریافت لینک ورود به وبینار، در کانال زیر عضو شوید:\n"
        "https://t.me/Apolo_konkur402"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ثبت‌نام لغو شد.")
    return ConversationHandler.END


async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # فقط ادمین اجازه دارد فایل را بگیرد
    if ADMIN_ID and user_id != ADMIN_ID:
        await update.message.reply_text("شما اجازه دسترسی به این دستور را ندارید.")
        return

    if not os.path.isfile(DATA_FILE):
        await update.message.reply_text("هنوز هیچ ثبت‌نامی انجام نشده است.")
        return

    with open(DATA_FILE, "rb") as f:
        await update.message.reply_document(document=f, filename=DATA_FILE)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.UpdateType.MESSAGE, get_name)],
            GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.UpdateType.MESSAGE, get_grade)],
            FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.UpdateType.MESSAGE, get_field)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.UpdateType.MESSAGE, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("export", export_data))
    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
