
from telegram import *
from telegram.ext import *
import logging
import configparser
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')
admin=config["Default"]["ADMIN"]
admin_on_coinos=config["Default"]["ADMIN_ON_COINOS"]
BOT_TOKEN=config["Default"]["BOTTOKEN"]

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    logger.info("User %s started the bot.", user.username)
    if (context.user_data):
        update.message.reply_text("You already have an account "+context.user_data["username"])
    else:
        update.message.reply_markdown_v2(
            fr'Hi {user.mention_markdown_v2()}\! \n Send /login or /signup',
            reply_markup=ForceReply(force_reply=True,
                                    input_field_placeholder="/login or /signup"))


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.username)
    to_cancel=[]
    for obj in context.user_data.keys():
        if obj!="last_notification" and obj!="token" and obj!="username" and obj!="password":
            to_cancel.append(obj)
    for obj in to_cancel:
        context.user_data.pop(obj, None)
    update.message.reply_text("Canceled.")
    return ConversationHandler.END

