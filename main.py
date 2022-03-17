import logging
from telegram import *
from telegram.ext import *
from telegram_bot_pagination import InlineKeyboardPaginator
import os
import sys
from threading import Thread
from ptbcontrib.postgres_persistence import PostgresPersistence
from botsend import botsend
from tip import tip
from login import *
from signup import *
from notify import notify
from userinfo import *
from receive import *
from ln import *
from transactions import *
from notifications import *
from liquid import *
from serverinfo import *
from bitcoin import *
from lnurl import *
from qhandler import qhandler
from common import *
from inlinequery import inlinequery

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


    
def main() -> None:
    DB_URI = config["postgres"]["URL"]
    updater = Updater(BOT_TOKEN,persistence=PostgresPersistence(url=DB_URI))
    dispatcher = updater.dispatcher
    
    #Conversation Handlers
    dispatcher.add_handler(liquid_conv_handler)
    dispatcher.add_handler(bitcoin_conv_handler)
    dispatcher.add_handler(lnurl_conv_handler)
    dispatcher.add_handler(ln_conv_handler)
    dispatcher.add_handler(login_conv_handler)
    dispatcher.add_handler(signup_conv_handler)

    #Command Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("token", token))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("delete_data", delete_data))
    dispatcher.add_handler(CommandHandler("send", botsend))
    dispatcher.add_handler(CommandHandler("invoice", invoice))
    dispatcher.add_handler(CommandHandler("tip", tip))
    dispatcher.add_handler(CommandHandler("enable_notifications", enable_notifications))
    dispatcher.add_handler(CommandHandler("disable_notifications", disable_notifications))
    dispatcher.add_handler(CommandHandler("history", history))
    dispatcher.add_handler(CommandHandler("server_funds", server_funds))
    dispatcher.add_handler(CommandHandler("ln_node", ln_node))
    dispatcher.add_handler(CommandHandler("receive", receive))
    dispatcher.add_handler(CommandHandler("my_account", my_account))
    dispatcher.add_handler(CommandHandler("my_password", my_password))

    #Query Handler
    dispatcher.add_handler(CallbackQueryHandler(qhandler))
    
    #Inline Query Handler
    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    #Message Handlers
    dispatcher.add_handler(MessageHandler(Filters.regex('^(/tx_)'), tx))
    
    #Set List of Commands
    commands=updater.bot.set_my_commands([("/login", "login to a coinos user"),
                                          ("/signup", "signup to a coinos user"),
                                          ("/my_account", "your account information"),
                                          ("/balance","get your balances"),
                                          ("/delete_data", "logout of your coinos user"),
                                          ("/send", "send to a telegram @user or a coinos user"),
                                          ("/invoice", "get a lightning invoice"),
                                          ("/history", "a list of your payments"),
                                          ("/server_funds", "Available BTC funds on server"),
                                          ("/receive", "Bitcoin and Liquid Addresses"),
                                          ("/enable_notifications", "Enable new payments notifications"),
                                          ("/disable_notifications", "Disable new payments notifications"),
                                          ("/ln_node", "coinos LN node addresses"),
                                          ],
                                          scope=BotCommandScopeAllPrivateChats())
    commands=updater.bot.set_my_commands([("/tip", "e.g. tip 0.5 USDt"),
                                          ("/balance","get your balances"),
                                          ("/send", "send to a telegram @user or a coinos user"),
                                          ("/invoice", "get a lightning invoice"),
                                          ("/server_funds", "Available BTC funds on server"),
                                          ("/ln_node", "coinos LN node addresses")],
                                          scope=BotCommandScopeAllGroupChats())
    #Inline Query
    
    
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()
    
    def stop_command(update, context):
        update.message.reply_text('Bot is stopping...')
        updater.stop()
    
    dispatcher.add_handler(CommandHandler('r', restart, filters=Filters.user(username=f'@{admin}')))
    dispatcher.add_handler(CommandHandler('sd', stop_command, filters=Filters.user(username=f'@{admin}')))

    #Start the bot
    if "assets" not in dispatcher.bot_data:
        dispatcher.bot_data["assets"]= {}

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

