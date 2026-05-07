import telebot
import yt_dlp
import os
import re
from telebot import types

# --- CONFIGURACIÓN MAESTRA ---
TOKEN = "8764531175:AAFk1mqWcQvQwnZyr5esK4J04zWhHROg_4g" 
bot = telebot.TeleBot(TOKEN)

# Carpeta para archivos temporales
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# --- COMANDO START ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "¡Sistemas reiniciados y al 100%! 🦾\nSoy Aurora. Pásame cualquier enlace (YouTube, Instagram, TikTok) y te desplegaré el panel de descargas, Hammerskull."
    )

# --- DETECCIÓN DE ENLACES Y MENÚ DESPLEGABLE ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.strip()

    if re.search(r'https?://', text):
        # Creamos los botones interactivos
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_alta = types.InlineKeyboardButton("🎬 Video (Alta Calidad)", callback_data="vid_alta")
        btn_baja = types.InlineKeyboardButton("📱 Video (Calidad Estándar/Ligero)", callback_data="vid_baja")
        btn_audio = types.InlineKeyboardButton("🎵 Solo Audio (Música)", callback_data="audio")
        markup.add(btn_alta, btn_baja, btn_audio)
        
        # Respondemos al mensaje original (esto es vital para que yo no pierda el link de vista)
        bot.reply_to(message, "🔗 ¡Enlace asegurado! ¿En qué formato lo procesamos?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"🔍 Me pides buscar: '{text}'\n(Sigo calibrando los motores de búsqueda directa, por favor envíame el enlace por ahora).")

# --- MANEJADOR DE LOS BOTONES (AQUÍ ES DONDE DESAPARECEN) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    formato = call.data
    
    # 1. Editamos el mensaje para borrar los botones y avisar que estamos trabajando
    bot.edit_message_text("⚙️ Comprendido. Descargando y procesando tu selección...", chat_id, message_id)
    
    # 2. Recuperamos el enlace desde el mensaje que tú enviaste originalmente
    if call.message.reply_to_message and call.message.reply_to_message.text:
        url = call.message.reply_to_message.text
        descargar_archivo(chat_id, url, formato)
    else:
        bot.send_message(chat_id, "❌ Error: No logré rastrear el enlace original en la base de datos.")

# --- MOTOR DE DESCARGA AVANZADO CON COOKIES ---
def descargar_archivo(chat_id, url, formato):
    try:
        # Configuraciones base y la LLAVE MAESTRA
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'cookiefile': 'cookies.txt',  # <-- LA EXTENSIÓN QUE GUARDASTE EN FIREFOX
        }
        
        # Ajustamos el motor según el botón que presionaste
        if formato == "vid_alta":
            ydl_opts['format'] = 'best'
        elif formato == "vid_baja":
            ydl_opts['format'] = 'worst'
        elif formato == "audio":
            ydl_opts['format'] = 'm4a/bestaudio/best' # Extrae el mejor formato de audio nativo

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Enviamos el archivo terminado
            with open(file_path, 'rb') as file:
                if formato == "audio":
                    bot.send_audio(chat_id, file, caption=f"✅ Operación exitosa:\n🎵 {info.get('title', 'Audio')}")
                else:
                    bot.send_video(chat_id, file, caption=f"✅ Operación exitosa:\n🎬 {info.get('title', 'Video')}")
            
            # Limpieza inmediata de los servidores de Render
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        bot.send_message(chat_id, f"❌ Rayos, hubo una falla en la extracción: {str(e)}")

if __name__ == "__main__":
    print(">>> Aurora Online - Panel táctico interactivo cargado...")
    bot.infinity_polling()
