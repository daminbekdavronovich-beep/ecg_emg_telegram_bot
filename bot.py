import numpy as np
import matplotlib.pyplot as plt
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = "8541718182:AAH_2oPg4ZfZARcUtsPWyF2rMM2dTL0awI0"

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🫀 ECG", callback_data="ecg"),
            InlineKeyboardButton("💪 EMG", callback_data="emg"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Qaysi signalni analiz qilamiz?",
        reply_markup=reply_markup
    )

# ===== BUTTON BOSILGANDA =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["signal_type"] = query.data

    await query.edit_message_text(
        f"{query.data.upper()} tanlandi.\n\nTXT fayl yuboring."
    )

# ===== FILE QABUL QILISH =====
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "signal_type" not in context.user_data:
        await update.message.reply_text("Avval /start bosib signal turini tanlang.")
        return

    signal_type = context.user_data["signal_type"]

    file = await update.message.document.get_file()
    file_bytes = await file.download_as_bytearray()

    try:
        data = np.loadtxt(io.BytesIO(file_bytes))

        if len(data.shape) > 1:
            # ECG 6-ustun, EMG 7-ustun deb olamiz
            if signal_type == "ecg":
                signal = data[:, 5]
            else:
                signal = data[:, 5]
        else:
            signal = data

        signal = signal - np.mean(signal)

        if len(signal) > 5000:
            step = len(signal) // 5000
            signal = signal[::step]

        plt.figure(figsize=(10,4))
        plt.plot(signal)
        plt.title(f"{signal_type.upper()} Signal")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        await update.message.reply_photo(photo=buf)

    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()