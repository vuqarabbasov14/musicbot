import os
import hashlib
import asyncio
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
CREATOR_NAME = os.getenv('CREATOR_NAME', 'Unknown')
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
def get_cache_filename(query):
    hash_name = hashlib.md5(query.lower().encode('utf-8')).hexdigest()
    return f'downloads/{hash_name}.mp3'
async def download_song(query: str):
    os.makedirs('downloads', exist_ok=True)
    cached_file = get_cache_filename(query)
    if os.path.exists(cached_file):
        return cached_file, query  # Cache varsa dərhal qaytar
    loop = asyncio.get_event_loop()
    def run_ydl():
        opts = ydl_opts.copy()
        opts['outtmpl'] = cached_file.replace('.mp3', '.%(ext)s')
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            title = info['entries'][0]['title']
            return cached_file, title
    result = await loop.run_in_executor(None, run_ydl)
    return result
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"Salam! Mən musiqi botuyam 🎵\n\n"
        "Mahnı axtarmaq üçün /song <mahnı adı> yaz.\n"
        "Məsələn: /song Imagine Dragons Believer\n\n"
        f"Bot yaradılıb: {CREATOR_NAME}"
    )
    await update.message.reply_text(welcome_text)
async def song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Zəhmət olmasa, mahnı adını yaz. Məsələn: /song Imagine Dragons Believer")
        return
    query = ' '.join(context.args)
    msg = await update.message.reply_text(f"'{query}' mahnısı axtarılır və yüklənir... ⏳")
    try:
        mp3_path, title = await download_song(query)
        await update.message.reply_audio(audio=open(mp3_path, 'rb'), title=title)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"Xəta baş verdi: {e}")
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bağışla, bu əmri başa düşmədim.")
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('song', song_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    print("Bot işləyir...")
    app.run_polling()
