import configparser
import json
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

# Reading Configs
config = configparser.ConfigParser()
config.read('C:\\Users\Oscar\Desktop\Oscars Coding folder\PythonProjects\config.ini') 

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

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

    #Translation of messages function

    List_of_pairs = ['audcad', 'audchf', 'audjpy', 'audnzd', 'audusd', 'cadchf', 'cadjpy', 'chfjpy', 'euraud', 'gbpnzd', 'eurgbp', 'nzdusd', 'nzdjpy', 'gbpusd', 'gbpjpy', 'eurjpy', 'usdcad', 'gbpcad', 'eurusd', 'xauusd', 'usdjpy', 'usdchf', 'eurnzd', 'gbpchf', 'usoil', 'eurcad', 'nzdcad', 'us30', 'nas100']
    list_of_indicators = ['sl', 'tp', 'stop', 'take', 'stoploss', 'takeprofit', 'tp1', 'tp2', 'tp3']
    punctuation = ['\n', '#', ':', '£', '*', '\\', '📈', '📉', '/']
    directions = ['buying', 'selling', 'sell', 'buy']

    def Translator(message):
        words = ''.join(message)
        words = words.lower()
        words = words.replace('/', '')
        
        for item in punctuation:
            words = words.replace(item, ' ')
    

        list_of_words = words.split(' ')

        for item in list_of_words:
            #print(item)
            if item in List_of_pairs:
                id = item
                
        
        dict_of_values = {}

        for value in range(len(list_of_words)):
            word = str(list_of_words[value])
            
            if word in directions:
                direction = word[:3]
            #print(type(word))
            
            if word in list_of_indicators:
                val = value
                i = word
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
            return 'Close', id
        else:
            return id, direction, dict_of_values

    user_input_channel = 'https://t.me/joinchat/AAAAAFE68OMuZqcIMIjbZQ'

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
                        current_signal = signal_to_give
                        print('New signal inbound!')
                        print(signal_to_give)
                        #Isaac do stuff here to make trade.
                    else:
                        print('No new signals!')
                
                except UnboundLocalError:
                    print('Cannot read signal.')
                #print(signal_to_give)

                #call to make trade
                time.sleep(10)
        except errors.FloodWaitError as e:
            print('Sleeping')
            time.sleep(90)


with client:
    client.loop.run_until_complete(main(phone))