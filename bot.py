import os
import telegram
import logging
import datetime
from randomEmoji import random_emoji
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from collections import OrderedDict

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = 'TELEGRAM-BOT-TOKEN'
BOT_NAME = 'TELEGRAM-BOT-NAME'
HEROKU_URL = 'https://HEROKU-APP-NAME.herokuapp.com'

PORT = int(os.environ.get('PORT', '8443'))
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

# add handlers
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)

updater.bot.set_webhook(HEROKU_URL + "/" + TOKEN)

# Intiate new poll
def start(bot, update):
    chat_id = update.message.chat.id
    answers = pollAnswers()
    poll = emptyPoll(answers)

    title = update.message.text
    title = title.replace("/start@"+BOT_NAME, "").strip()
    title = title.replace("/start", "").strip()

    if len(title) == 0: # Auto title
        tomorrowDayName = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%A")
        poll["title"] = tomorrowDayName + ' ' + str(random_emoji()[0])
    else: # Manual title.
        poll["title"] = title

    text = pollText(poll)

    reply_markup = poll_reply_markup(answers)
    message = bot.sendMessage(chat_id=chat_id, text=text, reply_markup=reply_markup)

def pollAnswers():
    return ["Yes!", "Morning", "Evening", "No"]

def emptyPoll(answers):
    poll = {}
    for answer in answers:
        poll[answer] = []
    return poll


def poll_answer_handler(bot, update):
    chat_id = update.callback_query.message.chat.id
    poll_id = update.callback_query.message.message_id
    answer = update.callback_query.data
    user_name = update.callback_query.from_user.username
    user_first_name = update.callback_query.from_user.first_name
    user_last_name = update.callback_query.from_user.last_name

    if user_last_name is None:
        user_last_name = ""
    if user_first_name is not None:
        user_name = user_first_name + " " + str(user_last_name)
    elif user_name is None:
        user_name = "Unknown Person (didn't set user-name or first-name)"
    user_name = user_name.strip()


    poll_text = update.callback_query.message.text
    poll = pollFromText(poll_text)

    addVote(poll, user_name, answer)

    new_poll_text = pollText(poll)
    reply_markup = poll_reply_markup((pollAnswers()))
    bot.edit_message_text(new_poll_text, chat_id, poll_id, reply_markup=reply_markup)

def addVote(poll, user_name, answer):
    if answer not in poll:
        poll[answer] = []

    for poll_answer in poll:
        if user_name in poll[poll_answer]:
            poll[poll_answer].remove(user_name)
            break

    poll[answer].append(user_name)

def poll_reply_markup(answers):
    keyboard_buttons = []
    for answer in answers:
        keyboard_buttons.append([InlineKeyboardButton(answer, callback_data=answer)])
    return InlineKeyboardMarkup(keyboard_buttons)

def pollFromText(poll_text):
    poll = OrderedDict()

    poll["title"] = poll_text.split("\n")[0].replace("**", "")

    lines = poll_text.split("\n")[1:]

    answer = None
    for line in lines:
        if len(line.strip()) == 0:
            continue;

        if line[0] != ' ':
            answer = line.split("[")[0].strip()
            poll[answer] = []
        else:
            poll[answer].append(line.strip())

    return poll

def pollText(poll):
    text = '**Poll Title**'

    if "title" in poll:
        text = "**" + poll["title"] + "**"

    text = text + '\n\n'
    text = text + formatted_poll(poll)
    return text

def formatted_poll(poll):
    results = ""

    for answer in poll:
        if answer == "title":
            continue

        result_text = '{0} [{1}]\n'.format(answer,len(poll[answer]))
        results = results + result_text

        for name in poll[answer]:
            name_text = '  {0}\n'.format(name)
            results = results + name_text

        results = results + '\n\n'

    return results

start_handler = CommandHandler('start', start)
poll_answer_handler = CallbackQueryHandler(poll_answer_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(poll_answer_handler)
