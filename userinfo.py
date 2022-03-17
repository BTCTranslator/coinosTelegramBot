from API import *
from telegram import *
from telegram.ext import *
import logging
logger = logging.getLogger(__name__)

def token (update: Update, context: CallbackContext):
    if ("token" in context.user_data):
        context.user_data["token"]=get_token(context.user_data["username"], context.user_data["password"])
        context.bot.send_message(chat_id=update.effective_user.id, text="<code>"+context.user_data["token"]+"</code>", parse_mode="html")
        user = update.message.from_user
        logger.info("User %s asked for his token "+context.user_data["token"], user.id)
        
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")


def my_account(update: Update, context: CallbackContext):
    coinos_user=context.user_data
    if "token" in coinos_user:
        context.bot.send_message(chat_id=update.effective_user.id, text="Your username is "+coinos_user["username"]+".\nYour Payment page is https://coinos.io/"+coinos_user["username"]+"\nYour Lightning Address is "+coinos_user["username"]+"@coinos.io", disable_web_page_preview=True)
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")

def my_password(update: Update, context: CallbackContext):
    coinos_user=context.user_data
    if "token" in coinos_user:
        context.bot.send_message(chat_id=update.effective_user.id, text="Your password is <code>"+coinos_user["password"]+"</code>", parse_mode="html")
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")


def balance (update: Update, context: CallbackContext):
    if ("token" in context.user_data):
        balances=get_balance(context.user_data["username"],context.user_data["password"])
        reply="🏦\n"
        for account in balances.items():
            if(account[1]["balance"]>0):
                if account[0]!="BTC":
                    reply+=str(f'{account[1]["balance"]/10**account[1]["precision"]:g}')+"\t"+account[0]
                else:
                    reply+=str(f'{account[1]["balance"]}')+"\t"+"sats"
                    reply+=f"\t ({account[1]['balance']*get_price()['USD']/100000000:.2f} USD)"
                reply+="\n"
            if account[0] not in context.bot_data["assets"]:
                to_add=True
                for asset in context.bot_data["assets"]:
                    if asset==account[1]["asset"]:
                        to_add=False
                context.bot_data["assets"][account[0]]=account[1]["asset"]
        if reply=="🏦\n":
            reply+="0 sats"
        reply+="\n#balance\n/history"
        context.bot.send_message(chat_id=update.effective_user.id, text=reply)
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")

def delete_data (update: Update, context: CallbackContext):
    if (context.user_data):
        user = update.message.from_user
        for x in list(context.user_data):
            del context.user_data[x]
        logger.info("User %s disaccosiated his coinos user", user.username)
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")


