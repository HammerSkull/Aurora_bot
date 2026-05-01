import asyncio
import logging
import yt_dlp
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURACIÓN ---
TOKEN = "8764531175:AAFk1mqWcQvQwnZyr5esK4J04zWhHROg_4g"
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Carpeta de descargas
DOWNLOAD_PATH = './downloads'
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "✨ *Aurora Music* ✨\n\n¿Qué descargamos hoy, Hammerskull?\n\nDesarrollador: *Hammerskull*"
    keyboard = [[InlineKeyboardButton("🎵 Música", callback_data='music'), 
                 InlineKeyboardButton("🎬 Video", callback_data='video')]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'music':
        keyboard = [
            [InlineKeyboardButton("🎶 MP3 128", callback_data='fmt_mp3_128'), 
             InlineKeyboardButton("🎶 AAC 192", callback_data='fmt_aac_192')],
            [InlineKeyboardButton("🎶 MP3 192", callback_data='fmt_mp3_192'), 
             InlineKeyboardButton("🎶 AAC 256 (💎 TOP)", callback_data='fmt_aac_256')],
            [InlineKeyboardButton("🎶 MP3 320", callback_data='fmt_mp3_320')]
        ]
        await query.edit_message_text("🎧 *Selecciona Calidad de Audio:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == 'video':
        keyboard = [[InlineKeyboardButton("🎥 MP4 - 720p", callback_data='fmt_vid_720')],
                    [InlineKeyboardButton("🌟 MP4 - 1080p", callback_data='fmt_vid_1080')]]
        await query.edit_message_text("📺 *Selecciona Resolución:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data.startswith('fmt_'):
        _, tipo, calidad = query.data.split('_')
        context.user_data['tipo'] = tipo
        context.user_data['calidad'] = calidad
        await query.edit_message_text(f"✅ *Configurado:* {tipo.upper()} | {calidad}\n\nEscribe el nombre de la rola o pega el link:")

    elif query.data.startswith('dl_'):
        video_id = query.data.split('_')[1]
        tipo = context.user_data.get('tipo', 'mp3')
        calidad = context.user_data.get('calidad', '320')
        
        await query.message.delete()
        proceso_msg = await context.bot.send_message(chat_id=query.message.chat_id, text="🚀 *Aurora Juggernaut: Procesando descarga...*")

        file_base = os.path.join(DOWNLOAD_PATH, f"{video_id}")
        extension = 'mp4' if tipo == 'vid' else tipo
        file_final = f"{file_base}.{extension}"
        
        ydl_opts = {
            'format': 'bestaudio/best' if tipo != 'vid' else 'bestvideo+bestaudio/best',
            'outtmpl': file_base,
            'writethumbnail': True,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': tipo, 'preferredquality': calidad} if tipo != 'vid' else {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata', 'add_metadata': True}
            ],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                url_yt = f"https://www.youtube.com/watch?v={video_id}"
                info = await asyncio.to_thread(ydl.extract_info, url_yt, download=True)
                titulo = info.get('title', 'Audio')
                artista = info.get('uploader', 'Aurora')

            if os.path.exists(file_final):
                await proceso_msg.edit_text(f"📤 *Enviando: {titulo}...*")
                with open(file_final, 'rb') as f:
                    if tipo == 'vid':
                        await context.bot.send_video(chat_id=query.message.chat_id, video=f, caption=f"🎥 {titulo}")
                    else:
                        await context.bot.send_audio(
                            chat_id=query.message.chat_id,
                            audio=f,
                            caption=f"✨ *Aurora Music*\n🎵 {titulo}\n👤 {artista}\n💎 {calidad}kbps",
                            title=titulo,
                            performer=artista
                        )
                await proceso_msg.delete()
                os.remove(file_final)
            else:
                await proceso_msg.edit_text("❌ Error: El archivo no se generó.")
            
        except Exception as e:
            await proceso_msg.edit_text(f"❌ Error en la descarga. Revisa el log de Render.")
            print(f"ERROR: {e}")

async def search_and_suggest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    status_msg = await update.message.reply_text(f"🔍 Buscando en YouTube: *{user_input}*...")

    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'extract_flat': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Búsqueda de tus 10 resultados
            info = await asyncio.to_thread(ydl.extract_info, f"ytsearch10:{user_input}", download=False)
            if 'entries' in info:
                keyboard = []
                for entry in info['entries']:
                    title = (entry.get('title')[:45] + '..') if len(entry.get('title')) > 45 else entry.get('title')
                    keyboard.append([InlineKeyboardButton(f"📥 {title}", callback_data=f"dl_{entry.get('id')}")])
                
                await status_msg.delete()
                await update.message.reply_text(f"Resultados para: *{user_input}*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    except Exception:
        await status_msg.edit_text("❌ No encontré resultados.")

def main():
    # SIN PROXY - CONEXIÓN DIRECTA EN RENDER
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_and_suggest))
    
    print("Aurora Juggernaut activa y patrullando...")
    application.run_polling()

if __name__ == '__main__':
    main()