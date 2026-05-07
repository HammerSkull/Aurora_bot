import telebot
import yt_dlp
import os
import re
from telebot import types

# --- CONFIGURACIÓN MAESTRA ---
# Tu token oficial autorizado por BotFather
TOKEN = "8764531175:AAFk1mqWcQvQwnZyr5esK4J04zWhHROg_4g" 
bot = telebot.TeleBot(TOKEN)

# Carpeta de operaciones temporales
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# --- MENÚ DE MANDO (TECLADO PRINCIPAL) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_start = types.KeyboardButton('🚀 Start')
    btn_stop = types.KeyboardButton('🛑 Detener descarga')
    markup.add(btn_start, btn_stop)
    return markup

# --- COMANDO DE ARRANQUE ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "¡Sistemas Aurora en línea, Hammerskull! 🦾\nPanel de control activado. Envíame un enlace de cualquier plataforma para iniciar la extracción.",
        reply_markup=main_menu()
    )

# --- DETECCIÓN DE ENLACES Y PANEL INTERACTIVO ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Si detectamos un link en cualquier parte del texto
    if re.search(r'https?://', text):
        # Creamos los botones que desaparecerán después de usarse
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_alta = types.InlineKeyboardButton("🎬 Video (Máxima Calidad)", callback_data="vid_alta")
        btn_baja = types.InlineKeyboardButton("📱 Video (Calidad Estándar)", callback_data="vid_baja")
        btn_audio = types.InlineKeyboardButton("🎵 Solo Audio (MP3/M4A)", callback_data="audio")
        markup.add(btn_alta, btn_baja, btn_audio)
        
        bot.reply_to(message, "🔗 Enlace detectado. Selecciona el formato de salida:", reply_markup=markup)
    
    # Comandos de texto del menú principal
    elif text == '🚀 Start':
        bot.send_message(chat_id, "Reiniciando protocolos de Aurora... Listo.", reply_markup=main_menu())
    elif text == '🛑 Detener descarga':
        bot.send_message(chat_id, "Se ha enviado la señal de interrupción.")
    else:
        bot.send_message(chat_id, f"🔍 Buscando: '{text}'... (Dame el link directo para procesarlo ahora mismo).")

# --- MANEJADOR DE BOTONES INTERACTIVOS (DESAPARECEN AL TOCARLOS) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    formato = call.data
    
    # Editamos el mensaje para quitar los botones y evitar clics dobles
    bot.edit_message_text("⚙️ Procesando solicitud... Conectando con los servidores de descarga.", chat_id, message_id)
    
    # Extraemos el link del mensaje al que respondimos
    if call.message.reply_to_message and call.message.reply_to_message.text:
        url = call.message.reply_to_message.text
        descargar_archivo(chat_id, url, formato)
    else:
        bot.send_message(chat_id, "❌ Error táctico: No pude recuperar el enlace original.")

# --- MOTOR DE EXTRACCIÓN CON ESCUDOS MÓVILES ---
def descargar_archivo(chat_id, url, formato):
    try:
        # Configuración de los escudos y cookies
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'cookiefile': 'cookies.txt',  # Tu llave de Firefox
            # ESTA LÍNEA ES EL ESCUDO CONTRA EL PO TOKEN DE YOUTUBE:
            'extractor_args': {'youtube': ['client=android,ios']},
        }
        
        # Selección de armamento según el botón presionado
        if formato == "vid_alta":
            ydl_opts['format'] = 'best'
        elif formato == "vid_baja":
            ydl_opts['format'] = 'worst'
        elif formato == "audio":
            ydl_opts['format'] = 'm4a/bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Envío del material extraído
            with open(file_path, 'rb') as file:
                if formato == "audio":
                    bot.send_audio(chat_id, file, caption=f"✅ Extracción exitosa:\n🎵 {info.get('title', 'Audio')}")
                else:
                    bot.send_video(chat_id, file, caption=f"✅ Extracción exitosa:\n🎬 {info.get('title', 'Video')}")
            
            # Borrado para no saturar Render
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        bot.send_message(chat_id, f"❌ Fallo en la extracción: {str(e)}\n(Asegúrate de que tu cookies.txt esté actualizado).")

if __name__ == "__main__":
    print(">>> Aurora Pro Online - Esperando órdenes de Hammerskull...")
    bot.infinity_polling()
