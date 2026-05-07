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

# --- MENÚS ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_start = types.KeyboardButton('🚀 Start')
    btn_stop = types.KeyboardButton('🛑 Detener descarga')
    markup.add(btn_start, btn_stop)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Aurora V5 Online! 🦾\nProtocolo de bypass activado. Pásame ese link rebelde.", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if re.search(r'https?://', message.text):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_alta = types.InlineKeyboardButton("🎬 Video Alta", callback_data="vid_alta")
        btn_audio = types.InlineKeyboardButton("🎵 Solo Audio", callback_data="audio")
        markup.add(btn_alta, btn_audio)
        bot.reply_to(message, "🔗 Link detectado. ¿Qué procedemos?", reply_markup=markup)
    elif message.text == '🚀 Start':
        bot.send_message(message.chat.id, "Sistemas listos.", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.edit_message_text("⚙️ Aplicando bypass de seguridad... Dame un momento.", call.message.chat.id, call.message.message_id)
    if call.message.reply_to_message:
        descargar_archivo(call.message.chat.id, call.message.reply_to_message.text, call.data)

# --- MOTOR DE DESCARGA V5 (EL "ROMPEMUROS") ---
def descargar_archivo(chat_id, url, formato):
    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'cookiefile': 'cookies.txt',
            # CAMBIO TÁCTICO: Usamos el cliente 'tv' que es el que menos pide Token PO
            'extractor_args': {
                'youtube': {
                    'player_client': ['tv', 'ios'],
                    'player_skip': ['web', 'web_music', 'android']
                }
            },
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_warnings': True
        }
        
        if formato == "vid_alta":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            ydl_opts['format'] = 'bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info: raise Exception("YouTube bloqueó la conexión.")
            
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as f:
                if formato == "audio":
                    bot.send_audio(chat_id, f, caption=f"✅ {info.get('title')}")
                else:
                    bot.send_video(chat_id, f, caption=f"✅ {info.get('title')}")
            
            if os.path.exists(file_path): os.remove(file_path)
                
    except Exception as e:
        bot.send_message(chat_id, f"❌ YouTube sigue bloqueando la IP de Render.\nError: {str(e)}")

if __name__ == "__main__":
    print(">>> Aurora V5 Online - Hammerskull, vamos por ese bypass.")
    bot.infinity_polling()
