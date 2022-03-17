from API import *
from telegram import *
from telegram.ext import *
from functions import *
from telegram_bot_pagination import InlineKeyboardPaginator
import logging
import time
logger = logging.getLogger(__name__)

def qhandler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if(query.data=="pay"):
        if "invoice" not in context.user_data:
            context.user_data["invoice"]={}
            invoice_data=read_ln_invoice(query.message.reply_to_message.text)
            context.user_data["invoice"]["text"]=query.message.reply_to_message.text
            context.user_data["invoice"]["amount"]=invoice_data["amount"]
        sending=send("lightning",context.user_data["invoice"]["amount"],context.user_data["invoice"]["text"],context.user_data["token"])
        if (sending[0]=='{'):
            query.edit_message_text(text=query.message.text+f"\nSent.")
        else:
            query.edit_message_text(text=query.message.text+f"\n{sending}.")
        context.user_data.pop("invoice", None)
    elif(query.data=="cancel"):
        context.user_data.pop("tx", None)
        context.user_data.pop("lnurl", None)
        context.user_data.pop("qr-data", None)
        context.user_data.pop("invoice", None)
        try:
            query.edit_message_text(text=query.message.text+f"\nCancelled.")
        except:
            query.edit_message_text(text="Cancelled.")
    elif (query.data=="send-liquid"):
        sending=send(context.user_data["tx"]["network"], context.user_data["tx"]["amount"], context.user_data["tx"]["address"], context.user_data["token"],context.bot_data["assets"][context.user_data["tx"]["asset"]],context.user_data["tx"]["feerate"])
        if(sending[0]=='{'):
            query.edit_message_text(text=query.message.text+f"\nSent.")
        del context.user_data["tx"]
    elif (query.data=="send-bitcoin"):
        sending=send(context.user_data["tx"]["network"], context.user_data["tx"]["amount"], context.user_data["tx"]["address"], context.user_data["token"],context.bot_data["assets"][context.user_data["tx"]["asset"]],context.user_data["tx"]["feerate"])
        if(sending.text[0]=='{'):
            query.edit_message_text(text=query.message.text+f"\nSent.")
        else:
            context.bot.send_message(chat_id=update.effective_user.id, text=sending.text)
        del context.user_data["tx"]
    elif(query.data.isnumeric()):
        if "txs" in context.user_data:
            txs=context.user_data["txs"]
        else:
            txs=payments(context.user_data["username"], context.user_data["password"])
            txs.sort(key=tx_time, reverse=True)
            context.user_data["txs"]=txs
            context.job_queue.run_once(delete_txs, 60,context=update.effective_user.id)

        paginator = InlineKeyboardPaginator(
        -(len(txs)//-5),
        current_page=int(query.data)
        )
        networks={"lightning": "LN", "liquid": "LQ", "bitcoin":"BC","COINOS":"CS"}
        text=""
        txs=txs[(int(query.data)-1)*5:int(query.data)*5]
        for tx in txs:
            text=text+"\n"+"<code>{:2s} {:2.8f} {:4s} {}</code> {:12s}".format(networks[tx['network']],tx['amount']/10**tx['account']["precision"],tx['account']['ticker'], human_time(coinos_time_to_timestamp(tx["updatedAt"])) ,f"/tx_{tx['id']}")
        query.edit_message_text(text=text, parse_mode="html",reply_markup=paginator.markup)
    
    
    elif (query.data.startswith("claim-")):
        
        createdAt=query.data[6:]
        for giveaway in context.bot_data["giveaways"]:
            if giveaway["createdAt"]==createdAt:# and query.from_user.id!=giveaway["from_user"]
                new_account=False
                sender_id=giveaway["from_user"]
                receiver=query.from_user.username
                receiver_id=query.from_user.id
                asset=giveaway["asset"]
                amount=giveaway["amount"]
                if "token" not in context.user_data:
                    new_account=create_arbitrary_account()
                    context.dispatcher.user_data[receiver_id]["username"]=new_account[0]
                    context.dispatcher.user_data[receiver_id]["password"]=new_account[1]
                    token=get_token(context.dispatcher.user_data[receiver_id]["username"], context.dispatcher.user_data[receiver_id]["password"])
                    coinos_receiver=context.dispatcher.user_data[receiver_id]["username"]
                    if (token=="ERROR"):
                        update.message.reply_text("Unexpected Error.")
                        del context.dispatcher.user_data[receiver_id]["username"]
                        del context.dispatcher.user_data[receiver_id]["password"]
                        return
                    else:
                        context.dispatcher.user_data[receiver_id]["token"]=token
                        context.dispatcher.user_data[receiver_id]["last_notification"]=0
                        new_account=True
                
                sending=send("internal",amount,context.user_data["username"],giveaway["token"],context.bot_data["assets"][asset])
                if (sending[0]=='{'):
                    if asset=="BTC": asset="sats"
                    amount=float(float((amount))/(10**giveaway["precision"]))
                    if (new_account==False):
                        query.edit_message_text(text="Done.")
                        context.bot.send_message(chat_id=sender_id,text=f"Sent {amount:g} {asset} to @{receiver}", parse_mode="html")
                        context.bot.send_message(chat_id=receiver_id,text=f"Received {amount:g} {asset} from a giveaway", parse_mode="html")
                    else:
                        query.edit_message_text(text="Done. To manage your funds open a conversation with @coinostelegrambot.")
                        context.bot.send_message(chat_id=sender_id,text=f"Sent {amount} {asset} to @{receiver}", parse_mode="html")
                else:
                    query.edit_message_text(text=sending)
    
        context.bot_data["giveaways"]=[x for x in context.bot_data["giveaways"] if x["createdAt"]!=createdAt]
        context.bot_data["giveaways"]=[x for x in context.bot_data["giveaways"] if float(x["createdAt"])+x["TTL"]<time.time()]
        
    