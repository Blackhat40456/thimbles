import telebot
import time
import random
from telebot import types
import os

API_TOKEN = "7560937841:AAHizOMSN94qemWXYknRwW73nWAP0Ynt4wM"
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 5767213888
required_channels = {
    "@redhatJoinmain": "Join Channel 1 📡",
    "@redhatFreeHacks": "Join Channel 2 📡"
}

IMAGES = [
    "https://i.imgur.com/7uuILcO.jpeg",
    "https://i.imgur.com/iwDyPNq.jpeg",
    "https://i.imgur.com/ogjTLdZ.jpeg",
]

if not os.path.exists("users.txt"):
    open("users.txt", "w").close()
if not os.path.exists("referrals.txt"):
    open("referrals.txt", "w").close()


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


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    is_new_user = False

    with open("users.txt", "a+") as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(str(user_id) + "\n")
            is_new_user = True
            if len(args) > 1:
                inviter_id = args[1]
                if inviter_id != str(user_id):
                    add_referral(inviter_id, user_id)

    channel_status = has_joined_required_channels(user_id)
    if all(status == '✅' for status in channel_status.values()):
        referrals = get_user_referrals(user_id)
        if referrals >= 3:
            welcome_user(message, is_new_user)
        else:
            ask_for_referrals(message, referrals)
    else:
        ask_to_join_channels(message, channel_status)


def ask_to_join_channels(message, channel_status):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for channel, status in channel_status.items():
        name = required_channels[channel]
        btn = types.InlineKeyboardButton(f"{status} {name}", url=f"https://t.me/{channel[1:]}")
        markup.add(btn)
    markup.add(types.InlineKeyboardButton("✅ I've Joined", callback_data="check_channels"))
    bot.send_message(message.chat.id, "*You must join all channels first!*", reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == "check_channels")
def check_channels(call):
    user_id = call.from_user.id
    status = has_joined_required_channels(user_id)
    if all(s == '✅' for s in status.values()):
        referrals = get_user_referrals(user_id)
        if referrals >= 3:
            welcome_user(call.message, False)
        else:
            ask_for_referrals(call.message, referrals)
    else:
        bot.answer_callback_query(call.id, "❌ You still haven't joined all channels!")


def ask_for_referrals(message, count):
    markup = types.InlineKeyboardMarkup()
    invite_link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    markup.add(types.InlineKeyboardButton("📢 Share your invite link", url=invite_link))
    referral_message = (
        f"<b>You need 3 referrals to access the bot!</b>\n\n"
        f"<i>👥 Current referrals: {count}/3</i>\n"
        f"<i>🔗 Invite Link:</i>\n<a href='{invite_link}'>Click here to Start👈</a>\n\n"
        "<i>👉 Share this link with your friends. They must also join the required channels.</i>"
    )
    bot.send_message(message.chat.id, referral_message, reply_markup=markup, parse_mode='HTML')


def welcome_user(message, is_new):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🌀 NEXT BALL POSITION"),
        types.KeyboardButton("🛑 STOP HACK"),
        types.KeyboardButton("🎲 NEW GAME"),
        types.KeyboardButton("🔄 Restart"),
        types.KeyboardButton("🌐 Open")
    )
    user_count = sum(1 for _ in open("users.txt"))
    welcome_text = f"*🎮 Welcome to the Game Menu!*\n👥 Total users: *{user_count}*"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
    if is_new:
        bot.send_message(message.chat.id, "✅ Thanks for joining! You're now inside.")


@bot.message_handler(func=lambda msg: msg.text == "🌀 NEXT BALL POSITION")
def next_ball(message):
    bot.send_message(message.chat.id, "🔄 Calculating next ball position...")
    time.sleep(2)
    bot.send_photo(message.chat.id, random.choice(IMAGES), caption="✅ Next position ready!")


@bot.message_handler(func=lambda msg: msg.text == "🛑 STOP HACK")
def stop_hack(message):
    bot.send_message(message.chat.id, "⚠️ Stopping the hack...")
    time.sleep(2)
    bot.send_message(message.chat.id, "✅ Hack stopped successfully!")


@bot.message_handler(func=lambda msg: msg.text == "🎲 NEW GAME")
def new_game(message):
    bot.send_message(message.chat.id, "🆕 Starting a new game...")
    time.sleep(2)
    bot.send_message(message.chat.id, "✅ New game ready!")


@bot.message_handler(func=lambda msg: msg.text == "🔄 Restart")
def restart(message):
    start(message)


@bot.message_handler(func=lambda msg: msg.text == "🌐 Open")
def open_site(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Visit Website", url="https://example.com"))  # replace with your link
    bot.send_message(message.chat.id, "Tap below to open our official site:", reply_markup=markup)


# Admin Panel
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📨 Broadcast Text", "🖼️ Broadcast Media")
        bot.send_message(message.chat.id, "Welcome to the Admin Panel:", reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == "📨 Broadcast Text" and msg.from_user.id == ADMIN_ID)
def ask_text_broadcast(message):
    bot.send_message(message.chat.id, "Send the message you'd like to broadcast to all users:")
    bot.register_next_step_handler(message, broadcast_message)


@bot.message_handler(func=lambda msg: msg.text == "🖼️ Broadcast Media" and msg.from_user.id == ADMIN_ID)
def ask_media_broadcast(message):
    bot.send_message(message.chat.id, "Send photo/video/document with a caption.\nAdd `>>LINK-URL` at the end of caption to create a button.")
    bot.register_next_step_handler(message, handle_media_broadcast)


def broadcast_message(message):
    count = 0
    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
        for user in users:
            try:
                bot.send_message(int(user), message.text, parse_mode='Markdown')
                count += 1
                time.sleep(0.1)
            except:
                continue
        bot.send_message(message.chat.id, f"✅ Broadcast sent to {count} users.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")


def handle_media_broadcast(message):
    file_id = None
    markup = None
    caption = message.caption or ""
    link = None

    if ">>" in caption:
        caption, link = caption.split(">>", 1)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔗 Open Link", url=link.strip()))

    with open("users.txt", "r") as f:
        users = f.read().splitlines()

    count = 0
    for user in users:
        try:
            if message.photo:
                bot.send_photo(int(user), message.photo[-1].file_id, caption=caption.strip(), reply_markup=markup)
            elif message.video:
                bot.send_video(int(user), message.video.file_id, caption=caption.strip(), reply_markup=markup)
            elif message.document:
                bot.send_document(int(user), message.document.file_id, caption=caption.strip(), reply_markup=markup)
            count += 1
            time.sleep(0.1)
        except:
            continue

    bot.send_message(message.chat.id, f"✅ Media broadcast sent to {count} users.")


bot.polling(none_stop=True)
