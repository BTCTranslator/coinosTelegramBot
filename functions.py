from telegram import *
from telegram.ext import *
import time
import re
from ptbcontrib.username_to_chat_api import UsernameToChatAPI
from datetime import datetime
import bolt11
import configparser
import random
import string
from functools import wraps
config = configparser.ConfigParser()
config.read('config.ini')
BOT_TOKEN=config["Default"]["BOTTOKEN"]
U2C_SERVER=config["UsernameToChatAPI"]["SERVER"]
U2C_KEY=config["UsernameToChatAPI"]["KEY"]

def username_to_userid(username:str):
    bot = Bot(BOT_TOKEN)
    wrapper = UsernameToChatAPI(U2C_SERVER, U2C_KEY, bot)
    try:
        chat = wrapper.resolve(username)
    except:
        return "ERROR"
    return (chat)

def username_to_coinos_username (username: str, dispatcher: Dispatcher):
    return dispatcher.user_data[username_to_userid(username)["id"]]["username"]

def check_email(email):
    if(re.fullmatch("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", email)):
        return True
    else:
        return False

def base64_to_png(img_data, filename_to_save):
    with open(filename_to_save, "wb") as fh:
        fh.write(base64.decodebytes(bytes(img_data,"utf-8")))

def lnaddr_to_lnurl (lnaddr):
    if check_email(lnaddr):
        user, service=lnaddr.split('@')
        return f"https://{service}/.well-known/lnurlp/{user}"
    else:
        return -1

def read_ln_invoice(invoice):
    invoice=bolt11.decode(invoice)
    if invoice.amount is None:
        amount = -1000   
    else:
        amount=invoice.amount
    if "d" in invoice.tags and "x" in invoice.tags:
        invoice_data={
        "amount":amount/1000,
        "hash":invoice.tags["p"],
        "payee":invoice.payee_public_key,
        "memo":invoice.tags["d"],
        "CreatedAt":str(datetime.fromtimestamp(invoice.timestamp)),
        "ExpiresAt":str(datetime.fromtimestamp(invoice.tags["x"]+invoice.timestamp))}
    elif "d" in invoice.tags and "x" not in invoice.tags:
        invoice_data={
        "amount":amount/1000,
        "hash":invoice.tags["p"],
        "payee":invoice.payee_public_key,
        "memo":invoice.tags["d"],
        "CreatedAt":datetime.fromtimestamp(invoice.timestamp),
        "ExpiresAt":None}
    elif "d" not in invoice.tags and "x" in invoice.tags:
        invoice_data={
        "amount":amount/1000,
        "hash":invoice.tags["p"],
        "payee":invoice.payee_public_key,
        "memo":"",
        "CreatedAt":datetime.fromtimestamp(invoice.timestamp),
        "ExpiresAt":datetime.fromtimestamp(invoice.tags["x"]+invoice.timestamp)}
    else: 
        invoice_data={
        "amount":amount/1000,
        "hash":invoice.tags["p"],
        "payee":invoice.payee_public_key,
        "memo": "",
        "CreatedAt":datetime.fromtimestamp(invoice.timestamp),
        "ExpiresAt":None}
    return invoice_data

def coinos_time_to_timestamp(coinos_time):
    timestamp=time.mktime(datetime.strptime(coinos_time, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())
    return timestamp

def human_time (timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def tx_time(tx):
    return coinos_time_to_timestamp(tx["updatedAt"])

def is_bitcoin_address(address):
    regex = r"^(bitcoin:)?(bc1p|bc1q|[13])[a-zA-HJ-NP-Z0-9]{24,38}(\?amount=.)?"
    result = re.search(regex, address, re.MULTILINE)
    if result is None:
        return False
    if len(result.groups())>0:
        if result.start(1) == 0 and result.end(1) == 8:
            prefixed = True
        else:
            prefixed = False
        
        if (prefixed == True and result.group(2)=="1") or (prefixed == False and result.group(2)=="1"):
            type="P2PKH"
        elif (prefixed == True and result.group(2)=="bc1q") or (prefixed == False and result.group(2)=="bc1q"):
            type="Bech32"
        elif (prefixed == True and result.group(2)=="bc1p") or (prefixed == False and result.group(2)=="bc1p"):
            type="Bech32m"
        elif (prefixed == True and result.group(2)=="3") or (prefixed == False and result.group(2)=="3"):
            type="P2SH"
        
        if result.group(3) is not None:
            amounted= True
        else:
            amounted= False
        #return (type, address)
        #return result.group(3)
        
        if (prefixed==True): address= address[8:]
        if (amounted==True): address=address[:address.index("?amount")]
        return (type, address)
    else:
        return False


def run_usernameToChat_server():
    pid = os.fork()
    
    if pid > 0 :
        print("I am parent process:")
        print("Process ID:", os.getpid())
        print("Child's process ID:", pid)

    else :
        print("\nI am child process:")
        print("Process ID:", os.getpid())
        print("Parent's process ID:", os.getppid())

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator
