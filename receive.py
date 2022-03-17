from API import *
from telegram import *
from telegram.ext import *
import logging
import qrcode
from PIL import Image
import datetime
import os
import sys
logger = logging.getLogger(__name__)

def receive (update: Update, context: CallbackContext):
    if "token" in context.user_data:
        if (len(context.args)>0):
            network=context.args[0].lower()
            address=get_address (context.user_data["username"],context.user_data["password"],network, type="bech32")
            update.message.reply_html(f"{network.capitalize()} Address: <code>{address}</code>", reply_to_message_id=update.effective_message.message_id)

        else:
            bitcoin_address=get_address (context.user_data["username"],context.user_data["password"],"bitcoin", type="bech32")
            liquid_address=get_address (context.user_data["username"],context.user_data["password"],"liquid", type="bech32")
            update.message.reply_html(f"Bitcoin Address: <code>{bitcoin_address}</code>\nLiquid Address: <code>{liquid_address}</code>", reply_to_message_id=update.effective_message.message_id)
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")
        
def invoice (update: Update, context: CallbackContext):
    if "token" in context.user_data:
        if (len(context.args)>1):
            invoice=(get_lightning_invoice(context.user_data["username"],context.user_data["token"], int(context.args[0]),context.args[1]))
        else:
            invoice=(get_lightning_invoice(context.user_data["username"],context.user_data["token"], int(context.args[0]),""))
        filename="qr/"+update.effective_user.username+"_invoice_"+context.args[0]+"_"+str(datetime.datetime.now().timestamp())+".png"
        qr=qrcode.make(invoice)
        qr.save(filename)
        image = Image.open(filename)
        new_image = image.resize((240, 240))
        new_image.save(filename)
        context.bot.send_photo(update.effective_chat.id, open(filename,'rb'), caption="<code>"+invoice+"</code>", parse_mode="html")
        os.remove(filename)
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")
