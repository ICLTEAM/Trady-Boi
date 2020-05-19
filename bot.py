# First Created: 17/05/2020
# Authors: Oscar Weeding, Isaac Lee

#                              .-----.
#                             /7  .  (
#                            /   .-.  \
#                           /   /   \  \
#                          / `  )   (   )
#                         / `   )   ).  \
#                       .'  _.   \_/  . |
#      .--.           .' _.' )`.        |
#     (    `---...._.'   `---.'_)    ..  \
#      \            `----....___    `. \  |
#       `.           _ ----- _   `._  )/  |
#         `.       /"  \   /"  \`.  `._   |
#           `.    ((O)` ) ((O)` ) `.   `._\
#             `-- '`---'   `---' )  `.    `-.
#                /                  ` \      `-.
#              .'                      `.       `.
#             /                     `  ` `.       `-.
#      .--.   \ ===._____.======. `    `   `. .___.--`     .''''.
#     ' .` `-. `.                )`. `   ` ` \          .' . '  8)
#    (8  .  ` `-.`.               ( .  ` `  .`\      .'  '    ' /
#     \  `. `    `-.               ) ` .   ` ` \  .'   ' .  '  /
#      \ ` `.  ` . \`.    .--.     |  ` ) `   .``/   '  // .  /
#       `.  ``. .   \ \   .-- `.  (  ` /_   ` . / ' .  '/   .'
#         `. ` \  `  \ \  '-.   `-'  .'  `-.  `   .  .'/  .'
#           \ `.`.  ` \ \    ) /`._.`       `.  ` .  .'  /
#            |  `.`. . \ \  (.'               `.   .'  .'
#         __/  .. \ \ ` ) \                     \.' .. \__
#  .-._.-'     '"  ) .-'   `.                   (  '"     `-._.--.
# (_________.-====' / .' /\_)`--..__________..-- `====-. _________)
#                  (.'(.'
# "Ribbit" - Froge



# API Information
#98687799930ef52671ed0b5cedfd5a94-b7c6913e9ed847fa80f17863b502a698
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

my_token = "98687799930ef52671ed0b5cedfd5a94-b7c6913e9ed847fa80f17863b502a698"

# Creating the API Object
api = API(access_token = my_token)
accountID = "101-004-14849550-001" 

def get_trades():
    r = trades.TradesList(accountID)
    print("REQUEST:{}".format(r))
    rv = api.request(r)
    print("RESPONSE:\n{}".format(json.dumps(rv, indent=2)))


def create_market_order(order_instrument, order_units, order_take_profit, order_stop_loss):
    """ Create a market order """
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


    

    


### CALLING FUNCTIONS ###
#create_market_order("AUD_CAD", 100, 0.95, 0.90)
#get_trades()
#create_trailing_stop_loss_order("21", 0.02, "GTC")
#close_order("40", "ALL")
