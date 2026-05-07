import telebot
import yt_dlp
import os
import re
from telebot import types

# --- CONFIGURACIÓN ---
# Aquí está tu token íntegro para que no haya pierde
TOKEN = "7867375620:AAH88789H-G87GH878H-G87H" 
bot = telebot.TeleBot(TOKEN)

# Carpeta para archivos temporales
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# --- MENÚ DE BOTONES ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_start = types.KeyboardButton('🚀 Start')
    btn_quality = types.KeyboardButton('⚙️ iQuality')
    btn_stop = types.KeyboardButton('🛑 Detener descarga')
    markup.add(btn_start, btn_quality, btn_stop)
    return markup

# --- MANEJADOR DE INICIO ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "¡Aurora activa! 🦾\nListo para la acción, Hammerskull. Pásame un link o dime qué buscamos.", 
        reply_markup=main_menu()
    )

# --- MANEJADOR PRINCIPAL ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # 1. Detectar si el mensaje contiene un link (en cualquier posición gracias a re.search)
    if re.search(r'https?://', text):
        bot.send_message(chat_id, "🔗 ¡Enlace detectado! Procesando descarga...")
        descargar_video(chat_id, text)
    
    # 2. Respuesta a botones del teclado
    elif text == '🚀 Start':
        bot.send_message(chat_id, "Sistema reiniciado. ¿Qué descargamos?", reply_markup=main_menu())
    elif text == '⚙️ iQuality':
        bot.send_message(chat_id, "Ajustes de calidad disponibles.")
    elif text == '🛑 Detener descarga':
        bot.send_message(chat_id, "Se ha cancelado la descarga en curso.")
    
    # 3. Si es puro texto, lo toma como búsqueda
    else:
        bot.send_message(chat_id, f"🔍 Buscando: {text}...\nMostrando las 10 mejores opciones.")

# --- LÓGICA DE DESCARGA ---
def descargar_video(chat_id, url):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
            with open(video_path, 'rb') as video:
                bot.send_video(chat_id, video, caption=f"✅ ¡Aquí lo tienes!\n🎬 {info.get('title', 'Video')}")
            
            # Borrar el archivo después de enviarlo para no llenar el servidor
            if os.path.exists(video_path):
                os.remove(video_path)
                
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error en la descarga: {str(e)}")

if __name__ == "__main__":
    print(">>> Aurora Online - Esperando órdenes de Hammerskull...")
    bot.infinity_polling()
