# First Created: 17/05/2020
# Authors: Oscar Wooding, Isaac Lee

# ████████╗██████╗░░█████╗░██████╗░██╗░░░██╗  ██████╗░░█████╗░██╗
# ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗╚██╗░██╔╝  ██╔══██╗██╔══██╗██║
# ░░░██║░░░██████╔╝███████║██║░░██║░╚████╔╝░  ██████╦╝██║░░██║██║
# ░░░██║░░░██╔══██╗██╔══██║██║░░██║░░╚██╔╝░░  ██╔══██╗██║░░██║██║
# ░░░██║░░░██║░░██║██║░░██║██████╔╝░░░██║░░░  ██████╦╝╚█████╔╝██║
# ░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░  ╚═════╝░░╚════╝░╚═╝
#===============================================================================================#
#--------------------------------------- TODO LIST ---------------------------------------------#
#===============================================================================================#
# TODO check all orders to avoid running multiple of same order
# TODO add trailing stop loss
# TODO close trades
# TODO add buy limit and stop limit orders
#===============================================================================================#
#------------------------------------- MODULE IMPORTS ------------------------------------------#
#===============================================================================================#
import json
from oandapyV20 import API
import oandapyV20.endpoints.trades as trades
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
from oandapyV20.contrib.requests import TrailingStopLossOrderRequest
from oandapyV20.contrib.requests import TradeCloseRequest
import oandapyV20.endpoints.orders as orders
#from oandapyV20.endpoints.trades import 
import oandapyV20
import configparser
import asyncio
from datetime import date, datetime
import time
from telethon import TelegramClient
from telethon import errors
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)
#===============================================================================================#
#------------------------------------ GLOBAL VARIABLES -----------------------------------------#
#===============================================================================================#
list_of_pairs = ['audcad', 'audchf', 'audjpy', 'audnzd', 'audusd', 'cadchf', 'cadjpy', 'chfjpy', 'euraud', 'gbpnzd', 'eurgbp', 'nzdusd', 'nzdjpy', 'gbpusd', 'gbpjpy', 'eurjpy', 'usdcad', 'gbpcad', 'eurusd', 'xauusd', 'usdjpy', 'usdchf', 'eurnzd', 'gbpchf', 'usoil', 'eurcad', 'nzdcad', 'us30', 'nas100', 'gbpaud']
list_of_sl_indicators = ['sl',  'stop',  'stoploss']
list_of_tp_indicators = ['tp', 'take', 'takeprofit','tp1', 'tp2', 'tp3']
punctuation = ['\n', '#', ':', '£', '*', '\\', '📈', '📉', '/']
directions = ['buying', 'selling', 'sell', 'buy']
#===============================================================================================#
#------------------------------------ TRADING API SETUP ----------------------------------------#
#===============================================================================================#
#oscar_token = "9d6e6cd1c372515f82dfda2de4b7540f-cd6cafe8b8da1ba8a83d3964e05252e1"
isaac_token = "98687799930ef52671ed0b5cedfd5a94-b7c6913e9ed847fa80f17863b502a698"
#number = +44 7375 066642
# Creating the API Object
try:
    api = API(access_token = oscar_token)
    accountID = "101-004-14834458-001"  # Oscar Oanda AccountID
    print("Using Oscars' Account")
except NameError:
    api = API(access_token = isaac_token)
    accountID = "101-004-14849550-001"   # Isaac Oanda AccountID
    print("Using Isaacs' Account")
# NOTE: For some reason if I switch to my account after already first running it with Oscars then
# it still uses Oscars? To fix I have to relaunch my python shell
#===============================================================================================#
#------------------------------------ TRADING FUNCTIONS ----------------------------------------#
#===============================================================================================#
def list_trades():
    r = trades.TradesList(accountID)
    print("REQUEST:{}".format(r))
    rv = api.request(r)
    print("RESPONSE:\n{}".format(json.dumps(rv, indent=2)))

def create_market_order(order_instrument, order_units, order_take_profit, order_stop_loss):
    """ 
    Create a market order.
    A market order is an order that is filled immediately upon creation using the current market price.
    """
    # Create the order body
    ordr = MarketOrderRequest(
        instrument = order_instrument,
        units = order_units,
        takeProfitOnFill=TakeProfitDetails(price=order_take_profit).data,
        stopLossOnFill=StopLossDetails(price=order_stop_loss).data)
    
    # create the OrderCreate request
    r = orders.OrderCreate(accountID, data=ordr.data)
    try:
        # create the OrderCreate request
        rv = api.request(r)
    except oandapyV20.exceptions.V20Error as err:
        print(r.status_code, err)
    else:
        print(json.dumps(rv, indent=2))

def create_trailing_stop_loss_order(order_tradeID, order_distance, order_timeInForce):
    """ Create a trailing stop loss order """
    ordr = TrailingStopLossOrderRequest(
        # The ID of the Trade to close when the price threshold is breached.
        tradeID = order_tradeID,
        # The price distance (in price units) specified for the TrailingStopLoss Order.
        distance = order_distance,
        # The time-in-force requested for the TrailingStopLoss Order. Restricted to
        # “GTC”, “GFD” and “GTD” for TrailingStopLoss Orders.
        timeInForce = order_timeInForce
        # The date/time when the StopLoss Order will be cancelled if its
        # timeInForce is “GTD”.
        #gtdTime = order_gtdTime
        )
    # create the OrderCreate request
    r = orders.OrderCreate(accountID, data=ordr.data)
    try:
        # create the OrderCreate request
        rv = api.request(r)
    except oandapyV20.exceptions.V20Error as err:
        print(r.status_code, err)
    else:
        print(json.dumps(rv, indent=2))

