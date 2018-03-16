from datetime import datetime
from datetime import timedelta
import time, numpy, os

from record_prices import *
from Perc_Recorder import *
from pump import *
import config
import threading
import math

stop_threads = False

#Multithreading update prices
def update_price_thread(thread_position, main_client, coins):
	time.sleep(config.time_between_thread*thread_position) #Max of 16,6 req per sec
	last = time.time()

	while stop_threads == False:
		if time.time() - last >= config.time_to_sleep:
			last += config.time_to_sleep
			try:
				update_prices(main_client.get_all_tickers(), coins)
			except Exception as e:
				print(e)

def start_updating_prices(main_client, coins):
	num_of_threads = int(math.ceil(config.time_to_sleep / config.time_between_thread)) 

	for thread_number in range(num_of_threads):
		t = threading.Thread(target=update_price_thread, args=(thread_number, main_client, coins))
		t.daemon = True #kill thread if main ends
		t.start()

def terminate_threads():
	global stop_threads 
	stop_threads = True

#Inicialization functions
def update_prices(tickers, coins):
	for ticker in tickers:
		if ticker['symbol'].endswith(config.market):
			symb = ticker['symbol'].replace(config.market, '') #Symbol without the ETH
			if symb in coins.keys():
				coins[symb]['price'] = unicode_to_float(ticker['price']) 

def track_all_coins(tickers, coins_to_track):
	for ticker in tickers:
		symb = str(ticker['symbol'])
		if symb.endswith(config.market): #ETH pairs
			symb = symb.replace(config.market, '')
			coins_to_track.append(symb)
