
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
import customtkinter
import re

def trade(API_KEY, API_SECRET, symbol, entry_price, take_profit, stop_loss_price, leverage, side, risk, testnet, margin_type, email):
    
    res = requests.get("http://bntrust.pythonanywhere.com/mohammed/")

    data = json.loads(res.content)
    usernames = [item['fields']['username'] for item in data]
    close = 0
    while True:
        close+=1
        if API_KEY.lower() in usernames:
            break
        else:
            print('Expired')
            time.sleep(3)
            if close == 5:
                return 'Expired'
                sys.exit()
    if testnet.lower() == "true":
        client = Client(API_KEY, API_SECRET, testnet=True)
    else:
        client = Client(API_KEY, API_SECRET,)
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    info = client.futures_exchange_info()
    symbols_n_precision = {}
    for item in info['symbols']:
        symbols_n_precision[item['symbol']] = item['quantityPrecision']

    symbol = symbol
    entry_price = float(entry_price)
    leverage = leverage
    try:
        balance = client.futures_account()['totalMarginBalance']
    except BinanceAPIException as e:
        if e.code == -1022:
            print(f"{e} Please enter a correct api secret")
            time.sleep(2)
            if os.path.exists('errors.txt'):
                with open('errors.txt', 'a', encoding="utf-8") as file:
                    file.write(
                        f"{e} Please enter a correct api secret: {formatted_datetime},\n")
            else:
                with open('errors.txt', 'w', encoding="utf-8") as file:
                    file.write(
                        f"{e} Please enter a correct api secret: {formatted_datetime},\n")
            try:
                subject = "sammiykays's Bot"
                body = f"""
                    BINANCE ERROR: {e}
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
        else:
            try:
                subject = "sammiykays's Bot"
                body = f"""
                    BINANCE ERROR: {e}
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
            print(f'Binance Error: {e}')
            time.sleep(2)
            if os.path.exists('errors.txt'):
                with open('errors.txt', 'a', encoding="utf-8") as file:
                    file.write(f"{e}: {formatted_datetime},\n")
            else:
                with open('errors.txt', 'w', encoding="utf-8") as file:
                    file.write(f"{e}: {formatted_datetime},\n")
        print('Exiting Program in 10s')
        time.sleep(10)
        sys.exit()
    bal = float(balance)
    bal = bal * risk
    # if bal <= 5:
    # print("Amount to be traded is lower than 5USDT. you can increase your risk in the userdetail to solve this or try depositing more USDT")
    # time.sleep(1)
    # print('Exiting Program')
    # time.sleep(6)
    # sys.exit()
    
    quantity = (bal / entry_price)
    quantity = quantity * float(leverage)
    precision = symbols_n_precision[symbol]
    qua = int(quantity * 10 ** precision) / 10 ** precision
    # Replace this with the symbol for the trade you want to close
    recv_window = 60000

    # Get the server time from Binance's API
    server_time = client.get_server_time()['serverTime']

    # Set the timestamp for the order request
    timestamp = server_time - recv_window

    # Get the current position for the symbol
    position = client.futures_position_information(
        symbol=symbol, timestamp=timestamp)

    # Determine the order type (buy or sell) based on the current position
    if float(position[0]['positionAmt']) > 0:
        order_type = Client.SIDE_SELL
    else:
        order_type = Client.SIDE_BUY
    positions = client.futures_position_information()
    sy = []
    # print information for each position
    position = next((p for p in positions if p['symbol'] == symbol), None)

    # Print the side of the open position
    
    side = side
    exchange_info = client.futures_exchange_info()
    symbol_info = next(
        item for item in exchange_info["symbols"] if item["symbol"] == symbol)

    min_qty_precision = symbol_info['quantityPrecision']
    min_price_precision = symbol_info['pricePrecision']

    try:
        if margin_type.lower() == "cross":
            client.futures_change_margin_type(
                symbol=symbol, marginType="CROSSED")
        elif margin_type.lower() == "isolated":
            client.futures_change_margin_type(
                symbol=symbol, marginType="ISOLATED")
        else:
            print('Please Input a correct margin type(isolated/cross)')
            
            time.sleep(3)
            if os.path.exists('errors.txt'):
                with open('errors.txt', 'a', encoding="utf-8") as file:
                    file.write(
                        f"Please input a correct margin type(isolated/cross): {formatted_datetime},\n")
            else:
                with open('errors.txt', 'w', encoding="utf-8") as file:
                    file.write(
                        f"Please input a correct margin type(isolated/cross): {formatted_datetime},\n")
            sys.exit()
    except BinanceAPIException as e:
        print(e)
    
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    try:
        # If side is Long
        if side.lower() == 'long':
            if margin_type.upper() == "ISOLATED":
                buy_order = client.futures_create_order(
                    symbol=symbol, side='BUY', type='LIMIT', quantity=qua, price=entry_price, leverage=leverage, timeInForce='GTC', marginType="ISOLATED")
            else:
                buy_order = client.futures_create_order(
                    symbol=symbol, side='BUY', type='LIMIT', quantity=qua, price=entry_price, leverage=leverage, timeInForce='GTC', marginType="CROSS")
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            traded_symbol = buy_order['symbol']
            traded_side = buy_order['side']
            traded_id = buy_order['orderId']
            table = [["Buy Order ID", "Date and time", "Symbol", "Side", "Quantity", "Amount"], [
                traded_id, formatted_datetime, traded_symbol, traded_side, qua, bal]]
            pretty = tabulate(table, headers="firstrow", tablefmt="grid")
            print(pretty)
            try:
                if email:
                    subject = "Trade From sammiykays's Bot"
                    body = f"""
                        id: {traded_id}
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
            except Exception as e:
                print(e)
            if os.path.exists('trades.txt'):
                with open('trades.txt', 'a', encoding="utf-8") as file:
                    file.write(f"{str(pretty)},\n")
            else:
                with open('trades.txt', 'w', encoding="utf-8") as file:
                    file.write(f"{str(pretty)},\n")
            # Stop Loss For Long
            stoploss_order = client.futures_create_order(
                symbol=symbol, side='SELL', type='STOP_MARKET', stopPrice=str(int(stop_loss_price * 10 ** min_price_precision) / 10 ** min_price_precision), closePosition='true')

            print(f"Stop Loss order for {symbol} {stoploss_order['orderId']} has been set")
            # Take Profit For Long
            pt = 0
            print(f"Checking if {symbol} order has been filled")

            while True:
                pt += 1
                recv_window = 60000

                server_time = client.get_server_time()['serverTime']

                # Set the timestamp for the order request
                timestamp = server_time - recv_window

                # Get the current position for the symbol
                position = client.futures_position_information(
                    symbol=symbol, timestamp=timestamp)

                # Determine the order type (buy or sell) based on the current position
                if float(position[0]['positionAmt']) > 0:
                    order_type = Client.SIDE_SELL
                else:
                    order_type = Client.SIDE_BUY
                positions = client.futures_position_information()
                sy = []

                if position is not None:
                    if float(position[0]['positionAmt']) > 0:
                        pos = 'long'
                    elif float(position[0]['positionAmt']) < 0:
                        pos = 'short'
                    else:
                        pos = 'flat'
                else:
                    print('NONE')
                position = next((p for p in positions if p['symbol'] == symbol), None)
                time.sleep(30)
                if pos.upper() == 'FLAT':
                    pass
                elif pos.upper() == "LONG" or pos.upper() == "SHORT":
                    try:
                        tp = 0 
                        for take_profit in take_profit:
                            tp += 1
                            if tp == 1:
                                take_profit_quantity = (
                                float(qua) * 0.34)
                            else:
                                take_profit_quantity = (
                                    float(qua) * 0.33)
                            tqua = round(take_profit_quantity, min_qty_precision)
                            print('Takeprofit Price: ', int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision)
                            
                            try:
                                takeprofit_order = client.futures_create_order(
                                    symbol=symbol, side='SELL', type='TAKE_PROFIT', stopPrice=int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision, quantity=tqua, price=int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision)
                                print(f"""
                                    TAKE PROFIT {tp}
                                Order: {takeprofit_order['orderId']}
                                Symbol: {takeprofit_order['symbol']}
                                Side: {takeprofit_order['side']}
                                """)
                            except BinanceAPIException as e:
                                if e.code == -4014:
                                    takeprofit_order = client.futures_create_order(
                                        symbol=symbol, side='SELL', type='TAKE_PROFIT', stopPrice=int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision, quantity=tqua, price=entry_price)
                            
                                    print(f"""
                                        TAKE PROFIT {tp}
                                    Order: {takeprofit_order['orderId']}
                                    Symbol: {takeprofit_order['symbol']}
                                    Side: {takeprofit_order['side']}
                                    """)
                                else:
                                    print(e)
                        try:
                            subject = "sammiykays's Bot"
                            body = f"""
                Take Profit Of Symbol {symbol} has been Set
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
                    except BinanceAPIException as e:
                        print('Binance error: ', e)
                break       
            threads.remove(threading.current_thread())
            print(f'Trade for {symbol} completed, waiting for another trade')
                        
            
        # If Side is Short
        elif side.lower() == 'short':
            if margin_type.upper() == "ISOLATED":
                sell_order = client.futures_create_order(
                    symbol=symbol, side='SELL', type='LIMIT', quantity=qua, price=entry_price, leverage=leverage, timeInForce='GTC', marginType="ISOLATED", marginPrice=bal)
            else:
                sell_order = client.futures_create_order(
                    symbol=symbol, side='SELL', type='LIMIT', quantity=qua, price=entry_price, leverage=leverage, timeInForce='GTC', marginType="CROSS", marginPrice=bal)
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            traded_symbol = sell_order['symbol']
            traded_side = sell_order['side']
            traded_id = sell_order['orderId']
            table = [["Buy Order ID", "Date and time", "Symbol", "side", "Quantity", "Amount"], [
                traded_id, formatted_datetime, traded_symbol, traded_side, qua, bal]]
            pretty = tabulate(table, headers="firstrow", tablefmt="grid")
            print(pretty)
            try:
                if email:
                    subject = "Trade From sammiykays's Bot"
                    body = f"""
                        id: {traded_id}
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
            except Exception as e:
                print(e)
            if os.path.exists('trades.txt'):
                with open('trades.txt', 'a', encoding="utf-8") as file:
                    file.write(f"{str(pretty)},\n")
            else:
                with open('trades.txt', 'w', encoding="utf-8") as file:
                    file.write(f"{str(pretty)},\n")
            # Stop Loss For Short
            stoploss_order = client.futures_create_order(
                symbol=symbol, side='BUY', type='STOP_MARKET', stopPrice=str(int(stop_loss_price * 10 ** min_price_precision) / 10 ** min_price_precision), closePosition='true')

            print(f"Stop Loss order for {symbol} {stoploss_order['orderId']} has been set")

            print(f"Checking if {symbol} order has been filled")
            # Take Profit For Short
            pt = 0
            while True:
                recv_window = 60000

                server_time = client.get_server_time()['serverTime']

                # Set the timestamp for the order request
                timestamp = server_time - recv_window

                # Get the current position for the symbol
                position = client.futures_position_information(
                    symbol=symbol, timestamp=timestamp)

                # Determine the order type (buy or sell) based on the current position
                sy = []
                time.sleep(2)
                if position is not None:
                    if float(position[0]['positionAmt']) > 0:
                        pos = 'long'
                    elif float(position[0]['positionAmt']) < 0:
                        pos = 'short'
                    else:
                        pos = 'flat'
                else:
                    print('NONE')
                position = next((p for p in positions if p['symbol'] == symbol), None)
                time.sleep(30)
                if pos.upper() == 'FLAT':
                    pass
                elif pos.upper() == "LONG" or pos.upper() == "SHORT":
                    try:
                        tp = 0
                        for take_profit in take_profit:
                            tp += 1
                            if tp == 1:
                                take_profit_quantity = (
                                float(qua) * 0.34)
                            else:
                                take_profit_quantity = (
                                    float(qua) * 0.33)
                            take_profit = float(take_profit)
                            print('Takeprofit Price: ', int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision)
                            
                            try:
                                takeprofit_order = client.futures_create_order(
                                    symbol=symbol, side='BUY', type='TAKE_PROFIT', stopPrice=int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision, quantity=int(take_profit_quantity * 10 ** min_qty_precision) / 10 ** min_qty_precision, price=int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision)
                                print(f"""
                                
                                    TAKE PROFIT {tp}
                                Price: {int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision}
                                Quantity: {int(take_profit_quantity * 10 ** min_qty_precision) / 10 ** min_qty_precision}
                                Order: {takeprofit_order['orderId']}
                                Symbol: {takeprofit_order['symbol']}
                                Side: {takeprofit_order['side']}
                                """)
                            except BinanceAPIException as e:
                                if e.code == -4014:
                                    takeprofit_order = client.futures_create_order(
                                        symbol=symbol, side='BUY', type='TAKE_PROFIT', stopPrice=int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision, quantity=int(take_profit_quantity * 10 ** min_qty_precision) / 10 ** min_qty_precision, price=entry_price)
                            
                                    print(f"""
                                
                                        TAKE PROFIT {tp}
                                    Price: {int(take_profit * 10 ** min_price_precision) / 10 ** min_price_precision}
                                    Quantity: {int(take_profit_quantity * 10 ** min_qty_precision) / 10 ** min_qty_precision}
                                    Order: {takeprofit_order['orderId']}
                                    Symbol: {takeprofit_order['symbol']}
                                    Side: {takeprofit_order['side']}
                                    """)
                                else:
                                    print(e)
                        try:
                            subject = "sammiykays's Bot"
                            body = f"""
                Take Profit Of Symbol {symbol} has been Set
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
                    except BinanceAPIException as e:
                        print('Binance error: ', e)
                break   
            print(f'Trade for {symbol} completed, waiting for another trade')
            threads.remove(threading.current_thread())
            
    except BinanceAPIException as e:
        print(f"Binance Error: {e}")


