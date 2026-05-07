import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- CONFIGURACIÓN DIRECTA ---
TOKEN = "8764531175:AAFk1mqWcQvQwnZyr5esK4J04zWhHROg_4g"

# Función para que los mensajes desaparezcan (se hagan polvito)
async def borrar_mensaje(context, chat_id, message_id, delay=5):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

# --- COMANDO START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Menú de tres rayitas (Teclado inferior)
    teclado_lateral = [['/start'], ['/quality']]
    markup_lateral = ReplyKeyboardMarkup(teclado_lateral, resize_keyboard=True)
    
    texto_bienvenida = (
        "✨ *Aurora Download Music* ✨\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👤 *Desarrollador:* Hammerskull\n\n"
        "¿Qué quieres hacer hoy?"
    )
    
    botones_principales = [
        [InlineKeyboardButton("🎵 Música", callback_data='menu_música'),
         InlineKeyboardButton("🎬 Vídeo", callback_data='menu_video')]
    ]
    
    await update.message.reply_text(texto_bienvenida, reply_markup=markup_lateral, parse_mode='Markdown')
    await update.message.reply_text("Selecciona una opción:", reply_markup=InlineKeyboardMarkup(botones_principales))

# --- MANEJO DE BOTONES (MENÚS) ---
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'menu_música':
        botones_calidad = [
            [InlineKeyboardButton("🎧 MP3", callback_data='form_mp3'),
             InlineKeyboardButton("📻 AAC", callback_data='form_aac')]
        ]
        await query.edit_message_text("Elige el formato de audio:", reply_markup=InlineKeyboardMarkup(botones_calidad))

    elif query.data == 'form_mp3':
        calidades = [
            [InlineKeyboardButton("128kbps", callback_data='q_128'),
             InlineKeyboardButton("192kbps", callback_data='q_192'),
             InlineKeyboardButton("320kbps", callback_data='q_320')]
        ]
        await query.edit_message_text("Calidad MP3:", reply_markup=InlineKeyboardMarkup(calidades))

    elif query.data == 'form_aac':
        calidades_aac = [
            [InlineKeyboardButton("192kbps", callback_data='q_192'),
             InlineKeyboardButton("256kbps", callback_data='q_256')]
        ]
        await query.edit_message_text("Calidad AAC:", reply_markup=InlineKeyboardMarkup(calidades_aac))

    elif query.data == 'menu_video':
        vids = [
            [InlineKeyboardButton("720p", callback_data='q_720'),
             InlineKeyboardButton("1080p", callback_data='q_1080')]
        ]
        await query.edit_message_text("Calidad de Video:", reply_markup=InlineKeyboardMarkup(vids))

    elif query.data.startswith('q_'):
        valor = query.data.replace('q_', '')
        msg = await query.edit_message_text(f"✅ Configurado a: {valor}")
        # Programar que el mensaje se borre solo
        asyncio.create_task(borrar_mensaje(context, query.message.chat_id, msg.message_id, 4))

# --- DETECCIÓN DE ENLACES Y BÚSQUEDA ---
async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_texto = update.message.text
    
    if "spotify.com" in msg_texto.lower():
        await update.message.reply_text("🎵 Enlace de Spotify detectado. Extrayendo información...")
    elif "youtube.com" in msg_texto.lower() or "youtu.be" in msg_texto.lower():
        await update.message.reply_text("🎬 Enlace de YouTube detectado. Preparando descarga...")
    else:
        await update.message.reply_text(f"🔎 Buscando '{msg_texto}'... (Mostrando 10 mejores opciones)")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(botones))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensaje))
    
    print("Aurora Bot iniciado correctamente...")
    application.run_polling()

if __name__ == '__main__':
    main()
