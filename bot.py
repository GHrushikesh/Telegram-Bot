import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8689052345:AAGeC4DFdfsZr91J5a5B0kMGXa2vctQowqA"   # 🔴 replace this

user_state = {}

# ===== START MENU =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to HG Tools Bot!\n\n"
        "1. 📊 PPT → PDF\n"
        "2. 📄 PDF → Word\n"
        "3. 🖼 Image → Text\n"
        "4. 📉 Compress PDF\n"
        "5. 🗜 Compress Image\n"
        "6. 🔄 WEBP → PNG/JPG"
    )

# ===== HANDLE OPTION =====
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    user_state[update.message.chat_id] = choice
    await update.message.reply_text("📂 Send your file")

# ===== HANDLE FILE =====
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        doc = update.message.document

        # 🔥 Telegram file size limit handling
        if doc.file_size > 20 * 1024 * 1024:  # 20MB safe limit
            await update.message.reply_text("❌ File too large (Max ~20MB)")
            return

        file = await doc.get_file()

        os.makedirs("downloads", exist_ok=True)
        file_path = f"downloads/{doc.file_name}"

        await file.download_to_drive(file_path)

        choice = user_state.get(update.message.chat_id)

        # ===== 1. PPT → PDF =====
        if choice == "1":
            await update.message.reply_text("⏳ Converting PPT to PDF...")

            soffice = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
            os.system(f'"{soffice}" --headless --convert-to pdf "{file_path}" --outdir downloads')

            output = file_path.rsplit(".", 1)[0] + ".pdf"

            if os.path.exists(output):
                await update.message.reply_document(open(output, "rb"))
            else:
                await update.message.reply_text("❌ Conversion failed!")

        # ===== 2. PDF → WORD =====
        elif choice == "2":
            await update.message.reply_text("⏳ Converting PDF to Word...")

            from pdf2docx import Converter

            output = file_path.replace(".pdf", ".docx")

            cv = Converter(file_path)
            cv.convert(output)
            cv.close()

            await update.message.reply_document(open(output, "rb"))

        # ===== 3. IMAGE → TEXT =====
        elif choice == "3":
            await update.message.reply_text("⏳ Extracting text...")

            from PIL import Image
            import pytesseract

            text = pytesseract.image_to_string(Image.open(file_path))

            await update.message.reply_text(text[:4000] if text else "❌ No text found")

        # ===== 4. COMPRESS PDF =====
        elif choice == "4":
            await update.message.reply_text("⏳ Compressing PDF...")

            output = "downloads/compressed.pdf"

            os.system(
                f'gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 '
                f'-dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH '
                f'-sOutputFile="{output}" "{file_path}"'
            )

            if os.path.exists(output):
                await update.message.reply_document(open(output, "rb"))
            else:
                await update.message.reply_text("❌ Compression failed!")

        # ===== 5. COMPRESS IMAGE =====
        elif choice == "5":
            await update.message.reply_text("⏳ Compressing image...")

            from PIL import Image

            img = Image.open(file_path)

            output = "downloads/compressed.jpg"
            img.convert("RGB").save(output, "JPEG", quality=40, optimize=True)

            await update.message.reply_document(open(output, "rb"))

        # ===== 6. WEBP → PNG/JPG =====
        elif choice == "6":
            await update.message.reply_text("⏳ Converting image...")

            from PIL import Image

            img = Image.open(file_path)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            output = "downloads/converted.png"
            img.save(output, "PNG")

            await update.message.reply_document(open(output, "rb"))

        else:
            await update.message.reply_text("❌ Use /start first")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ===== MAIN =====
def main():
    print("🤖 Bot Running...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    app.run_polling()

if __name__ == "__main__":
    main()