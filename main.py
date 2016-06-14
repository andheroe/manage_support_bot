#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import string
import threading

import telebot
from telebot import types

from telegram_bot_users import *

TEAM_USER_LOGGING = 0
TEAM_USER_ACCEPTED = 1
BUSINESS_USER_REPLYING = 2

team_users = TeamUserList()

TOKEN = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(TOKEN)

user_step = {}
user_active_dialog = {}
reply_data_db = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Support_Bot!")

@bot.message_handler(commands=['on'])
def subscribe_chat(message):
    if message.chat.id in team_users:
        bot.reply_to(message, "You are already an operator")
    else:
        user_step[message.chat.id] = TEAM_USER_LOGGING
        bot.reply_to(message, "Enter team secret phrase:")


@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == TEAM_USER_LOGGING)
def team_user_login(message):
    global team_users
    if message.text == 'password1':
        team_users.add(TeamUser(message.chat.id))
        user_step[message.chat.id] = TEAM_USER_ACCEPTED
        bot.reply_to(message, "You`ve started receiving messages")
    else:
        bot.reply_to(message, "Wrong secrete phrase, try again")


@bot.message_handler(commands=['off'])
def team_user_logout(message):
    global team_users
    if message.chat.id not in team_users:
        bot.reply_to(message, "You are not an operator anyway")
    else:
        team_users.remove_by_chat_id(message.chat.id)
        bot.reply_to(message, "You`ve stopped receiving messages")

@bot.callback_query_handler(func=lambda call: True)
def reply_callback(call):
    reply_data = reply_data_db.get(call.data.split()[1])
    if reply_data is not None:
        for chat_id, msg_id in reply_data['chat_msg_ids']:
            if chat_id == call.message.chat.id:
                if call.data.split()[0] == 'admin_reply':
                    bot.edit_message_text(call.message.text + u'\nYou started answering',
                                          chat_id, msg_id, disable_web_page_preview=True)
            else:
                bot.edit_message_text(call.message.text + '\n\n' + call.from_user.first_name + u' is answering\n',
                                      chat_id, msg_id, disable_web_page_preview=True)

def process(message):
    msg_reply_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
    text = '%s\n%s writes to %s\nReply: %s' %\
           (message, 'some_user', 'some_company', 'some_reply_url')
    markup = types.InlineKeyboardMarkup(row_width=3)
    reply_data_db[msg_reply_id] = {'to_name': 'some_user', 'chat_msg_ids': []}
    itembtn = telebot.types.InlineKeyboardButton('Reply', callback_data="admin_reply " +  msg_reply_id)
    markup.add(itembtn)

    for user in team_users:
        reply = bot.send_message(user.chat_id, text, reply_markup=markup, disable_web_page_preview=True)
        reply_data_db[msg_reply_id]['chat_msg_ids'].append((reply.chat.id, reply.message_id))


threading.Thread(target=bot.polling).start()
while True:
    msg = input("Enter your message: ")
    process(msg)