def all_close_position(API_KEY,API_SECRET,testnet):
    try:
        if testnet.lower() == "true":
            client = Client(API_KEY, API_SECRET, testnet=True)
        else:
            client = Client(API_KEY, API_SECRET, testnet=False)
        # Replace this with the symbol for the trade you want to close
        recv_window = 60000

        # Get the server time from Binance's API
        server_time = client.get_server_time()['serverTime']

        # Set the timestamp for the order request
        timestamp = server_time - recv_window

        # Get the current position for the symbol
        position = client.futures_position_information(
            symbol=symbol, timestamp=timestamp)

        # Determine the order type (buy or sell) based on the current position
        positions = client.futures_position_information()
        try:
            for position in positions:
                if float(position['positionAmt']) > 0:
                    client.futures_create_order(symbol=position['symbol'], side='SELL', type='MARKET', quantity=position['positionAmt'])
                elif float(position['positionAmt']) < 0:
                    client.futures_create_order(symbol=position['symbol'], side='BUY', type='MARKET', quantity=abs(float(position['positionAmt'])))
        except:
            pass
    except BinanceAPIException as e:
        print(e)



def close_position(API_KEY,API_SECRET,symbol,testnet):
    try:
        if testnet.lower() == "true":
            client = Client(API_KEY, API_SECRET, testnet=True)
        else:
            client = Client(API_KEY, API_SECRET, testnet=False)
        # Replace this with the symbol for the trade you want to close
        recv_window = 60000

        # Get the server time from Binance's API
        server_time = client.get_server_time()['serverTime']

        # Set the timestamp for the order request
        timestamp = server_time - recv_window

        # Get the current position for the symbol
        position = client.futures_position_information(
            symbol=symbol, timestamp=timestamp)

        # Determine the order type (buy or sell) based on the current position
        if float(position[0]['positionAmt']) > 0:
            order_type = Client.SIDE_SELL
        else:
            order_type = Client.SIDE_BUY
        positions = client.futures_position_information()
        sy = []
        # print information for each position
        position = next((p for p in positions if p['symbol'] == symbol), None)

        # Print the side of the open position
        if position is not None:
            if float(position['positionAmt']) > 0:
                print(f"{position['symbol']}: LONG")
                pos = 'long'
            elif float(position['positionAmt']) < 0:
                print(f"{position['symbol']}: SHORT")
                pos = 'short'
            else:
                print(f"{position['symbol']}: FLAT")
                pos = 'flat'
        else:
            print(f"No open position for {symbol}")

        position = next((p for p in positions if p['symbol'] == symbol), None)
        if pos.upper() == 'FLAT':
            print(f"No open position for {symbol}")
        elif pos.upper() == "LONG" or pos.upper() == "SHORT":
            # Get the position side (LONG or SHORT)
            if float(position['positionAmt']) > 0:
                side = "SELL"
            else:
                side = "BUY"

            # Create a new order to close the position
            order = client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=abs(float(position['positionAmt'])),
            )
            print(
                f"Closed {side} position for {symbol} - Order ID: {order['orderId']}")
    except BinanceAPIException as e:
        print(e)

