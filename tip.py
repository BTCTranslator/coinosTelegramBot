from API import *
from telegram import *
from telegram.ext import *
from common import *
def tip (update: Update, context: CallbackContext):
    if len(context.args)==0:
        update.message.reply_text("Please specify amount (and asset if not sats)")
        return
    if update.effective_message.reply_to_message is None:
        update.message.reply_text("A tip command should be in a reply")
        return
    new_account=False
    if "token" in context.user_data:
        sender=update.effective_message.from_user.username
        sender_id=update.effective_message.from_user.id
        receiver=update.effective_message.reply_to_message.from_user.username
        receiver_id=update.effective_message.reply_to_message.from_user.id
        msg_id=update.effective_message.reply_to_message.message_id
        if "token" in context.dispatcher.user_data[receiver_id]:
            if (receiver=="coinostelegrambot"):
                receiver=admin
                coinos_receiver=admin_on_coinos
            else:
                coinos_receiver=context.dispatcher.user_data[receiver_id]["username"]
        else:
            if update.effective_message.reply_to_message.from_user.is_bot:
                context.bot.send_message(chat_id=sender_id,text="Can't tip an unknown bot.")
                return
            new_account=create_arbitrary_account()
            context.dispatcher.user_data[receiver_id]["username"]=new_account[0]
            context.dispatcher.user_data[receiver_id]["password"]=new_account[1]
            token= get_token(context.dispatcher.user_data[receiver_id]["username"], context.dispatcher.user_data[receiver_id]["password"])
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
        
        amount=float(context.args[0])
        precision=0
        if (len(context.args)==1):
            asset="BTC"
        else:
            if(context.args[1]=="sats" or context.args[1]=="BTC"):
                asset="BTC"
            else:
                asset=context.args[1]
                if asset in context.bot_data["assets"]:
                    balances=get_balance(context.user_data["username"],context.user_data["password"])
                    precision=balances[asset]["precision"]
                    amount=amount*(10**precision)
                else:
                    context.bot.send_message(chat_id=sender_id,text="Invalid asset")
                    if new_account:
                        for key in list(context.dispatcher.user_data[receiver_id]):
                            del context.dispatcher.user_data[receiver_id][key]
                    return
        if precision==0:
            try:
                amount=int(amount)
            except:
                update.message.reply_text("Invalid amount")
        
        if (coinos_receiver!=context.user_data["username"]):
            sending=send("internal", amount, coinos_receiver, context.user_data["token"], context.bot_data["assets"][asset])
            if (sending.text[0]=='{'):
                if (asset == "BTC"):
                    asset="sats" 
                if (precision==0):
                    amount=int(amount/10**precision)
                else:
                    amount=float(amount/10**precision)
                context.bot.send_message(chat_id=sender_id, text="You tipped @"+receiver+" "+str(amount)+" "+asset)
                if new_account:
                    update.message.reply_text(f"{str(amount)} {asset} given from @{sender} to @{receiver}. To manage your funds, start a conversation with @coinostelegrambot.", reply_to_message_id=msg_id)
                else:
                    if not update.effective_message.reply_to_message.from_user.is_bot:
                        context.bot.send_message(chat_id=receiver_id, text="@"+sender+" tipped you "+str(amount)+" "+asset)
            else:
                context.bot.send_message(chat_id=sender_id,text=sending.text)
        else:
            update.message.reply_text("Can't tip oneself")
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")
