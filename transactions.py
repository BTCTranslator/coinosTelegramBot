from API import *
from telegram import *
from telegram.ext import *
from functions import *
from telegram_bot_pagination import InlineKeyboardPaginator
import logging
logger = logging.getLogger(__name__)


@send_action(ChatAction.TYPING)
def history(update: Update, context: CallbackContext):
    if "token" in context.user_data:
        networks={"lightning": "LN", "liquid": "LQ", "bitcoin":"BC","COINOS":"CS"}
        text=""
        txs=payments(context.user_data["username"], context.user_data["password"])
        txs.sort(key=tx_time, reverse=True)
        chat_id = update.effective_chat.id
        context.user_data["txs"]=txs
        context.job_queue.run_once(delete_txs, 60,context=chat_id)
        paginator = InlineKeyboardPaginator(
        -(len(txs)//-5),
        current_page=1
        )
        txs=txs[:5]
        for tx in txs:
            text=text+"\n"+"<code>{:2s} {:2.8f} {:4s} {}</code> {:12s}".format(networks[tx['network']],tx['amount']/10**tx['account']["precision"],tx['account']['ticker'], human_time(coinos_time_to_timestamp(tx["updatedAt"])) ,f"/tx_{tx['id']}")
        
        context.bot.send_message(chat_id=update.effective_user.id,text=text, parse_mode="html",reply_markup=paginator.markup)
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")

def tx(update: Update, context: CallbackContext):
    text=update.effective_message.text
    txid=text.split("_")[1]
    tx_info={}
    if "txs" in context.user_data:
        mytx=[x for x in context.user_data["txs"] if x["id"]==int(txid)]
        tx_info=mytx[0]
    
    if tx_info=={}:
        tx_info=get_tx(txid, context.user_data["username"], context.user_data["password"])
    
    if tx_info == -1:            
        context.bot.send_message(chat_id=update.effective_user.id,text="Error finding tx")
    else:
        if tx_info['account']['ticker']=="BTC":
            text=f"Hash: <code>{tx_info['hash']}</code>\nNetwork: {tx_info['network'].capitalize()} \nAmount: {tx_info['amount']} sats"
        else:
            text=f"Hash: <code>{tx_info['hash']}</code>\nNetwork: {tx_info['network'].capitalize()} \nAmount: {tx_info['amount']/10**tx_info['account']['precision']:.8g} {tx_info['account']['ticker']}"
        if tx_info['network']=='lightning':
            text=text+f"\nPreimage: <code>{tx_info['preimage']}</code>"
        context.bot.send_message(chat_id=update.effective_user.id,text=text, parse_mode="html")

def delete_txs (context: CallbackContext):
    job=context.job
    if "txs" in context.dispatcher.user_data[job.context]:
        del context.dispatcher.user_data[job.context]["txs"]