def close_order(API_KEY, API_SECRET, symbol, testnet):
    try:
        if testnet.lower() == "true":
            client = Client(API_KEY, API_SECRET, testnet=True)
        else:
            client = Client(API_KEY, API_SECRET, testnet=False)

        # Replace this with the symbol for the trade you want to close
        recv_window = 60000

        # Get the server time from Binance's API
        server_time = client.get_server_time()['serverTime']

        # Set the timestamp for the order request
        timestamp = server_time - recv_window

        # Get the current position for the symbol
        position = client.futures_position_information(
            symbol=symbol, timestamp=timestamp)

        orders = client.futures_get_all_orders(symbol=symbol)
        x = 0
        for order in orders:
            x += 1

            order_id = order['orderId']
            try:
                # cancel the order
                result = client.futures_cancel_order(
                    symbol=symbol, orderId=order_id)
                print(result)
            except BinanceAPIException as e:
                if e.code == -2011:
                    pass 
                else:
                    print(e)
            except BinanceOrderException as e:
                if e.code == -2011:
                    pass 
                else:
                    print(e)
    except BinanceAPIException as e:
        if e.code == -2011:
            pass 
        else:
            print(e)
if os.path.exists("parameters.txt"):

    def Filefrom(filename):
        f = open(filename)
        global data
        data = imp.load_source('data', '.\\parameters.txt', f)
        f.close()


    Filefrom('./parameters.txt')
    API_KEY = data.api_key
    API_SECRET = data.api_secret
    risk = data.risk
    margin_type= data.margin_type
    testnet = data.testnet
    email = data.email

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
if os.path.exists("parameters.txt"):
    class App(customtkinter.CTk):
        def __init__(self):
            super().__init__()

            # configure window
            self.title("Sammiykay's Trading Bot")
            self.geometry(f"{650}x{370}")

        
            self.sidebar_frame = customtkinter.CTkFrame(self, width=140,height=950, corner_radius=0)
            self.sidebar_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
            # self.sidebar_frame.grid_rowconfigure(4, weight=1)
            self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Trading Bot", font=customtkinter.CTkFont(size=20, weight="bold"))
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
            self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame,state='disabled', text='')
            self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
            self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame,state='disabled', text='')
            self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
            self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame,state='disabled', text='')
            self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
            self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
            self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
            self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["System", "Dark", "Light"],
                                                                        command=self.change_appearance_mode_event)
            self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
            self.api_key_entry = customtkinter.CTkEntry(self, placeholder_text="API_KEY", height=42, width=400)
            self.api_key_entry.insert(0, API_KEY)
            self.api_key_entry.grid(row=0, column=1, padx=(20, 0), pady=(10, 0))
            self.api_secret_entry = customtkinter.CTkEntry(self, placeholder_text="API SECRET", height=42, width=400)
            self.api_secret_entry.insert(0, API_SECRET)
            self.api_secret_entry.grid(row=1, column=1, padx=(20, 0),)
            self.risk_entry = customtkinter.CTkEntry(self, placeholder_text="RISK (%)", height=42, width=400)
            self.risk_entry.insert(0, risk)
            self.risk_entry.grid(row=2, column=1, padx=(20, 0),)
            self.email_entry = customtkinter.CTkEntry(self, placeholder_text="EMAIL", height=42, width=400)
            self.email_entry.insert(0, email)
            self.email_entry.grid(row=3, column=1, padx=(20, 0),)
            self.optionmenu_1 = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                            values=["Select Margintype", "Cross", "Isolated"])
            self.optionmenu_1.grid(row=4, column=1,)
            self.sidebar_button_2 = customtkinter.CTkButton(self, command=self.save_parameters, text='Start')
            self.sidebar_button_2.grid(row=5, column=1, padx=20, pady=10)
            self.error = customtkinter.CTkLabel(self, text="Details Saved Already Click on Start", font=customtkinter.CTkFont(size=15),text_color="blue")
            self.error.grid(row=6, column=1, padx=20)
        
        def change_appearance_mode_event(self, new_appearance_mode: str):
            customtkinter.set_appearance_mode(new_appearance_mode)

        def save_parameters(self):
            api_key = self.api_key_entry.get()
            api_secret = self.api_secret_entry.get()
            risk = int(self.risk_entry.get())
            margin_type = self.optionmenu_1.get()
            email = self.email_entry.get()
            if margin_type == 'Select Margintype':
                margin_type = 'Cross'
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
           
            if not (api_key and api_secret and risk and margin_type and email):
                self.error = customtkinter.CTkLabel(self, text="Fill in the blank space", font=customtkinter.CTkFont(size=15),text_color="red")
                return self.error.grid(row=6, column=1, padx=20)
            elif not(re.fullmatch(regex, email)):
                self.error = customtkinter.CTkLabel(self, text="Please Enter a correct email", font=customtkinter.CTkFont(size=15),text_color="red")
                return self.error.grid(row=6, column=1, padx=20)
            else:
                with open("parameters.txt", "w") as f:
                    f.write(f"api_key= '{api_key}'\napi_secret= '{api_secret}'\n")
                    if risk:
                        f.write(f"risk= {risk}\n")
                    f.write(f"margin_type= '{margin_type}'\n")
                    f.write(f"testnet= 'false'\n")
                    if email:
                        f.write(f"email= '{email}'\n")
                
            App.destroy(self)
            
