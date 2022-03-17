from telegram import *
from telegram.ext import *
from notify import notify
def enable_notifications (update: Update, context: CallbackContext):
    if "token" in context.user_data:
        chat_id = update.message.chat_id
        if not context.job_queue.get_jobs_by_name("notification"):
            context.job_queue.run_repeating(notify, 15*60,first=0,context=chat_id, name="notification")
            update.message.reply_text("Notifications Enabled successfully!")
        else: 
            update.message.reply_text("Notifications Enabled already!")
    else: 
        update.message.reply_text("You don't have an account. Sign up or Login first.")    

def disable_notifications (update: Update, context: CallbackContext):
    if "token" in context.user_data:
        chat_id = update.message.chat_id
        jobs= context.job_queue.get_jobs_by_name("notification")
        for job in jobs:
            job.schedule_removal()
        text = 'Notifications disabled successfully!'
        update.message.reply_text(text)
    else:
        update.message.reply_text("You don't have an account. Sign up or Login first.")

    
