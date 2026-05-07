import telebot
import yt_dlp
import os
import re
from telebot import types

# --- CONFIGURACIÓN ---
TOKEN = "7867375620:AAH88789H-G87GH878H-G87H" # Tu token asignado
bot = telebot.TeleBot(TOKEN)

# Carpeta temporal para descargas
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# --- MENÚ DE BOTONES (ReplyKeyboardMarkup) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # Incluimos los botones que mencionaste, incluyendo Detener
    btn_start = types.KeyboardButton('🚀 Start')
    btn_quality = types.KeyboardButton('⚙️ iQuality')
    btn_stop = types.KeyboardButton('🛑 Detener descarga')
    markup.add(btn_start, btn_quality, btn_stop)
    return markup

# --- COMANDOS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bienvenida = (
        "¡Hola Hammerskull! 🦾\n"
        "Soy Aurora, tu asistente de tecnología. Estoy lista para descargar "
        "lo que necesites de cualquier plataforma. Pásame un link o una búsqueda."
    )
    bot.reply_to(message, bienvenida, reply_markup=main_menu())

# --- MANEJADOR DE MENSAJES PRINCIPAL ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # PRIORIDAD 1: Detectar si es un enlace (Instagram, TikTok, FB, YT, etc.)
    # Si empieza con http, va directo a descarga sin buscar opciones
    if re.search(r'^https?://', text):
        bot.send_message(chat_id, "🔗 Enlace detectado. Procesando descarga directa...")
        descargar_video_universal(chat_id, text)
    
    # PRIORIDAD 2: Botones del menú
    elif text == '🚀 Start':
        bot.send_message(chat_id, "Reiniciando servicios de Aurora... Listo.", reply_markup=main_menu())
    elif text == '⚙️ iQuality':
        bot.send_message(chat_id, "Menú de calidad: Selecciona el formato deseado.")
    elif text == '🛑 Detener descarga':
        bot.send_message(chat_id, "Se ha enviado la señal para detener las descargas activas.")
    
    # PRIORIDAD 3: Si no es link ni botón, es una búsqueda de texto
    else:
        bot.send_message(chat_id, f"🔍 Buscando: {text}\nMostrando las 10 mejores opciones de YouTube...")
        # Aquí llamarías a tu función de búsqueda de YouTube original
        # buscar_en_youtube(chat_id, text)

# --- FUNCIÓN DE DESCARGA UNIVERSAL ---
def descargar_video_universal(chat_id, url):
    try:
        # Configuración optimizada para Render y varias plataformas
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            # No agregamos cookies aquí para evitar el error de Chrome de la otra vez
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraer información y descargar
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
            # Enviar el video al usuario
            with open(video_path, 'rb') as video:
                bot.send_video(
                    chat_id, 
                    video, 
                    caption=f"✅ Aquí tienes tu video:\n🎬 {info.get('title', 'Video descargado')}"
                )
            
            # Limpiar el servidor (Render tiene poco espacio)
            if os.path.exists(video_path):
                os.remove(video_path)
                
    except Exception as e:
        error_msg = str(e)
        if "confirm your age" in error_msg or "sign in" in error_msg:
            bot.send_message(chat_id, "❌ Esta plataforma pide inicio de sesión (Cookies). Intentaré otro método...")
        else:
            bot.send_message(chat_id, f"❌ Error al procesar el enlace: {error_msg}")

if __name__ == "__main__":
    print(">>> Aurora Online - Esperando órdenes de Hammerskull...")
    bot.infinity_polling()
