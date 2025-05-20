import telebot
import time
import random
from telebot import types
import os

API_TOKEN = "7560937841:AAHizOMSN94qemWXYknRwW73nWAP0Ynt4wM"  # Replace with your actual token
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 5767213888  # Your Telegram ID

# Required Channels
required_channels = {
    "@redhatJoinmain": "Join Channel 1 📡",
    "@redhatFreeHacks": "Join Channel 2 📡"
}

IMAGES = [
    "https://i.imgur.com/7uuILcO.jpeg",
    "https://i.imgur.com/iwDyPNq.jpeg",
    "https://i.imgur.com/ogjTLdZ.jpeg"
]

# Ensure files exist
for filename in ["users.txt", "referrals.txt"]:
    if not os.path.exists(filename):
        open(filename, "w").close()

def has_joined_required_channels(user_id):
    status_dict = {}
    for channel in required_channels.keys():
        try:
            member_status = bot.get_chat_member(channel, user_id)
            if member_status.status in ['left', 'kicked']:
                status_dict[channel] = '❌'
            else:
                status_dict[channel] = '✅'
        except:
            status_dict[channel] = '❌'
    return status_dict

def get_user_referrals(user_id):
    with open("referrals.txt", "r") as f:
        lines = f.read().splitlines()
    referrals = [line.split(":")[1] for line in lines if line.split(":")[0] == str(user_id)]
    return len(referrals)

def add_referral(inviter_id, new_user_id):
    with open("referrals.txt", "a") as f:
        f.write(f"{inviter_id}:{new_user_id}\n")

def update_bot_name():
    with open("users.txt", "r") as f:
        user_count = len(f.read().splitlines())
    try:
        bot.set_my_name(f"Game Bot 🎮 | {user_count} Users")
    except:
        pass

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    with open("users.txt", "a+") as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(str(user_id) + "\n")
            if len(args) > 1:
                inviter_id = args[1]
                if inviter_id != str(user_id):
                    add_referral(inviter_id, user_id)
            update_bot_name()

    status = has_joined_required_channels(user_id)
    if all(v == '✅' for v in status.values()):
        referrals = get_user_referrals(user_id)
        if referrals >= 3:
            welcome_user(message)
        else:
            ask_for_referrals(message, referrals)
    else:
        ask_to_join_channels(message, status)

def ask_to_join_channels(message, status):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for ch, stat in status.items():
        markup.add(types.InlineKeyboardButton(f"{stat} {required_channels[ch]}", url=f"https://t.me/{ch[1:]}"))
    markup.add(types.InlineKeyboardButton("✅ I've Joined", callback_data="check_channels"))
    bot.send_message(message.chat.id, "*You must join all channels first!*", reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "check_channels")
def check_channels(call):
    user_id = call.from_user.id
    status = has_joined_required_channels(user_id)
    if all(v == '✅' for v in status.values()):
        referrals = get_user_referrals(user_id)
        if referrals >= 3:
            welcome_user(call.message)
        else:
            ask_for_referrals(call.message, referrals)
    else:
        bot.answer_callback_query(call.id, "❌ You still haven't joined all channels!")

def ask_for_referrals(message, count):
    invite_link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Share your invite link", url=invite_link))
    text = (
        f"<b>You need 3 referrals to access the bot!</b>\n\n"
        f"<i>👥 Current referrals: {count}/3</i>\n"
        f"<i>🔗 Invite Link:</i>\n<a href='{invite_link}'>Click here to Start 👈</a>\n\n"
        "<i>👉 Share this link with friends. They must join required channels to count.</i>"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

def welcome_user(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🌀 NEXT BALL POSITION", "🛑 STOP HACK")
    markup.add("🎲 NEW GAME", "🔄 Restart")
    bot.send_message(message.chat.id, "*🎮 Welcome to the Game Menu! Choose an option:*", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🌀 NEXT BALL POSITION")
def next_ball_position(message):
    bot.send_message(message.chat.id, "🔄 Calculating next ball position...", parse_mode='Markdown')
    time.sleep(2)
    random_image = random.choice(IMAGES)
    bot.send_photo(message.chat.id, random_image, caption="✅ Next position ready!")

@bot.message_handler(func=lambda message: message.text == "🛑 STOP HACK")
def stop_hack(message):
    bot.send_message(message.chat.id, "⚠️ Stopping the hack...", parse_mode='Markdown')
    time.sleep(2)
    bot.send_message(message.chat.id, "✅ Hack stopped successfully!", parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🎲 NEW GAME")
def new_game(message):
    bot.send_message(message.chat.id, "🆕 Starting a new game...", parse_mode='Markdown')
    time.sleep(2)
    bot.send_message(message.chat.id, "✅ New game ready!", parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🔄 Restart")
def restart_bot(message):
    start(message)

# ADMIN PANEL
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📨 Send Text", "📷 Send Image", "🎥 Send Video")
        markup.add("📁 Send File", "📬 Send Post", "🌐 Open Site Button")
        bot.send_message(message.chat.id, "Welcome to the admin panel:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "📨 Send Text")
def ask_text_broadcast(message):
    bot.send_message(message.chat.id, "Send the text you want to broadcast:")
    bot.register_next_step_handler(message, broadcast_message)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "📷 Send Image")
def ask_photo(message):
    bot.send_message(message.chat.id, "Send image with caption:")
    bot.register_next_step_handler(message, broadcast_photo)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "🎥 Send Video")
def ask_video(message):
    bot.send_message(message.chat.id, "Send video with caption:")
    bot.register_next_step_handler(message, broadcast_video)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "📁 Send File")
def ask_file(message):
    bot.send_message(message.chat.id, "Send file/document with caption:")
    bot.register_next_step_handler(message, broadcast_file)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "📬 Send Post")
def ask_post(message):
    bot.send_message(message.chat.id, "Send any post (message/photo/video/etc):")
    bot.register_next_step_handler(message, broadcast_post)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "🌐 Open Site Button")
def send_open_button(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌐 OPEN", url="https://your-website.com"))
    bot.send_message(message.chat.id, "This is the open button:", reply_markup=markup)

def broadcast_message(message):
    count = 0
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    for user in users:
        try:
            bot.send_message(int(user), message.text, parse_mode='HTML')
            count += 1
            time.sleep(0.1)
        except:
            continue
    bot.send_message(message.chat.id, f"✅ Sent to {count} users.")

def broadcast_photo(message):
    if message.photo:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
        for user in users:
            try:
                bot.send_photo(int(user), message.photo[-1].file_id, caption=message.caption or "")
            except:
                continue

def broadcast_video(message):
    if message.video:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
        for user in users:
            try:
                bot.send_video(int(user), message.video.file_id, caption=message.caption or "")
            except:
                continue

def broadcast_file(message):
    if message.document:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
        for user in users:
            try:
                bot.send_document(int(user), message.document.file_id, caption=message.caption or "")
            except:
                continue

def broadcast_post(message):
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    for user in users:
        try:
            bot.copy_message(int(user), from_chat_id=message.chat.id, message_id=message.message_id)
        except:
            continue

bot.polling(none_stop=True)