def close_order(order_tradeID, order_units):
    """ Close an order """
    ordr = TradeCloseRequest(units=order_units)
    # Create TradeClose order request
    r = trades.TradeClose(accountID, tradeID=order_tradeID, data=ordr.data)
    # Perform the request
    try:
        rv = api.request(r)
    except oandapyV20.exceptions.V20Error as err:
        print(r.status_code, err)
    else:
        print(json.dumps(rv, indent=2))
#===============================================================================================#
#------------------------------------ TELEGRAM API SETUP ---------------------------------------#
#===============================================================================================#
# Reading Configs
config = configparser.ConfigParser()
config.read('config.ini')  #-- Simplified by Isaac
# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
api_hash = str(api_hash)
phone = config['Telegram']['phone']
username = config['Telegram']['username']
# Create the client and connect
client = TelegramClient(username, api_id, api_hash)
#===============================================================================================#
#------------------------------------ TRANSLATOR FUNCTION --------------------------------------#
#===============================================================================================#
def Translator(message):
    """ Parse telegram order messages """
    words = ''.join(message)
    words = words.lower()
    words = words.replace('/', '')
    for item in punctuation:
        words = words.replace(item, ' ')
        list_of_words = words.split(' ')
        for item in list_of_words:
            #print(item)
            if item in list_of_pairs:
                # Convert 'audjpy' to 'AUD_JPY'
                new_pair = ""
                counter = 0
                for char in item:
                    if counter != 3:
                        new_pair += char.upper()
                    else:
                        new_pair += "_" + char.upper()
                        counter += 1
                        id = new_pair
        dict_of_values = {}
        for value in range(len(list_of_words)):
            word = str(list_of_words[value])
            val = value
            #Checks to see if buy limit/sell limit and adds limit to dict
            if word in directions:
                direction = word[:3]
                if 'limit' in list_of_words:
                    while val < len(list_of_words):
                        word = list_of_words[val]
                        try:
                            float(word)
                            #print(word)
                            dict_of_values['limit'] = word
                            break
                        except ValueError:
                            None
                        val += 1
                        #print(type(word))
            if word in list_of_sl_indicators:
                i = 'sl'
                #print(i)
                while val < len(list_of_words):
                    word = list_of_words[val]
                    try:
                        float(word)
                        #print(word)
                        dict_of_values[i] = word
                        break
                    except ValueError:
                        None
                    val += 1
            elif word in list_of_tp_indicators:
                val = value
                i = 'tp'
                #print(i)
                while val < len(list_of_words):
                    word = list_of_words[val]
                    try:
                        float(word)
                        #print(word)
                        dict_of_values[i] = word
                        break
                    except ValueError:
                        None
                    val += 1
        if 'close' in list_of_words:
            return id, 'close'
        else:
            return id, direction, dict_of_values



#===============================================================================================#
#---------------------------------- MAIN LOOP FUNCTION -----------------------------------------#
#===============================================================================================#
async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))
    me = await client.get_me()
    user_input_channel = '1314870937'
    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel
    current_signal = None
    while True:
        try:
            while True:
                my_channel = await client.get_entity(entity)
                newest_message = []
                async for message in client.iter_messages(my_channel,limit=1):
                    newest_message.append(message.text)
                #print(newest_message)
                try:
                    signal_to_give = Translator(newest_message)
                    if signal_to_give != current_signal:
                        # Parse the signal into variables
                        current_signal = signal_to_give
                        print('New signal inbound!')
                        print("Signal: {}".format(signal_to_give))
                        #Isaac do stuff here to make trade.
                        instrument = signal_to_give[0]
                        print("Instrument = {}".format(instrument))

                        order_type = signal_to_give[1]
                        print("Buy/Sell = {}".format(order_type))
                        # Take Profit
                        tp = signal_to_give[2]['tp']
                        print("Take Profit = {}".format(tp))
                        # Stop loss
                        sl = signal_to_give[2]['sl']
                        print("Stop Loss = {}".format(sl))
                        # Creating a market order - create_market_order(instrument, units, takeProfit, stopLoss)
                        # Test for buy or sell - if 'sel' then negative units used
                        if order_type == 'sel':
                            create_market_order(instrument, -5000, tp, sl)
                        elif order_type =='buy':
                            create_market_order(instrument, 5000, tp, sl)
                            #add order cancellation here !!!!!!!!!#
                        elif order_type == 'close':
                            None
                        else:
                            print("Error: Not a valid buy/sell order type")
                        # Create_trailing_stop_loss_order(order_tradeID, order_distance, order_timeInForce):
                        #list_trades()
                        #close_order("order_TradeID", "UNITS(use 'ALL' to fully close)")
                    else:
                        print('No new signals!')
                except UnboundLocalError:
                    print('Cannot read signal.')
                except KeyError:
                    print('Cannot read signal')
                except IndexError:
                    signal_to_give = Translator(newest_message)
                    if signal_to_give[1] == 'close':
                        None
                        #Isaac add more close stuff here !!!!!!
                    else:
                        print('Cannot read signal')
                #print(signal_to_give)
                time.sleep(30)
        except errors.FloodWaitError as e:
            print('Sleeping')
            time.sleep(90)
#===============================================================================================#
#------------------------------------ CALLING FUNCTIONS ----------------------------------------#
#===============================================================================================#
# with client:
#     client.loop.run_until_complete(main(phone))

### TRADING FUNCTIONS ###
#create_market_order("AUD_CAD", 100, 0.95, 0.90)
#list_trades()
#create_trailing_stop_loss_order("21", 0.02, "GTC")
#close_order("40", "ALL")



