from API import *
from telegram import *
from telegram.ext import *
import logging
from QRHandlers import *
from common import *
logger = logging.getLogger(__name__)
AMOUNT=1
def read_invoice(update: Update, context: CallbackContext):
    if "token" in context.user_data:
        context.user_data["invoice"]={}
        if(update.effective_message.photo):
            file_id = update.effective_message.effective_attachment[1].file_id
            with open('sample.json', 'r') as openfile:   
                json_object = json.load(openfile)
            for obj in json_object:
                if obj[0] == file_id:
                    invoice_data=read_ln_invoice(obj[1])
                    context.user_data["invoice"]["text"]=obj[1]
        
        elif(update.effective_message.text):
            invoice_data=read_ln_invoice(update.effective_message.text)
            context.user_data["invoice"]["text"]=update.effective_message.text
        context.user_data["invoice"]["data"]=invoice_data
        if invoice_data["amount"] != -1:
            context.user_data["invoice"]["amount"]=invoice_data["amount"]
            keyboard = [[
                        InlineKeyboardButton("Cancel", callback_data='cancel'),
                        InlineKeyboardButton("Pay", callback_data="pay")
                    ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_html(str(invoice_data["amount"])+" sat"+'\n'+"<i>"+str(invoice_data["memo"])+'\n'+'\n'+"</i>"+"Hash: <code>"+invoice_data["hash"]+"</code>\n"+"Created at: "+ str(invoice_data["CreatedAt"])+'\n'+"Expires at: "+ str(invoice_data["ExpiresAt"])+'\n'+"Payee: <code>"+ invoice_data["payee"]+"</code>",
                                    reply_markup=reply_markup)
            return ConversationHandler.END
        else:
            update.message.reply_html("Reply with the desired amount to confirm.")
            
            return AMOUNT
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")
        return CoversationHandler.END
def amount_ln (update: Update, context: CallbackContext):
    amount=update.effective_message.text
    context.user_data["invoice"]["amount"]=int(amount)
    invoice_data=context.user_data["invoice"]["data"]
    del context.user_data["invoice"]["data"]
    keyboard = [[
                    InlineKeyboardButton("Cancel", callback_data='cancel'),
                    InlineKeyboardButton("Pay", callback_data="pay")
                ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_html(str(amount)+" sat"+'\n'+"<i>"+str(invoice_data["memo"])+'\n'+'\n'+"</i>"+"Hash: <code>"+invoice_data["hash"]+"</code>\n"+"Created at: "+ str(invoice_data["CreatedAt"])+'\n'+"Expires at: "+ str(invoice_data["ExpiresAt"])+'\n'+"Payee: <code>"+ invoice_data["payee"]+"</code>",
                                reply_markup=reply_markup)
    return ConversationHandler.END


ln_conv_handler = ConversationHandler(
    entry_points=[MessageHandler((Filters.regex(r'^lnbc|LNBC') & Filters.chat_type.private), read_invoice),LNQR(read_invoice)],
    states={
        AMOUNT: [MessageHandler(Filters.regex('[0-9]+'), amount_ln)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)