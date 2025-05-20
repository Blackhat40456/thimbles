import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from config import BOT_TOKEN, OWNER_ID
from utils import is_admin, add_user, get_all_users

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Database setup
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY)""")
conn.commit()


# Start Command
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    add_user(message.chat.id)
    open_btn = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🟦 Open App", url="https://1win-production.up.railway.app/")
    )
    await message.answer(
        "<b>Welcome to the bot!</b>\nClick below to open the app.",
        reply_markup=open_btn
    )


# Stats Command (for Admin)
@dp.message_handler(commands=["stats"])
async def stats_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    total = len(get_all_users())
    await message.answer(f"Total users: <b>{total}</b>")


# Admin Command
@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Send Text", callback_data="send_text"),
        InlineKeyboardButton("Send Photo", callback_data="send_photo"),
        InlineKeyboardButton("Send Video", callback_data="send_video"),
        InlineKeyboardButton("Send File", callback_data="send_file"),
    )
    await message.answer("Admin Panel - Choose what to send:", reply_markup=keyboard)


# Admin Button Handler
@dp.callback_query_handler(lambda c: c.data.startswith("send_"))
async def process_send_buttons(callback: types.CallbackQuery):
    await callback.message.delete()
    action = callback.data.split("_")[1]
    await callback.message.answer(f"Send the {action} with format:\n<code>text/link</code>")


# Media Handler
@dp.message_handler(content_types=types.ContentType.ANY)
async def media_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    if message.caption and "/" in message.caption:
        text, url = message.caption.split("/", 1)
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔗 Visit Link", url=f"https://{url}")
        )
        users = get_all_users()
        for uid in users:
            try:
                await message.copy_to(uid, caption=text, reply_markup=markup)
            except:
                pass
        await message.reply("✅ Sent to all users!")


# Text with link
@dp.message_handler(lambda message: "/" in message.text)
async def send_text_link(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    text, url = message.text.split("/", 1)
    btn = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔗 Visit Link", url=f"https://{url}")
    )
    for user_id in get_all_users():
        try:
            await bot.send_message(user_id, text, reply_markup=btn)
        except:
            pass
    await message.reply("✅ Message sent to all users!")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
