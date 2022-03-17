from API import *
from telegram import *
from telegram.ext import *
import logging
from notify import notify
from common import *
USERNAME, PASSWORD=0,1
logger = logging.getLogger(__name__)
def signup(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_user.id, text="Send me your username.")
    return USERNAME

def signup_username (update: Update, context: CallbackContext):
    username=update._effective_message.text
    context.user_data["username"]=username
    context.bot.send_message(chat_id=update.effective_user.id, text="Send me your password.")
    return PASSWORD

def signup_password (update: Update, context: CallbackContext):
    password=update._effective_message.text
    context.user_data["password"]=password
    coinos_user=create_account(context.user_data["username"], context.user_data["password"])
    if (coinos_user!="ERROR"):
        token= get_token(context.user_data["username"], context.user_data["password"])
        if (token=="ERROR"):
            context.bot.send_message(chat_id=update.effective_user.id, text="ERROR. Try again.")
        else:
            context.user_data["token"]=token
            context.user_data["last_notification"]=0
            chat_id = update.effective_chat.id
            context.job_queue.run_repeating(notify, 15*60,context=chat_id, name="notification")
            user = update.message.from_user
            logger.info("User %s created coinos user %s.", user.username, context.user_data["username"])
            context.bot.send_message(chat_id=update.effective_user.id, text="Account "+coinos_user["username"]+" is created.\nYour Payment page is https://coinos.io/"+coinos_user["username"]+"\nYour Lightning Address is "+coinos_user["username"]+"@coinos.io")
            return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_user.id, text="Try another username.")
    return ConversationHandler.END

signup_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("signup",signup, filters=Filters.chat_type.private)],
    states={
        USERNAME: [MessageHandler(Filters.regex('^[A-Za-z][A-Za-z0-9_]{5,29}$'), signup_username)],
        PASSWORD: [MessageHandler(Filters.regex('.+'), signup_password)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)