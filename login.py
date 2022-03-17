from API import *
from telegram import *
from telegram.ext import *
from notify import notify
from common import *
USERNAME, PASSWORD=0,1

def login (update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_user.id, text="Send me your username.")
    return USERNAME

def login_username (update: Update, context: CallbackContext):
    username=update._effective_message.text
    context.user_data["username"]=username
    context.bot.send_message(chat_id=update.effective_user.id, text="Send me your password.")
    return PASSWORD

def login_password (update: Update, context: CallbackContext):
    password=update._effective_message.text
    context.user_data["password"]=password
    token= get_token(context.user_data["username"], context.user_data["password"])
    if (token=="ERROR"):
        context.bot.send_message(chat_id=update.effective_user.id, text="ERROR. Try again.")
    else:
        context.user_data["token"]=token
        context.user_data["last_notification"]=0
        chat_id = update.effective_chat.id
        context.job_queue.run_repeating(notify, 15*60,context=chat_id, name="notification")
        context.bot.send_message(chat_id=update.effective_user.id, text="Logged in")
    return ConversationHandler.END

login_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("login",login, filters=Filters.chat_type.private)],
            states={
                USERNAME: [MessageHandler(Filters.regex('^[A-Za-z][A-Za-z0-9_-]{3,29}$'), login_username)],
                PASSWORD: [MessageHandler(Filters.regex('.+'), login_password)],
            },
        fallbacks=[CommandHandler('cancel', cancel)],
    )