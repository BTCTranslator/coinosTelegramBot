
from telegram import *
from telegram.ext import *
from API import *
def server_funds (update: Update, context: CallbackContext):
    funds=get_server_balances()
    text="<code>{:9s}: {:9d}\n{:9s}: {:9d}\n{:9s}: {:9d}\n{:9s}: {:9d}\n</code>".format("Bitcoin",funds["bitcoin"],"Liquid",funds["liquid"],"Lightning",funds["lnchannel"],"Total",funds["total"])
    update.message.reply_text(text,parse_mode="html")

def ln_node (update: Update, context: CallbackContext):
    text="Clearnet:\n<code>02868e12f320073cad0c2959c42559fbcfd1aa326fcb943492ed7f02c9820aa399@coinos.io:9735</code>\nDarknet:\n<code>02868e12f320073cad0c2959c42559fbcfd1aa326fcb943492ed7f02c9820aa399@jbx2afvrkuxopekkvipjcult26ffvu3t4lq5x7k4zcs3z7hovu4kdtyd.onion:9735</code>"
    update.message.reply_text(text,parse_mode="html")
