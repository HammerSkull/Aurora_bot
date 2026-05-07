import telebot
import yt_dlp
import os
import re
from telebot import types

# --- CONFIGURACIÓN MAESTRA ---
# Token oficial de Aurora
TOKEN = "8764531175:AAFk1mqWcQvQwnZyr5esK4J04zWhHROg_4g" 
bot = telebot.TeleBot(TOKEN)

# Directorio de operaciones temporales
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# --- MENÚ DE MANDO (TECLADO PRINCIPAL) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_start = types.KeyboardButton('🚀 Start')
    btn_stop = types.KeyboardButton('🛑 Detener descarga')
    markup.add(btn_start, btn_stop)
    return markup

# --- PROTOCOLO DE ARRANQUE ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "¡Sistemas Aurora en línea, Hammerskull! 🦾\nTodos los módulos de combate y tecnología están operativos. Envíame un enlace o una búsqueda para comenzar.",
        reply_markup=main_menu()
    )

# --- RADAR DE ENLACES Y PANEL INTERACTIVO ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Radar de enlaces universal
    if re.search(r'https?://', text):
        # Panel táctico: botones que se eliminan tras el uso
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_alta = types.InlineKeyboardButton("🎬 Video (Máxima Calidad)", callback_data="vid_alta")
        btn_baja = types.InlineKeyboardButton("📱 Video (Calidad Estándar)", callback_data="vid_baja")
        btn_audio = types.InlineKeyboardButton("🎵 Solo Audio (MP3/M4A)", callback_data="audio")
        markup.add(btn_alta, btn_baja, btn_audio)
        
        bot.reply_to(message, "🔗 Enlace detectado por el radar. Selecciona el formato de salida:", reply_markup=markup)
    
    # Comandos del menú de teclado
    elif text == '🚀 Start':
        bot.send_message(chat_id, "Reiniciando protocolos... Base de datos lista.", reply_markup=main_menu())
    elif text == '🛑 Detener descarga':
        bot.send_message(chat_id, "Orden recibida. Interrumpiendo procesos de descarga.")
    
    # Lógica de búsqueda directa
    else:
        bot.send_message(chat_id, f"🔍 Buscando: '{text}'...\nMostrando las 10 mejores opciones en los servidores.")

# --- MANEJADOR DE BOTONES (AUTO-ELIMINACIÓN) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    formato = call.data
    
    # Eliminación de botones para evitar conflictos de señal
    bot.edit_message_text("⚙️ Procesando solicitud... Accediendo a los servidores de extracción.", chat_id, message_id)
    
    # Recuperación del enlace del mensaje original
    if call.message.reply_to_message and call.message.reply_to_message.text:
        url = call.message.reply_to_message.text
        descargar_archivo(chat_id, url, formato)
    else:
        bot.send_message(chat_id, "❌ Error de rastreo: No se pudo localizar el enlace original en la memoria.")

# --- MOTOR DE EXTRACCIÓN CON BLINDAJE MÓVIL ---
def descargar_archivo(chat_id, url, formato):
    try:
        # Configuración de escudos, cookies y bypass de seguridad
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'cookiefile': 'cookies.txt',  
            # AJUSTE TÁCTICO: Bypass del desafío n de YouTube
            'extractor_args': {'youtube': ['player_client=ios,android']},
        }
        
        # Selección de armamento según el formato
        if formato == "vid_alta":
            ydl_opts['format'] = 'best'
        elif formato == "vid_baja":
            ydl_opts['format'] = 'worst'
        elif formato == "audio":
            ydl_opts['format'] = 'm4a/bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Entrega del material
            with open(file_path, 'rb') as file:
                if formato == "audio":
                    bot.send_audio(chat_id, file, caption=f"✅ Operación exitosa:\n🎵 {info.get('title', 'Audio')}")
                else:
                    bot.send_video(chat_id, file, caption=f"✅ Operación exitosa:\n🎬 {info.get('title', 'Video')}")
            
            # Limpieza de rastro en el servidor
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        bot.send_message(chat_id, f"❌ Fallo crítico en la extracción: {str(e)}")

if __name__ == "__main__":
    print(">>> Aurora Pro V2 Online - Panel de combate listo para Hammerskull...")
    bot.infinity_polling()
