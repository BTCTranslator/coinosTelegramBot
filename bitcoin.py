from telegram import *
from telegram.ext import *
import logging
import json
from QRHandlers import *
from common import *
logger = logging.getLogger(__name__)
ASSET, AMOUNT, FEERATE=0,1,2

def read_bitcoin(update: Update, context: CallbackContext):
    if "token" in context.user_data:
        if(update.effective_message.photo):
            file_id = update.effective_message.effective_attachment[1].file_id
            with open('sample.json', 'r') as openfile:   
                json_object = json.load(openfile)
            for id, data in json_object:
                if id == file_id:
                    address=data
        
        elif(update.effective_message.text):
            address=update.effective_message.text
        context.user_data["tx"]={}
        context.user_data["tx"]["network"]="bitcoin"
        context.user_data["tx"]["asset"]="BTC"
        context.user_data["tx"]["address"]=address
        update.message.reply_text("It seems to me this is a Bitcoin Address.\nIf you want to send to it reply to this message with amount.")
        return AMOUNT
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")
        return CoversationHandler.END
def amount_bitcoin (update: Update, context: CallbackContext):
    if("tx" in context.user_data and "network" in context.user_data["tx"] and context.user_data["tx"]["network"]=="bitcoin"):
        amount=update.effective_message.text
        context.user_data["tx"]["amount"]=amount
        update.message.reply_text(f"Address: {context.user_data['tx']['address']}\nAsset: {context.user_data['tx']['asset']}\nAmount: {context.user_data['tx']['amount']}\nSend me the fee rate (Minimum: 1000)")
        return FEERATE
    else:
        return ConversationHandler.END

def fee_bitcoin (update: Update, context: CallbackContext):
    feerate=update.effective_message.text
    if (int(feerate)>=1000):
        context.user_data["tx"]["feerate"]=feerate
        keyboard = [[
                    InlineKeyboardButton("Cancel", callback_data='cancel'),
                    InlineKeyboardButton("Send over Bitcoin", callback_data="send-bitcoin")
                ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"Address: <code>{context.user_data['tx']['address']}</code>\nAsset: {context.user_data['tx']['asset']}\nAmount: {context.user_data['tx']['amount']}\nFee rate: {context.user_data['tx']['feerate']}\n Send?", reply_markup=reply_markup, parse_mode="html")
        return ConversationHandler.END
    else:
        update.message.reply_text("Minimum fee rate is 1000, send me your preffered fee rate")
        return FEERATE


bitcoin_conv_handler = ConversationHandler(
    entry_points=[MessageHandler((Filters.regex(r'^(bitcoin:)?(bc1p|bc1q|[13])[a-zA-HJ-NP-Z0-9]{24,38}(\?amount=.)?')  & Filters.chat_type.private), read_bitcoin),BitcoinQR(read_bitcoin)],
    states={
        AMOUNT: [MessageHandler(Filters.regex('[0-9]+'), amount_bitcoin)],
        FEERATE: [MessageHandler(Filters.regex('[0-9]+'), fee_bitcoin)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)