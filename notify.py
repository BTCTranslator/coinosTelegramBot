from API import *
from telegram import *
from telegram.ext import *
def notify(context: CallbackContext):
    job=context.job
    if "last_notification" in context.dispatcher.user_data[job.context]:
        new=new_incoming_payments(context.dispatcher.user_data[job.context]["username"], context.dispatcher.user_data[job.context]["password"], context.dispatcher.user_data[job.context]["last_notification"])
    else:
        new=new_incoming_payments(context.dispatcher.user_data[job.context]["username"], context.dispatcher.user_data[job.context]["password"],0)
    
    if new!=[]:
        for tx in new[::-1]:
            tx_info=f"New payment received: {tx['amount']/10**tx['account']['precision']:.8f} {tx['account']['ticker']} /tx_{tx['id']}"
            context.bot.send_message(chat_id=job.context, text=tx_info)
        context.dispatcher.user_data[job.context]["last_notification"]=coinos_time_to_timestamp(new[0]["updatedAt"])
