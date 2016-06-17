#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import threading

import telebot

from telegram_bot_users import *

# Constants to indicate steps while user is entering password
TEAM_USER_LOGGING = 0
TEAM_USER_ACCEPTED = 1

# Data structure for list of bot`s users
team_users = TeamUserList()

# Insert your telegram bot`s token here
TOKEN = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(TOKEN)

user_step = {}
user_active_dialog = {}
reply_data_db = {}

# Welcoming message
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Support_Bot!")

# Custom command to add user to an operator`s team
@bot.message_handler(commands=['on'])
def subscribe_chat(message):
    if message.chat.id in team_users:
        bot.reply_to(message, "You are already an operator")
    else:
        user_step[message.chat.id] = TEAM_USER_LOGGING
        bot.reply_to(message, "Enter team secret phrase:")


# Here we catch user message after '/on' command and
# interpret it as a password
@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == TEAM_USER_LOGGING)
def team_user_login(message):
    if message.text == 'password1':
        team_users.add(TeamUser(message.chat.id))
        user_step[message.chat.id] = TEAM_USER_ACCEPTED
        bot.reply_to(message, "You`ve started receiving messages")
    else:
        bot.reply_to(message, "Wrong secrete phrase, try again")

# Custom command to remove user from an operator`s team
@bot.message_handler(commands=['off'])
def team_user_logout(message):
    if message.chat.id not in team_users:
        bot.reply_to(message, "You are not an operator anyway")
    else:
        team_users.remove_by_chat_id(message.chat.id)
        bot.reply_to(message, "You`ve stopped receiving messages")

# Use this function when you need to send something
# to an operators team
def process(message):
    text = '%s\n%s writes to %s\nReply: %s' %\
           (message, 'Vasya', 'Super Support Team', '*reply_url*')

    # Sending message to every operator in our list
    for user in team_users:
        bot.send_message(user.chat_id, text, disable_web_page_preview=True)


threading.Thread(target=bot.polling).start()
while True:
    msg = input("Enter your message: ")
    process(msg)