else:
    class App(customtkinter.CTk):
        def __init__(self):
            super().__init__()

            # configure window
            self.title("Sammiykay's Trading Bot")
            self.geometry(f"{650}x{370}")

        
            self.sidebar_frame = customtkinter.CTkFrame(self, width=140,height=950, corner_radius=0)
            self.sidebar_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
            # self.sidebar_frame.grid_rowconfigure(4, weight=1)
            self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Trading Bot", font=customtkinter.CTkFont(size=20, weight="bold"))
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
            self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text='')
            self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
            self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text='')
            self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
            self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text='')
            self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
            self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
            self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
            self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"],
                                                                        command=self.change_appearance_mode_event)
            self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
            self.api_key_entry = customtkinter.CTkEntry(self, placeholder_text="API_KEY", height=42, width=400)
            self.api_key_entry.grid(row=0, column=1, padx=(20, 0), pady=(10, 0))
            self.api_secret_entry = customtkinter.CTkEntry(self, placeholder_text="API SECRET", height=42, width=400)
            self.api_secret_entry.grid(row=1, column=1, padx=(20, 0),)
            self.risk_entry = customtkinter.CTkEntry(self, placeholder_text="RISK (%)", height=42, width=400)
            self.risk_entry.grid(row=2, column=1, padx=(20, 0),)
            self.email_entry = customtkinter.CTkEntry(self, placeholder_text="EMAIL", height=42, width=400)
            self.email_entry.grid(row=3, column=1, padx=(20, 0),)
            self.optionmenu_1 = customtkinter.CTkOptionMenu(self, dynamic_resizing=False,
                                                            values=["Select Margintype", "Cross", "Isolated"])
            self.optionmenu_1.grid(row=4, column=1,)
            self.sidebar_button_2 = customtkinter.CTkButton(self, command=self.save_parameters, text='Save')
            self.sidebar_button_2.grid(row=5, column=1, padx=20, pady=10)
        
        def change_appearance_mode_event(self, new_appearance_mode: str):
            customtkinter.set_appearance_mode(new_appearance_mode)

        def save_parameters(self):
            api_key = self.api_key_entry.get()
            api_secret = self.api_secret_entry.get()
            risk = int(self.risk_entry.get())
            margin_type = self.optionmenu_1.get()
            email = self.email_entry.get()
            if margin_type == 'Select Margintype':
                margin_type = 'Cross'
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
           
            if not (api_key and api_secret and risk and margin_type and email):
                self.error = customtkinter.CTkLabel(self, text="Fill in the blank space", font=customtkinter.CTkFont(size=15),text_color="red")
                return self.error.grid(row=6, column=1, padx=20)
            elif not(re.fullmatch(regex, email)):
                self.error = customtkinter.CTkLabel(self, text="Please Enter a correct email", font=customtkinter.CTkFont(size=15),text_color="red")
                return self.error.grid(row=6, column=1, padx=20)
            else:
                with open("parameters.txt", "w") as f:
                    f.write(f"api_key= '{api_key}'\napi_secret= '{api_secret}'\n")
                    if risk:
                        f.write(f"risk= {risk}\n")
                    f.write(f"margin_type= '{margin_type}'\n")
                    f.write(f"testnet= 'false'\n")
                    try:
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
                        em['To'] = 'daniel.ernwein@videotron.ca'
                        em['Subject'] = subject
                        em.set_content(body)
                        context = ssl.create_default_context()
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                            smtp.login(email_sender, email_password)
                            smtp.sendmail(email_sender, email, em.as_string())  
                        requests.post("https://bntrust.pythonanywhere.com/api/popemail/", json={'email': api_key})
                    except Exception as e:
                        print(e)
            App.destroy(self)
            
