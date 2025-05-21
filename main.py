import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import sqlite3
from aiogram.dispatcher.filters import Command

API_TOKEN = '7560937841:AAHizOMSN94qemWXYknRwW73nWAP0Ynt4wM'  # আপনার bot টোকেন এখানে বসান
ADMIN_ID = 5767213888  # আপনার Telegram User ID

# Bot setup
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# --- DB Functions ---
def add_user(chat_id):
    conn = sqlite3.connect("thimbles/users.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY)")
    c.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()

def get_total_users():
    conn = sqlite3.connect("thimbles/users.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

# --- Start Command ---
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    add_user(message.chat.id)
    total = get_total_users()

    open_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("▶️ OPEN APP", url="https://1win-production.up.railway.app/")
    )

    await message.answer(
        f"<b>Welcome to Hack Bot!</b>\nTotal Users: <b>{total}</b>",
        reply_markup=open_button
    )

# --- Admin Command ---
@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ You are not authorized.")

    panel = InlineKeyboardMarkup(row_width=1)
    panel.add(
        InlineKeyboardButton("📤 Send Text", callback_data="send_text"),
        InlineKeyboardButton("🖼️ Send Photo", callback_data="send_photo"),
        InlineKeyboardButton("🎞️ Send Video", callback_data="send_video"),
        InlineKeyboardButton("📂 Send File", callback_data="send_file")
    )
    await message.answer("Welcome to Admin Panel:", reply_markup=panel)

# --- Handle Admin Actions ---
@dp.callback_query_handler(lambda c: c.data.startswith("send_"))
async def handle_send_options(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    await callback.message.answer(f"✅ Please send your {action} message now.\nYou can also add a link in caption.")

# --- Broadcast All Content ---
@dp.message_handler(lambda msg: msg.from_user.id == ADMIN_ID, content_types=types.ContentType.ANY)
async def broadcast_to_users(message: types.Message):
    conn = sqlite3.connect("thimbles/users.db")
    c = conn.cursor()
    c.execute("SELECT chat_id FROM users")
    users = c.fetchall()
    conn.close()

    count = 0
    for user in users:
        try:
            if message.text:
                await bot.send_message(user[0], message.text)
            elif message.photo:
                await bot.send_photo(user[0], message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                await bot.send_video(user[0], message.video.file_id, caption=message.caption)
            elif message.document:
                await bot.send_document(user[0], message.document.file_id, caption=message.caption)
            count += 1
        except Exception as e:
            pass  # Optional: log error

    await message.reply(f"✅ Broadcast sent to {count} users.")

# --- Run Bot ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
