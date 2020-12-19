import enum
from typing import Text
from telegram import update
import logging
from telegram.ext import Updater, CommandHandler, updater
import requests
import re
import os

from telegram.ext.callbackcontext import CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

class EmbyPath(enum.Enum):
    PING = "/System/Ping"
    INFO = "/System/Info"
    ITEM = "/Items/Counts"
    LIBRARY = "Library/Refresh"

    def __str__(self) -> str:
        return str(self.value)

SERVER = os.getenv('SERVER')
API_KEY = os.getenv('API_KEY')

BOT_ID = os.getenv('BOT_ID')
USER_ID = map(int, os.getenv("USER_ID").split(','))
ADMIN = int(os.getenv("ADMIN"))
#config['SERVER'] + param + "?api_key=" + config['EMBY_API']

def get_complete_url(path: str):
    return SERVER + path + "?api_key=" + API_KEY

def make_get_request(path):
    return requests.get(get_complete_url(path)).json()

def make_post_request(path):
    return requests.post(get_complete_url(path)).json()

def extract_json(content, key):
    return content[key]
    
def check_server(update: update.Update, context: CallbackContext):
    if (not check_chat_id(update, context)):
        return
    content = make_get_request(EmbyPath.INFO.value)
    count = make_get_request(EmbyPath.ITEM.value)
    pendingRestart = extract_json(content, "HasPendingRestart")
    hasUpdateAvailable = extract_json(content, "HasUpdateAvailable")
    local_addr = extract_json(content, "LocalAddress")
    wan_addr = extract_json(content, "WanAddress")
    server_name = extract_json(content, "ServerName")
    version = extract_json(content, "Version")
    movies = extract_json(count, "MovieCount")
    serie = extract_json(count, "SeriesCount")
    text = "{} is online!\n\nLocal Address: {}\nWan Address: {}\nVersion: {}\n\nMovies: {}\nSeries: {}".format(server_name, local_addr, wan_addr, version, movies, serie)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def refresh_library(update: update.Update, context: CallbackContext):
    if (not check_chat_id(update, context)):
        return
    content = make_post_request(EmbyPath.LIBRARY.value)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Library scan in progress...")


def get_status(update, context):
    if (not check_chat_id(update, context)):
        return
    content = make_get_request(EmbyPath.INFO.value)
    if content != None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Le serveur {} est allumé! :)".format(extract_json(content, "ServerName")))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="A priori le serveur est éteint.. :(")


def start(update, context):
    if (not check_chat_id(update, context)):
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bonjour, le bot est bien actif!")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Je regarde si le serveur est allumé...")

def make_backup(update: update.Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="TODO")

def check_chat_id(update: update.Update, context: CallbackContext) -> bool:
    if update.effective_chat.id not in USER_ID:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to access this bot.")
        context.bot.send_message(chat_id=ADMIN, text="{} {} ({}): {} try to acces to your bot".format(update.effective_user.last_name, update.effective_user.first_name, update.effective_user.username, update.effective_chat.id))
        return False
    return True

def main():
    updater = Updater(token=BOT_ID, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(CommandHandler('status', check_server))
    dispatcher.add_handler(CommandHandler('refresh', refresh_library))
    dispatcher.add_handler(CommandHandler('backup', make_backup))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()