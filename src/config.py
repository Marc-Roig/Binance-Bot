
#Pump
next_pump = {'year': 2018, 'month': 2, 'day': 11, 'hour' : 19, 'min' : 00, 'sec' : 00, 'group': "Mega_Pump", 'ended' : False}
make_order = True #For test purpouses, set it as False and any order will be placed during the pump
perc_to_pump = 0.9 #% of the total balance to invest, it has to be less than 1 due to the price variations of the coins.
pump_time_margin = 5 #-Seconds before the next_pump to start the pump procedure

pump_percentage = 0.03	#The coin which increases this percentage will be bought during the pump procedure
pump_change_abort = 0.1 #Abort the pump if the coin has already exceded this percentage

sell_amounts = [0.3, 0.4, 0.3] # Divide the sell limits with the % assigned, make sure the sum of all equals to 1
price_amounts = [1.11, 1.14, 1.16] # % of sell limits, make sure there are the same price amounts as sell amounts

min_motional = 0.002 #0.002 is the min BTC to trade, use a greater amount for being sure it wont pop an error

#Tracked coins
coins_to_track = [] #Testing, don't touch
market = 'BTC' #Market of the pump (BTC, ETH, BNB ...)
excluded_coins = ['ETH', 'TRX', 'XRP', 'GTO', 'ICX', 'NEO', 'VEN', 'BNB', 'HSR', 'ETC', 'NANO', 'BCC', 'ADA', 'EOS', 'LTC', 'POE', 'LSK', 'ADX', 'XLM', 'PPT', 'BLZ', 'GXS', 'NAV', 'IOTA', 'CDT', 'IOST', 'ZEC']

#Spikes
spikes_alarms = [-0.7,-0.1, 0.7, 0.05, 0.02] #Show an alarm if any coin exceeds this percentages

#Time events
t_betw_fetch = 0.5 #Time between the program will ask binance for prices
t_betw_rec = 5	#Time between recording for the .txt
t_betw_res_alarm = 20 #Time reset for the alarms
t_pump_duration = 40 #Seconds which the pump procedure will last

#Don't touch thingys
exclude_coins = True
record_coins_txt = False

#Price threads
time_between_thread = 0.15
time_to_sleep = 1



	

