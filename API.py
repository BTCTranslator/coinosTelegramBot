import requests
import json
from datetime import datetime
from functions import *
from bech32 import bech32_decode, convertbits
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
api=config["Default"]["APIURL"]

def get_token(username, password):
    data={"username": username, "password": password, "account_id":29374}
    response = requests.post(api+"/taboggan", json=data)
    if (response.status_code==200):
        return response.json()["token"]
    return "ERROR"

def headers(token="token"):
    headers = {
    'Content-type': 'application/json',
    'Authorization': 'Bearer '+token
    }
    return headers

def get_address (username, password,network, type="bech32"):
    params= {"network": network, "type": type}
    token=get_token(username, password)
    response = requests.get(api+"/address", headers=headers(token), params=params)
    if (network=="liquid"):
        address=response.json()["confidentialAddress"]
    elif (network=="bitcoin"):
        address=response.json()["address"]
    data={"invoice": {"address": address, "network": network}, "user": {"username": username}}
    invoice = requests.post(api+"/invoice", headers=headers(token), json=data)
    if (invoice.status_code==200):
        return address
    return "ERROR"

def get_lightning_invoice (username,token,amount,memo):
    data={"amount": amount, "memo": memo}
    response = requests.post(api+"/lightning/invoice", headers=headers(token), json=data).text
    data= {"invoice": {"text": response, "network": "bitcoin"}, "user": {"username": username}}
    invoice = requests.post(api+"/invoice", headers=headers(token), json=data)
    return invoice.json()["text"]

def payments(username,password):
    original_account_id=get_active_account_id(username, password)
    acc_list=get_accounts(username,password)
    token=get_token(username, password)
    payments=[]
    for acc in acc_list:
        switch_account(token, acc["id"])
        response = requests.get(api+"/payments", headers=headers(token))
        if (response.status_code==200):
            acc_payments=response.json()
            payments.append(acc_payments)
        else:
            return "ERROR"
    payments = [item for sublist in payments for item in sublist]
    return payments

def checktx(username, password,address=None, preimage=None, hash=None, amount=0):
    history=payments(username, password)
    if (address!=None and amount!=0):
        mytx=[x for x in history if x["address"]==address]
        if (mytx and mytx[0]["amount"]==amount):
            return True
        return False
    elif (preimage!=None and amount!=0):
        mytx=[x for x in history if x["preimage"]==preimage]
        if (mytx and mytx[0]["amount"]==amount):
            return True
        return False
    elif (hash!=None and amount!=0):
        mytx=[x for x in history if x["hash"]==hash]
        if (mytx and mytx[0]["amount"]==amount):
            return True
        return False
    else:
        return False

def get_tx(txid,username,password):
    history=payments(username,password)
    mytx=[x for x in history if x["id"]==int(txid)]
    if mytx==[]:
        return -1
    return mytx[0]

def send (network, amount, address, token,asset="6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d",feeRate=100):
    if (network=="bitcoin"):
        data ={"address": address, "amount": int(amount), "feeRate": feeRate }
        response1 = requests.post(api+"/bitcoin/fee", headers=headers(token), json=data)
        try:
            response1=response1.json()
        except:
            return response1
        data ={"address": address,"tx":{"hex":response1["tx"]["hex"], "fee":response1["tx"]["fee"]}}
        response2 = requests.post(api+"/bitcoin/send", headers=headers(token), json=data)
        return response2
    elif (network=="liquid"):
        data ={"address": address, "amount": int(amount), "feeRate": int(feeRate) ,"asset": asset}
        response1 = requests.post(api+"/liquid/fee", headers=headers(token), json=data)
        try:
            response1=response1.json()
        except:
            return response1
        
        data ={"address": address,"tx":{"hex":response1["tx"]["hex"], "fee":response1["tx"]["fee"]}}
        response2 = requests.post(api+"/liquid/send", headers=headers(token), json=data)
        return response2
    elif (network=="lightning"):
        data ={"payreq": address, "amount": amount}
        response = requests.post(api+"/lightning/send", headers=headers(token), json=data)
        return response.text
    elif (network=="internal"):
        data={"username": address, "amount": amount , "asset": asset}
        response = requests.post(api+"/send", headers=headers(token), json=data)
        return response.text
    else:
        return -1

def get_server_balances():
    response = requests.get(api+"/balances", headers={'Content-type': 'application/json', 'Cache-control': 'no-cache'})
    return response.json()


def get_account(token):
    response = requests.get(api+"/me", headers=headers(token))
    if (response.status_code==200):
        return response.json()["account"]
    return "ERROR"

def create_account(username, password):
    data={"user": {"username": username, "password": password, "confirm": password}}
    response = requests.post(api+"/register", headers=headers(), json=data)
    if (response.status_code==200):
        return response.json()
    return "ERROR"

def get_accounts(username, password):
    data={"username": username, "password": password}
    response = requests.post(api+"/taboggan", json=data)
    return response.json()["user"]["accounts"]

def get_active_account_id(username, password):
    data={"username": username, "password": password}
    response = requests.post(api+"/taboggan", json=data)
    return response.json()["user"]["account_id"]



def switch_account(token,new_account_id):
    data={"id": new_account_id}
    response = requests.post(api+"/shiftAccount",headers=headers(token) ,json=data)
    return response.text



def get_balance(username, password):
    token=get_token(username, password)
    balances= get_accounts(username, password)
    ret={}
    for i in balances:
        ret[i["ticker"]]={"balance":i["balance"], "name":i["name"], "asset":i["asset"], "precision": i["precision"]}
    return ret


def get_price ():
    response = requests.get(api+"/rates", headers=headers())
    if (response.status_code==200):
        return response.json()
    return "ERROR"

def get_user (token):
    response = requests.get(api+"/me", headers=headers(token))
    if (response.status_code==200):
        return response.json()
    return "ERROR"


def new_incoming_payments(username,password,last_notification):
    incoming=[]
    new=[]
    
    history=payments(username,password)
    for tx in history:
        if tx["amount"]>0:
            incoming.append(tx)
    
    for tx in incoming:
        timestamp=coinos_time_to_timestamp(tx["updatedAt"])
        if timestamp>last_notification:
            new.append(tx)
    return new


def lnurl(bech32lnurl):
    hrp, datapart=bech32_decode(bech32lnurl)
    array=convertbits(datapart, 5,8)
    if (array[-1]==0):
        b = bytes(array)[:-1]
    else:
        b = bytes(array)

    return b.decode("utf-8")

def get_lnurl_info(url:str):
    try:
        response=requests.get(url, headers=headers(""))
        return response.json()
    except Exception as err:
        return err

def get_external_invoice(url,amount,comment=""):
    try:
        response=requests.get(url, headers=headers(""), params={"amount":amount, "comment":comment})
        return response.json()
    except Exception as err:
        return err

def create_arbitrary_account():
    letters = string.ascii_lowercase
    result="ERROR"
    while (result=="ERROR"):
        username="ctb-"+''.join(random.choice(letters) for i in range(17))
        password=''.join(random.choice(letters) for i in range(20))
        result=create_account(username,password)
    return (username, password)