import os
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

TOKEN = os.environ.get("TOKEN")

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["signal_type"] = query.data
    await query.edit_message_text("TXT fayl yuboring.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "signal_type" not in context.user_data:
        await update.message.reply_text("Avval /start bosing.")
        return

    file = await update.message.document.get_file()
    file_bytes = await file.download_as_bytearray()

    try:
        data = np.loadtxt(io.BytesIO(file_bytes))

        if len(data.shape) > 1:
            if context.user_data["signal_type"] == "ecg":
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
        plt.title("Signal")

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        await update.message.reply_photo(photo=buf)

    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.run_polling()

if __name__ == "__main__":
    main()