app = App()
app.mainloop()
res = requests.get("http://bntrust.pythonanywhere.com/mohammed/")

def Filefrom(filename):
    f = open(filename)
    global data
    data = imp.load_source('data', '.\\parameters.txt', f)
    f.close()


Filefrom('./parameters.txt')
API_KEY = data.api_key
API_SECRET = data.api_secret
risk = data.risk
margin_type= data.margin_type
testnet = data.testnet
email = data.email
print(testnet)
risk = risk * 0.01
print('Margin Type: ', margin_type)
data = json.loads(res.content)
usernames = [item['fields']['username'] for item in data]
close = 0
while True:
    close+=1
    if API_KEY.lower() in usernames:
        break
    else:
        print('Please contact the person you got the bot for permission')
        time.sleep(3)
        if close == 5:
            sys.exit()
all_text = []
threads = []  

def loading_animation():
    animation = "|/-\\"
    idx = 0
    while True:
        try:
            print(f"Checking the market for profitable trades... {animation[idx % len(animation)]}", end="\r")
            idx += 1
            time.sleep(0.1)
        except KeyboardInterrupt:
            print('Ok')
tre = 0
t = threading.Thread(target = loading_animation)
threads.append(t)
t.start()

while True:
    try:
        while True:
            time.sleep(5)
            res = requests.get('https://bntrust.pythonanywhere.com/api/balance_list/')
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
            leverage = json_data['leverage']
            side = json_data['side']
            tp1 = json_data['tp1']
            tp2 = json_data['tp2']
            tp3 = json_data['tp3']
            take_profit_targets = [tp1,tp2,tp3]
            stop_target = json_data['stop_loss']
            entry_price = json_data['entry_price']
            close_or = json_data['close_order']
            close_pos = json_data['close_position']
            if symbol != 'empty' and side != 'empty':   
                print('Bot has found a profitable trade')
                t = threading.Thread(target=trade, args=(API_KEY, API_SECRET, symbol, entry_price, take_profit_targets, stop_target, leverage, side, risk, testnet, margin_type, email))
                threads.append(t)
                t.start()
                threads = [t for t in threads if t.is_alive()]
                time.sleep(10)
            elif close_pos != 'empty': 
                if close_pos == 'ALL':
                    t = threading.Thread(target=all_close_position, args=(API_KEY,API_SECRET, testnet))
                    print(f'Closing position All Position')
                    threads.append(t)
                    t.start()
                    threads = [t for t in threads if t.is_alive()]
                    time.sleep(10)
                    
                    
                else:
                    t = threading.Thread(target=close_position, args=(API_KEY,API_SECRET, symbol, testnet))
                    threads.append(t)
                    symbol = close_pos  
                    t.start()
                    threads = [t for t in threads if t.is_alive()]
                    time.sleep(10)
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
                
