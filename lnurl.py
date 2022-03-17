from telegram import *
from telegram.ext import *
import logging
import json
from API import *
from QRHandlers import *
from common import *
logger = logging.getLogger(__name__)
ASSET, AMOUNT, FEERATE, COMMENT=0,1,2,3

def read_lnurl (update: Update, context: CallbackContext):
    if "token" in context.user_data:
        if(update.effective_message.photo):
            file_id = update.effective_message.effective_attachment[1].file_id
            with open('sample.json', 'r') as openfile:   
                json_object = json.load(openfile)
            for id, data in json_object:
                if id == file_id:
                    bech32lnurl=data
        
        elif(update.effective_message.text):
            bech32lnurl=update.effective_message.text
        url=lnurl(bech32lnurl)
        info=get_lnurl_info(url)
        context.user_data["lnurl"]={}
        context.user_data["lnurl"]["callback"]=info["callback"]
        context.user_data["lnurl"]["minSendable"]=info['minSendable']
        context.user_data["lnurl"]["maxSendable"]=info['maxSendable']
        context.user_data["lnurl"]["commentAllowed"]=info['commentAllowed']


        update.message.reply_text(f"Minimum amount to pay is {context.user_data['lnurl']['minSendable']/1000}.\nMaximum amount to pay is {context.user_data['lnurl']['maxSendable']/1000}.\nPlease send to me the amount you want to send.")
        return AMOUNT
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")
        return CoversationHandler.END

def amount_lnurl (update: Update, context: CallbackContext):
    if context.user_data["lnurl"]:
        amount=update.effective_message.text
        if amount.isnumeric():
            amount=int(amount)*1000
            if amount>=context.user_data["lnurl"]["minSendable"] and amount<=context.user_data["lnurl"]["maxSendable"]:

                if context.user_data["lnurl"]["commentAllowed"]>0:
                    update.message.reply_text(f"Send a comment to confirm the payment.")
                    context.user_data["lnurl"]["amount"]=amount
                    return COMMENT
                else:
                    msg_id=update.message.reply_text(invoice["pr"]).message_id
                    invoice_data=read_ln_invoice(invoice["pr"])
                    keyboard = [[
                                InlineKeyboardButton("Cancel", callback_data='cancel'),
                                InlineKeyboardButton("Pay", callback_data="pay")
                            ]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_html(str(invoice_data["amount"])+" sat"+'\n'+"<i>"+str(invoice_data["memo"])+'\n'+'\n'+"</i>"+"Hash: <code>"+invoice_data["hash"]+"</code>\n"+"Created at: "+ str(invoice_data["CreatedAt"])+'\n'+"Expires at: "+ str(invoice_data["ExpiresAt"])+"\nPayee: <code>"+ invoice_data["payee"]+"</code>",
                                            reply_markup=reply_markup,
                                            reply_to_message_id=msg_id)
                    del context.user_data["lnurl"]
                    return ConversationHandler.END
            else:
                update.message.reply_text("Please send a valid amount.")
                return AMOUNT
        else:
            update.message.reply_text("Please send a valid amount.")
            return AMOUNT
    else:    
        return ConversationHandler.END
    
def comment_lnurl(update: Update, context: CallbackContext):
    comment=update.effective_message.text

    invoice=get_external_invoice(context.user_data["lnurl"]["callback"],context.user_data["lnurl"]["amount"],comment)
    
    msg_id=update.message.reply_text(invoice["pr"]).message_id
    invoice_data=read_ln_invoice(invoice["pr"])
    keyboard = [[
                InlineKeyboardButton("Cancel", callback_data='cancel'),
                InlineKeyboardButton("Pay", callback_data="pay")
            ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_html(str(invoice_data["amount"])+" sat"+'\n'+"<i>"+str(invoice_data["memo"])+'\n'+'\n'+"</i>"+"Hash: <code>"+invoice_data["hash"]+"</code>\n"+"Created at: "+ str(invoice_data["CreatedAt"])+'\n'+"Expires at: "+ str(invoice_data["ExpiresAt"])+'\n'+"Comment: "+comment+"\nPayee: <code>"+ invoice_data["payee"]+"</code>",
                            reply_markup=reply_markup,
                            reply_to_message_id=msg_id)
    del context.user_data["lnurl"]
    return ConversationHandler.END

lnurl_conv_handler = ConversationHandler(
    entry_points=[MessageHandler((Filters.regex(r'^lnurl|LNURL')& Filters.chat_type.private), read_lnurl),LNURLQR(read_lnurl)],
    states={
        AMOUNT: [MessageHandler(Filters.regex('[0-9]+'), amount_lnurl)],
        COMMENT:[MessageHandler(~Filters.command, comment_lnurl)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)