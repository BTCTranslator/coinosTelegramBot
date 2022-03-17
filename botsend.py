from API import *
from telegram import *
from telegram.ext import *
from functions import *
from re import match
from common import *
def botsend (update: Update, context: CallbackContext):
    if len(context.args)>=2 and context.args[1].isnumeric() and (match(r"@?(?=\w{1,64}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*",context.args[0]) or check_email(context.args[0])):
        amount=float(context.args[1])
        precision=0
        if (len(context.args)==2):
            asset="BTC"
        elif (len(context.args)>2):
            if(context.args[2]=="sats" or context.args[2]=="BTC" or context.args[2]=="sat"):
                asset="BTC"
            else:
                asset=context.args[2]
                if asset in context.bot_data["assets"]:
                    balances=get_balance(context.user_data["username"],context.user_data["password"])
                    precision=balances[asset]["precision"]
                    amount=amount*(10**precision)
                else:
                    context.bot.send_message(chat_id=update.effective_user.id,text="Invalid asset")
                    return
        if precision==0:
            try:
                amount=int(amount)
            except:
                update.message.reply_text("Invalid amount")
    else:
        context.bot.send_message(chat_id=update.effective_user.id,text="Please specify receiver then amount.\ne.g.\n<code>/send Adam 1 (sats)</code>", parse_mode="html")
        return
    if ("token" in context.user_data):
        if (context.args[0][0] != '@') and (len(context.args[0])<25) and not check_email(context.args[0]):
            send("internal",amount,context.args[0],context.user_data["token"],context.bot_data["assets"][asset])
            if asset=="BTC":asset="sats"
            context.bot.send_message(chat_id=update.effective_user.id,text=f"Sent {amount:g} {asset} to {context.args[0]}", parse_mode="html")
        elif(context.args[0][0] == '@'):
            try:
                sending=send("internal",amount,username_to_coinos_username(context.args[0], context.dispatcher),
                context.user_data["token"],asset=context.bot_data["assets"][asset])
            except:
                context.bot.send_message(chat_id=update.effective_user.id,text="Can't get the receiver's coinos account.")
            else:
                if sending.text[0]=='{':
                    context.bot.send_message(chat_id=username_to_userid(context.args[0])["id"], text="Someone sent you "+context.args[1]+" "+asset)
                    context.bot.send_message(chat_id=update.effective_user.id, text="Sent "+context.args[1]+" "+asset+" to "+context.args[0])
                else:
                    context.bot.send_message(chat_id=update.effective_user.id, text=sending.text)
        elif check_email(context.args[0]):
            if asset=="BTC":
                info=get_lnurl_info(lnaddr_to_lnurl(context.args[0]))
                if amount<info['minSendable']/1000 or amount>info['maxSendable']/1000:
                    context.bot.send_message(chat_id=update.effective_user.id, text=f"Minimum Sendable: {int(info['minSendable']/1000)} sats\nMaximum Sendable: {int(info['maxSendable']/1000)} sats")
                    return
                invoice=get_external_invoice(lnaddr_to_lnurl(context.args[0]),amount)["pr"]
                sending=send("lightning",amount,invoice,context.user_data["token"])
                if (sending[0]=='{'):
                    context.bot.send_message(chat_id=update.effective_user.id, text=f"sent {amount} sats to {context.args[0]}")
                else:
                    context.bot.send_message(chat_id=update.effective_user.id, text=sending)
            else:
                context.bot.send_message(chat_id=update.effective_user.id, text="asset must be btc when sending to lnaddr")
                return
        else:
            update.message.reply_text("Enter a valid @telegram_user or coinos_user")

    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")