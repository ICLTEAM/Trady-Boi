# First Created: 17/05/2020
# Authors: Oscar Weeding, Isaac Lee

# API Information
#98687799930ef52671ed0b5cedfd5a94-b7c6913e9ed847fa80f17863b502a698
import json
from oandapyV20 import API
import oandapyV20.endpoints.trades as trades
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails

import oandapyV20.endpoints.orders as orders
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


def create_order(order_instrument, order_units, order_take_profit, order_stop_loss):
    """ Create an oder with the OrderCreate method """
    mktOrder = MarketOrderRequest(
        instrument = order_instrument,
        units = order_units,
        takeProfitOnFill=TakeProfitDetails(price=order_take_profit).data,
        stopLossOnFill=StopLossDetails(price=order_stop_loss).data)
    
    # create the OrderCreate request
    r = orders.OrderCreate(accountID, data=mktOrder.data)
    try:
        # create the OrderCreate request
        rv = api.request(r)
    except oandapyV20.exceptions.V20Error as err:
        print(r.status_code, err)
    else:
        print(json.dumps(rv, indent=2))





get_trades()
#create_order("AUD_CAD", 10, 1.00, 0.80)
