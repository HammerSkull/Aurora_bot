import telebot
import yt_dlp
import os
import re
from telebot import types

# --- CONFIGURACIÓN ---
TOKEN = "8764531175:AAFk1mqWcQvQwnZyr5esK4J04zWhHROg_4g" 
bot = telebot.TeleBot(TOKEN)

if not os.path.exists('downloads'):
    os.makedirs('downloads')

# --- MENÚS (SIN MODIFICACIONES) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_start = types.KeyboardButton('🚀 Start')
    btn_stop = types.KeyboardButton('🛑 Detener descarga')
    markup.add(btn_start, btn_stop)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Aurora V6 Online! 🦾\nBlindaje de navegador activado. El último recurso contra YouTube.", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if re.search(r'https?://', message.text):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_alta = types.InlineKeyboardButton("🎬 Video Alta", callback_data="vid_alta")
        btn_audio = types.InlineKeyboardButton("🎵 Solo Audio", callback_data="audio")
        markup.add(btn_alta, btn_audio)
        bot.reply_to(message, "🔗 Radar activo. ¿Formato de salida?", reply_markup=markup)
    elif message.text == '🚀 Start':
        bot.send_message(message.chat.id, "Sistemas listos.", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.edit_message_text("⚙️ Aplicando camuflaje de navegador... Extrayendo.", call.message.chat.id, call.message.message_id)
    if call.message.reply_to_message:
        descargar_archivo(call.message.chat.id, call.message.reply_to_message.text, call.data)

# --- MOTOR V6: CAMUFLAJE DE NAVEGADOR ---
def descargar_archivo(chat_id, url, formato):
    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'cookiefile': 'cookies.txt',
            # NUEVO ARMAMENTO: Imitación de Navegador Chrome Real
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'nocheckcertificate': True,
        }
        
        if formato == "vid_alta":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            ydl_opts['format'] = 'bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            with open(file_path, 'rb') as f:
                if formato == "audio":
                    bot.send_audio(chat_id, f, caption=f"✅ {info.get('title')}")
                else:
                    bot.send_video(chat_id, f, caption=f"✅ {info.get('title')}")
            
            if os.path.exists(file_path): os.remove(file_path)
                
    except Exception as e:
        bot.send_message(chat_id, f"❌ YouTube ha bloqueado este servidor de Render temporalmente.\nIntenta con otro link o espera 10 min.")

if __name__ == "__main__":
    bot.infinity_polling()
