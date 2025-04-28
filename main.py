import telebot
import time
import random
from telebot import types
import os

API_TOKEN = "7753611465:AAHGF6-DlfuX-vFi28MYjxbq-PVJoJeHKJ0"
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 5767213888  # Update with your Telegram ID

# Required channels
required_channels = {
    "@redhatJoinmain": "Join Channel 1 📡",
    "@MinesvipsignalsbyReDHaT": "Join Channel 2 📡"
}

IMAGES = [
    "https://i.imgur.com/bNxGPlT.jpeg",
    "https://i.imgur.com/CakfQiB.jpeg",
    "https://i.imgur.com/Yo2y6k9.jpeg",
]

# Ensure file existence
if not os.path.exists("users.txt"):
    open("users.txt", "w").close()

if not os.path.exists("referrals.txt"):
    open("referrals.txt", "w").close()

# Helper Functions
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


# Handlers
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    # Save user if new
    with open("users.txt", "a+") as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(str(user_id) + "\n")
            # Handle referral
            if len(args) > 1:
                inviter_id = args[1]
                if inviter_id != str(user_id):
                    add_referral(inviter_id, user_id)

    channel_status = has_joined_required_channels(user_id)

    if all(status == '✅' for status in channel_status.values()):
        referrals = get_user_referrals(user_id)
        if referrals >= 10:
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

    text = "*You must join all channels first!*"
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == "check_channels")
def check_channels(call):
    user_id = call.from_user.id
    channel_status = has_joined_required_channels(user_id)

    if all(status == '✅' for status in channel_status.values()):
        referrals = get_user_referrals(user_id)
        if referrals >= 10:
            welcome_user(call.message)
        else:
            ask_for_referrals(call.message, referrals)
    else:
        bot.answer_callback_query(call.id, "❌ You still haven't joined all channels!")


def ask_for_referrals(message, count):
    markup = types.InlineKeyboardMarkup()
    invite_link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    markup.add(types.InlineKeyboardButton("📢 Share your invite link", url=invite_link))

    referral_message = (
        f"<b>You need 10 referrals to access the bot!</b>\n\n"
        f"<i>👥 Current referrals: {count}/10</i>\n"
        f"<i>🔗 Invite Link:</i>\n<a href='{invite_link}'>Clicck here to Start👈</a>\n\n"
        "<i>👉 Share this link with your friends and ask them to click it to join. Once they join, you will get credit!</i>\n\n"
        "<i>To get credit for your referral, your friends must join the required channels.</i>"
    )

    # Send the referral message with the invite link
    bot.send_message(
        message.chat.id,
        referral_message,
        reply_markup=markup,
        parse_mode='HTML'  # Switch to HTML parsing
    )

    # Tell the user how to forward the link
    bot.send_message(
        message.chat.id,
        "You can forward the☝️ message with your invite link to your friends! Make sure they click on the link to join."
    )


def welcome_user(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🌀 NEXT BALL POSITION")
    btn2 = types.KeyboardButton("🛑 STOP HACK")
    btn3 = types.KeyboardButton("🎲 NEW GAME")
    restart_btn = types.KeyboardButton("🔄 Restart")
    markup.add(btn1, btn2, btn3, restart_btn)

    bot.send_message(message.chat.id, "*🎮 Welcome to the Game Menu! Choose an option:*", reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "🌀 NEXT BALL POSITION")
def next_ball_position(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "🔄 Calculating next ball position...", parse_mode='Markdown')
    time.sleep(2)
    random_image = random.choice(IMAGES)
    bot.send_photo(user_id, random_image, caption="✅ Next position ready!")


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


# Admin Panel (Optional)
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        broadcast_button = types.KeyboardButton("📨 Send Text to Users")
        markup.add(broadcast_button)
        bot.send_message(message.chat.id, "Welcome to the admin panel:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "📨 Send Text to Users" and message.from_user.id == ADMIN_ID)
def request_broadcast_text(message):
    bot.send_message(message.chat.id, "Please enter the message you want to send to all users:")
    bot.register_next_step_handler(message, broadcast_message)


def broadcast_message(message):
    count = 0
    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()

        for user in users:
            try:
                bot.send_message(int(user), message.text, parse_mode='Markdown')
                count += 1
                time.sleep(0.3)
            except:
                continue

        bot.send_message(message.chat.id, f"✅ Broadcast sent to {count} users.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")


bot.polling(none_stop=True)
