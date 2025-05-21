from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

API_TOKEN = '7560937841:AAHizOMSN94qemWXYknRwW73nWAP0Ynt4wM'  # এখানে আপনার Bot Token দিন

bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# States
class Form(StatesGroup):
    waiting_for_input = State()

# Start command
@dp.message_handler(commands='start')
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="🖥️ CONNECT YOUR SERVER", callback_data="connect_server"),
        InlineKeyboardButton(text="▶️ START", callback_data="start_game"),
        InlineKeyboardButton(text="⏭️ NEXT", callback_data="next_image"),
    )
    await message.answer("<b>Welcome to Thimbles Hack Bot 🕵️</b>\nChoose an option below:", reply_markup=keyboard)

# Callback handler
@dp.callback_query_handler(lambda c: c.data == "connect_server")
async def connect_server_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "<b>🔐 Please enter your Player ID (9-10 digits only):</b>")
    await Form.waiting_for_input.set()

@dp.message_handler(state=Form.waiting_for_input)
async def handle_player_id(message: types.Message, state: FSMContext):
    player_id = message.text.strip()
    if not player_id.isdigit() or len(player_id) not in (9, 10):
        await message.answer("<b>❌ Invalid ID. Please enter a 9 or 10 digit number.</b>")
        return
    await state.finish()
    await message.answer("<b>✅ Server connected successfully!</b>\nWelcome to Login Activity.\nEnter your login key:")

# Dummy button actions
@dp.callback_query_handler(lambda c: c.data == "start_game")
async def start_game_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "<b>⏳ Loading... Please wait</b>")
    await bot.send_message(callback_query.from_user.id, "<b>✅ Game started! Enjoy!</b>")

@dp.callback_query_handler(lambda c: c.data == "next_image")
async def next_image_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "<b>⏳ Loading next image...</b>")
    # send photo/sticker if needed

# Run the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
