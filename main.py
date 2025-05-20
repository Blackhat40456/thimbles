import telebot
import time
import random
from telebot import types
import os

API_TOKEN = "7560937841:AAHizOMSN94qemWXYknRwW73nWAP0Ynt4wM"
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 5767213888  # Your Telegram ID

# Required channels
required_channels = {
    "@redhatJoinmain": "Join Channel 1 📡",
    "@redhatFreeHacks": "Join Channel 2 📡"
}

IMAGES = [
    "https://i.imgur.com/7uuILcO.jpeg",
    "https://i.imgur.com/iwDyPNq.jpeg",
    "https://i.imgur.com/ogjTLdZ.jpeg",
]

# Ensure files exist
for file_name in ["users.txt", "referrals.txt", "active_users.txt"]:
    if not os.path.exists(file_name):
        open(file_name, "w").close()

# ===== Helper Functions =====
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


def save_active_user(user_id):
    user_id = str(user_id)
    with open("active_users.txt", "a+") as f:
        f.seek(0)
        users = f.read().splitlines()
        if user_id not in users:
            f.write(user_id + "\n")


# ===== Handlers =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    save_active_user(user_id)
    args = message.text.split()

    # Save new user
    with open("users.txt", "a+") as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(str(user_id) + "\n")
            if len(args) > 1:
                inviter_id = args[1]
                if inviter_id != str(user_id):
                    add_referral(inviter_id, user_id)

    channel_status = has_joined_required_channels(user_id)

    if all(status == '✅' for status in channel_status.values()):
        referrals = get_user_referrals(user_id)
        if referrals >= 3:
            welcome_user(message)
        else:
            ask_for_referrals(message, referrals)
    else:
        ask_to_join_channels(message, channel_status)


def ask_to_join_channels(message, channel_status):
    markup = types.InlineKeyboardMarkup(row_width=2)
    channel_buttons = [
        types.InlineKeyboardButton(text=f"{status} {required_channels[channel]}", url=f"https://t.me/{channel[1:]}")
        for channel, status in channel_status.items()
    ]
    markup.add(*channel_buttons)
    markup.add(types.InlineKeyboardButton("✅ I've Joined", callback_data="check_channels"))

    bot.send_message(message.chat.id, "*You must join all channels first!*", reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == "check_channels")
def check_channels(call):
    user_id = call.from_user.id
    save_active_user(user_id)
    channel_status = has_joined_required_channels(user_id)

    if all(status == '✅' for status in channel_status.values()):
        referrals = get_user_referrals(user_id)
        if referrals >= 3:
            welcome_user(call.message)
        else:
            ask_for_referrals(call.message, referrals)
    else:
        bot.answer_callback_query(call.id, "❌ You still haven't joined all channels!")


def ask_for_referrals(message, count):
    save_active_user(message.from_user.id)
    invite_link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Share your invite link", url=invite_link))

    referral_message = (
        f"<b>You need 3 referrals to access the bot!</b>\n\n"
        f"<i>👥 Current referrals: {count}/3</i>\n"
        f"<i>🔗 Invite Link:</i>\n<a href='{invite_link}'>Click here to start</a>\n\n"
        "<i>👉 Share this link with your friends and ask them to click it to join. Once they join, you will get credit!</i>\n"
        "<i>To get credit, your friends must join the required channels.</i>"
    )

    bot.send_message(message.chat.id, referral_message, reply_markup=markup, parse_mode='HTML')
    bot.send_message(message.chat.id, "Forward this message to your friends!")


def welcome_user(message):
    save_active_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🌀 NEXT BALL POSITION"),
        types.KeyboardButton("🛑 STOP HACK"),
        types.KeyboardButton("🎲 NEW GAME"),
        types.KeyboardButton("🔄 Restart")
    )
    bot.send_message(message.chat.id, "*🎮 Welcome to the Game Menu! Choose an option:*", reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text in ["🌀 NEXT BALL POSITION", "🛑 STOP HACK", "🎲 NEW GAME", "🔄 Restart"])
def handle_game_buttons(message):
    save_active_user(message.from_user.id)

    if message.text == "🌀 NEXT BALL POSITION":
        bot.send_message(message.chat.id, "🔄 Calculating next ball position...")
        time.sleep(2)
        bot.send_photo(message.chat.id, random.choice(IMAGES), caption="✅ Next position ready!")

    elif message.text == "🛑 STOP HACK":
        bot.send_message(message.chat.id, "⚠️ Stopping the hack...")
        time.sleep(2)
        bot.send_message(message.chat.id, "✅ Hack stopped successfully!")

    elif message.text == "🎲 NEW GAME":
        bot.send_message(message.chat.id, "🆕 Starting a new game...")
        time.sleep(2)
        bot.send_message(message.chat.id, "✅ New game ready!")

    elif message.text == "🔄 Restart":
        start(message)


# ===== Admin Panel =====
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("📨 Send Text to Users"))
        bot.send_message(message.chat.id, "Welcome to the admin panel:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "📨 Send Text to Users" and m.from_user.id == ADMIN_ID)
def request_broadcast_text(message):
    bot.send_message(message.chat.id, "Please enter the message to send to all active users:")
    bot.register_next_step_handler(message, broadcast_message)


def broadcast_message(message):
    count = 0
    failed = 0
    try:
        with open("active_users.txt", "r") as f:
            users = f.read().splitlines()

        for user in users:
            try:
                bot.send_message(int(user), message.text, parse_mode='Markdown')
                count += 1
                time.sleep(0.3)
            except:
                failed += 1
                continue

        bot.send_message(message.chat.id, f"✅ Broadcast sent to {count} users, failed: {failed}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")


# ===== Global Tracker =====
@bot.message_handler(func=lambda message: True)
def track_all_messages(message):
    save_active_user(message.from_user.id)
    bot.reply_to(message, "Use /start or buttons to interact.")

# ===== Start Polling =====
bot.polling(none_stop=True)
