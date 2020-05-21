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
# DONE check all orders to avoid running multiple of same order
# DONE close trades
# TODO add trailing stop loss - Question: How do I know when to add a stop loss to the order?
# DONE add buy limit order
# DONE add stop limit order
#===============================================================================================#
#------------------------------------- MODULE IMPORTS ------------------------------------------#
#===============================================================================================#
import json
from oandapyV20 import API
import oandapyV20.endpoints.trades as trades
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import LimitOrderRequest
from oandapyV20.contrib.requests import StopOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
from oandapyV20.contrib.requests import TrailingStopLossOrderRequest
from oandapyV20.contrib.requests import TradeCloseRequest
import oandapyV20.endpoints.orders as orders
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
def get_trades():
    """ Returns a json of all accounts trades """ 
    r = trades.TradesList(accountID)
    #print("REQUEST:{}".format(r))
    rv = api.request(r)
    #print("RESPONSE:\n{}".format(json.dumps(rv, indent=2)))
    return rv

def get_trade_info_by_instrument(order_instrument):
    """ Get tradeID and unit information on a trade with the given currency pair/instrument""" 
    trade_info = {}
    trade_response = get_trades()
    all_trades = trade_response['trades']
    for trade in all_trades:
        tradeID = trade['id']
        instrument = trade['instrument']
        current_units = trade['currentUnits']
        #print("tradeID:\n{}".format(tradeID))#.format(json.dumps(trade, indent=2)))
        #print("Instrument:\n{}".format(instrument))
        #print("Current units:\n{}".format(current_units))
        if instrument == order_instrument:
            trade_info['tradeID'] = tradeID
            trade_info['units'] = current_units

    if bool(trade_info) == False:
        # Checking if the trade_info dictionary is empty
        print("No open {} trades found!".format(order_instrument))
        return False
    else:
        return trade_info

def get_all_open_trades():
    """ 
    Get tradeID, unit information and instrument for all currently open trades.
    Stores each trade in nested lists, of the form ['tradeID', 'units', 'instrument']
    """
    all_open_trades = []
    trade_response = get_trades()
    all_trades = trade_response['trades']
    for trade in all_trades:
        trade_list = []
        tradeID = trade['id']
        trade_list.append(tradeID)
        current_units = trade['currentUnits']
        trade_list.append(current_units)
        instrument = trade['instrument']
        trade_list.append(instrument)
        all_open_trades.append(trade_list)
    return all_open_trades

def check_for_existing_trades(order_instrument, order_units):
    """ 
    Check for an existing trade with the same instrument and units.
    Returns True if trade exists with same instrument and units and false if matching trade does not exist.
    """
    trade_exists = False
    open_trades = get_all_open_trades()
    for trade in open_trades:
        units = trade[1]
        instrument = trade[2]
        if units == order_units and instrument == order_instrument:
            #print("{} Trade with {} units already exists!".format(instrument, units))
            trade_exists = True
    return trade_exists
        

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

def create_limit_order(order_instrument, order_units, order_take_profit, order_stop_loss, order_price):
    """ 
    Create a limit order.
    The Limit Order will only be filled by a market price that is equal to or better than this price.
    """
    # Create the order body
    ordr = LimitOrderRequest(
        instrument = order_instrument,
        units = order_units,
        takeProfitOnFill=TakeProfitDetails(price=order_take_profit).data,
        stopLossOnFill=StopLossDetails(price=order_stop_loss).data,
        price = order_price)
    # create the OrderCreate request
    r = orders.OrderCreate(accountID, data=ordr.data)
    try:
        # create the OrderCreate request
        rv = api.request(r)
    except oandapyV20.exceptions.V20Error as err:
        print(r.status_code, err)
    else:
        print(json.dumps(rv, indent=2))

def create_stop_order(order_instrument, order_units, order_take_profit, order_stop_loss, order_price):
    """ 
    Create a stop order.
    A StopOrder is an order that is created with a price threshold, and will only be filled by a price that is equal to or worse 
    than the threshold.
    """
    # Create the order body
    ordr = StopOrderRequest(
        instrument = order_instrument,
        units = order_units,
        takeProfitOnFill=TakeProfitDetails(price=order_take_profit).data,
        stopLossOnFill=StopLossDetails(price=order_stop_loss).data,
        price = order_price)
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
                try:
                    signal_to_give = Translator(newest_message)
                    if signal_to_give != current_signal:
                        # Parse the signal into variables
                        current_signal = signal_to_give
                        #print('New signal inbound!')
                        print("Signal: {}".format(signal_to_give))
                        # Currency Pair/Instrument
                        instrument = signal_to_give[0]
                        # Buy/Sell/Close
                        order_type = signal_to_give[1]
                        # Take Profit
                        tp = signal_to_give[2]['tp'] 
                        # Stop loss
                        sl = signal_to_give[2]['sl']
                        # Unique tradeID
                        tradeID = get_trade_info_by_instrument(instrument)['tradeID']
                        # Number of units 
                        units = 1000
                        # Test for buy or sell - if 'sel' then negative units used
                        if order_type == 'sel':
                            # To sell units must be negative
                            sell_units = -1 * units 
                            # Check if the trade already exists
                            if check_for_existing_trades(instrument, sell_units) == False: 
                                # Creating a market order - create_market_order(instrument, units, takeProfit, stopLoss)
                                create_market_order(instrument, sell_units, tp, sl)
                            else:
                                print("{} Trade with {} units already exists!".format(instrument, sell_units))
                        elif order_type =='buy':
                            buy_units = units 
                            if check_for_existing_trades(instrument, buy_units) == False: 
                                create_market_order(instrument, sell_units, tp, sl)
                            else:
                                print("{} Trade with {} units already exists!".format(instrument, buy_units))
                        elif order_type == 'close':
                            # Close the order, using its tradeID
                            close_order(tradeID, 'ALL')
                        else:
                            print("Error: Not a valid buy/sell order type")
                    else:
                        print('No new signals!')
                except UnboundLocalError:
                    print('UnboundLocalError: Cannot read signal.')
                except KeyError:
                    print('KeyError: Cannot read signal')
                except IndexError:
                    signal_to_give = Translator(newest_message)
                    if signal_to_give[1] == 'close':
                        None
                        #Isaac add more close stuff here !!!!!!
                        # Why do I need to close an order if we get an error? - Isaac 
                    else:
                        print('IndexError: Cannot read signal')
                time.sleep(30)
        except errors.FloodWaitError as e:
            print('Sleeping')
            time.sleep(90)
#===============================================================================================#
#------------------------------------ CALLING FUNCTIONS ----------------------------------------#
#===============================================================================================#
# with client:
#     client.loop.run_until_complete(main(phone))

### TESTING FUNCTIONS ###
#create_market_order("AUD_CHF", 69, 0.65, 0.60)
#get_trades()
#print(get_trade_info_by_instrument("AUD_CAD")['tradeID'])
#print(get_all_open_trades())
#print(check_for_existing_trades('AUD_CAD', '69'))
#create_trailing_stop_loss_order("21", 0.02, "GTC")
#close_order("40", "ALL")
#create_limit_order('AUD_CAD', 77, 0.93, 0.90, '0.91')
#create_stop_order('AUD_CAD', 28, 0.93, 0.90, 0.91)

