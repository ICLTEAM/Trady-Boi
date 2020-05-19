
signals = ['I’ve got an SL at 9366 so potential entry would \nSELL NASDAQ @ 9346\nSL @ 9366\nTP @ 9270']

List_of_pairs = ['eurusd', 'usdjpy', 'gbpjpy', 'usdchf', 'usdcad', 'audusd', 'nzdusd', 'eurgbp', 'euraud', 'gbpjpy', 'chfjpy', 'nzdjpy', 'gbpcad', 'gbpnzd', 'xauusd', 'nasdaq']
list_of_indicators = ['sl', 'tp', 'stop', 'take', 'stoploss', 'takeprofit', 'tp1', 'tp2', 'tp3']
punctuation = ['\n', '#', ':', '£', '*', '\', ']

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
        
        if word == 'buy':
            direction = 'buy'
        elif word == 'sell':
            direction = 'sell'
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

print(Translator(signals))