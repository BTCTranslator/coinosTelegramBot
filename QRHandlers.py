from telegram.ext import *
from telegram import *
import json
from PIL import Image
from pyzbar import pyzbar
import os
from functions import *

class LNQR(Handler):
    def check_update(self, update):
        if (update.effective_message.photo and update.effective_chat.type=="private"):
            newFile = update.effective_message.effective_attachment[1].get_file()
            file_id = update.effective_message.effective_attachment[1].file_id
            lst=[]
            cached=False
            data=""
            with open('sample.json', 'r') as openfile:   
                json_object = json.load(openfile)
                lst=json_object
            for obj in json_object:
                if obj[0] == file_id:
                    data=data
                    cached=True
            if data=="":
                newFile.download("qr/"+file_id)
                image = Image.open("qr/"+file_id)
                try:
                    qr_code = pyzbar.decode(image)[0]
                except:
                    update.message.reply_text("Error parsing QR code.")
                else:
                    data= qr_code.data.decode("utf-8")                
            if (data.lower()[:4]=="lnbc"):
                if (not cached):
                    tup =(file_id,data)
                    lst.append(tup)
                    if len(lst) > 10:
                        if os.path.exists("qr/"+lst[0][0]):
                            os.remove("qr/"+lst[0][0])
                        lst=lst[-10:]
                    with open("sample.json", "w") as outfile:
                        json.dump(lst, outfile)
                return True
            else:
                return False
        return False


class LiquidQR(Handler):
    def check_update(self, update):
        if (update.effective_message.photo  and update.effective_chat.type=="private"):
            newFile = update.effective_message.effective_attachment[1].get_file()
            file_id = update.effective_message.effective_attachment[1].file_id
            lst=[]
            data=""
            cached=False
            with open('sample.json', 'r') as openfile:   
                json_object = json.load(openfile)
                lst=json_object
            for obj in json_object:
                if obj[0] == file_id:
                    data=data
                    cached=True
            if data=="":
                newFile.download("qr/"+file_id)
                image = Image.open("qr/"+file_id)
                try:
                    qr_code = pyzbar.decode(image)[0]
                except:
                    update.message.reply_text("Error parsing QR code.")
                else:
                    data= qr_code.data.decode("utf-8")                
            if (data.lower()[0]=="v" and len(data.lower())==80):
                if (not cached):
                    tup =(file_id,data)
                    lst.append(tup)
                    if len(lst) > 10:
                        if os.path.exists("qr/"+lst[0][0]):
                            os.remove("qr/"+lst[0][0])
                        lst=lst[-10:]
                    with open("sample.json", "w") as outfile:
                        json.dump(lst, outfile)
                return True
            else:
                return False
        return False




class BitcoinQR(Handler):
    def check_update(self, update):
        if (update.effective_message.photo  and update.effective_chat.type=="private"):
            newFile = update.effective_message.effective_attachment[1].get_file()
            file_id = update.effective_message.effective_attachment[1].file_id
            lst=[]
            data=""
            cached=False
            with open('sample.json', 'r') as openfile:   
                json_object = json.load(openfile)
                lst=json_object
            for obj in json_object:
                if obj[0] == file_id:
                    data=data
                    cached=True
            if data=="":
                newFile.download("qr/"+file_id)
                image = Image.open("qr/"+file_id)
                try:
                    qr_code = pyzbar.decode(image)[0]
                except:
                    update.message.reply_text("Error parsing QR code.")
                else:
                    data= qr_code.data.decode("utf-8")

            if (is_bitcoin_address(data.lower())!=False):
                data=is_bitcoin_address(data.lower())[1]
                if (not cached):
                    tup =(file_id,data)
                    lst.append(tup)
                    if len(lst) > 10:
                        if os.path.exists("qr/"+lst[0][0]):
                            os.remove("qr/"+lst[0][0])
                        lst=lst[-10:]
                    with open("sample.json", "w") as outfile:
                        json.dump(lst, outfile)
                return True
            else:
                return False
        return False





class LNURLQR(Handler):
    def check_update(self, update):
        if (update.effective_message.photo and update.effective_chat.type=="private"):
            newFile = update.effective_message.effective_attachment[1].get_file()
            file_id = update.effective_message.effective_attachment[1].file_id
            lst=[]
            data=""
            cached=False
            with open('sample.json', 'r') as openfile:   
                json_object = json.load(openfile)
                lst=json_object
            for obj in json_object:
                if obj[0] == file_id:
                    data=data
                    cached=True
            if data=="":
                newFile.download("qr/"+file_id)
                image = Image.open("qr/"+file_id)
                try:
                    qr_code = pyzbar.decode(image)[0]
                except:
                    update.message.reply_text("Error parsing QR code.")
                else:
                    data= qr_code.data.decode("utf-8")                
            if (data.lower()[:5]=="lnurl"):
                if (not cached):
                    tup =(file_id,data)
                    lst.append(tup)
                    if len(lst) > 10:
                        if os.path.exists("qr/"+lst[0][0]):
                            os.remove("qr/"+lst[0][0])
                        lst=lst[-10:]
                    with open("sample.json", "w") as outfile:
                        json.dump(lst, outfile)
                return True
            else:
                return False
        return False
