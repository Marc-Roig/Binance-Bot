from binance.client import Client
from datetime import datetime
from datetime import timedelta
import time, numpy, os

from record_prices import *
from Perc_Recorder import *
from pump import *
from update_prices import *

import api
import config
import threading
import math

def print_coins(coins):
	for key, value in coins.items():
		print("{}: {}".format(key, value['price']))
	print ('\n')

def pause_program():
	while True:
		pass

def check_spikes(coins, clients, pump_running):
	
	for key, coin in coins.items():
		
		spike = (coin['price'] - coin['mean'])/coin['mean']

		if pump_running == True and clients[0]['pump'].coin_bought == False:
			if spike >= config.pump_percentage and spike < config.pump_change_abort:
				for client in clients:
					client['pump'].calculate_order_parameters(str(key), coin['price'], coin['mean'], coin['minQty'], coin['tickSize'])
					if config.make_order:
						buy_pumped_coin(str(key)+config.market, client['pump'], client['client'], client['user'])
					client['pump'].print_parameters()

		for spike_alarm in config.spikes_alarms:

			if pump_running == False and str(spike_alarm) not in coin['previous_spikes'].keys():
				if spike_alarm < 0:
					if spike < spike_alarm:
						print(str(key), " Has fallen a", ("{:.3f}%!").format(spike*-100))
						coin['previous_spikes'][str(spike_alarm)] = datetime.now()
				if spike_alarm > 0:
					if spike > spike_alarm:
						print(str(key), " Has increased a", ("{:.3f}%!").format(spike*100))
						coin['previous_spikes'][str(spike_alarm)] = datetime.now()

def get_clients():
	clients = []
	for client_info in api.clients:
		if not client_info['active']:
			continue
		try:
			client = {}
			client['user'] = client_info['user']
			client['client'] = Client(client_info['api_key'], client_info['api_secret'])
			client['pump'] = pump_info(unicode_to_float(client['client'].get_asset_balance(asset=config.market)['free']))
			# client['pump'] = pump_info(0.025) #Testing purpouses
			clients.append(client)
			check_client(client) #Check if balance is enough for the minimum 0.002 trade
			print('Client : {}, Balance : {:.8f}'.format(client_info['user'], client['pump'].btc_available))
		except Exception as e:
			print('Client : {}, Detected an error and can not use API'.format(client_info['user']))
			print (e)
			pause_program()
			
	if len(clients) == 0:
		print('No clients avaliable')
		pause_program()

	return clients


def check_client(client): #Check if balance is enough for the trades
	btc_amounts = []
	for a in range(len(config.sell_amounts)):
		btc_used = client['pump'].btc_available*config.sell_amounts[a]
		btc_amounts.append(btc_used)
		if  btc_used < config.min_motional:
			print ("Sell amounts not big enough")
			print (btc_amounts)
			pause_program()

def main():
	#--CLIENT INITIALIZATION--#
	clients = get_clients()
	main_client = clients[0]['client']

	#--COIN TRACKER INITIALIZATION--#
	coins_to_track = config.coins_to_track

	track_all_coins(main_client.get_all_tickers(), coins_to_track)

	if config.exclude_coins:		
		for coin in config.excluded_coins:
			if coin in coins_to_track:
				coins_to_track.remove(coin)

	price_recorder = Price_Recorder(config.t_betw_rec, 10)
	price_recorder.initialize_coins(main_client.get_all_tickers(), coins_to_track, main_client.get_exchange_info()['symbols'] )

	#--TIME EVENTS--#
	t_fetch = time.time()
	t_dips = time.time()
	t_reset_alarms = time.time()
	t_pump_start = time.time()


	#--LIST OF RETAINED PRICES DURING PUMP--#
	retained_prices = {} 
	for coin in coins_to_track:
		retained_prices[coin] = []

	#--RESET SPIKE ALARM--#
	t_betw_res_alarm_delta =timedelta(seconds = config.t_betw_res_alarm)

	#--PUMP INFO--#
	pump_running = False

	#--PRICE UPDATES--#
	pricing_with_threads = False

	#--MAIN LOOP--#
	while True:
		#--UPDATE PRICES--#
		if time.time() - t_fetch > config.t_betw_fetch:
			t_fetch = time.time()

			if pricing_with_threads == False:
				update_prices(main_client.get_all_tickers(), price_recorder.coins)

			#---RECORD COINS---#
			if config.record_coins_txt:
				if pump_running == True: 
					for symb, coin in price_recorder.coins.items():
						retain_coin_price(coin['price'], retained_prices[symb], symb)
				else: 
					for symb, coin in price_recorder.coins.items():
						record_coin_price(coin['price'], symb)
			
			#---START PUMP MODE---#
			if config.next_pump['ended'] == False and pump_running == False:
				if is_pump_near(config.next_pump, 0, config.pump_time_margin+2) and pricing_with_threads == False:
					start_updating_prices(main_client, price_recorder.coins)
					pricing_with_threads = True
				elif is_pump_near(config.next_pump, 0, config.pump_time_margin): # 5 seconds before
					pump_running = True
					config.t_betw_fetch = 0.15
					t_pump_start = time.time()
					print ("...Starting Pump Procedure...")

			#---CHECK FOR FAST % CHANGES---#
			check_spikes(price_recorder.coins, clients, pump_running)

		#---UPDATE RECORDS---#
		if time.time() - t_dips > config.t_betw_rec:
			t_dips = time.time()
			price_recorder.update_previous_prices()

		#---PUMP MODE ENDED---#
		if time.time() - t_pump_start > config.t_pump_duration and pump_running:
			pump_running = False
			pricing_with_threads = False
			config.next_pump['ended'] = True
			config.t_betw_fetch = 0.5
			terminate_threads()
			for client in clients:
				client['pump'].reset_parameters()
			print ("Dumping data, Pump finalized!")

			if config.record_coins_txt:
				for key, coin_retained_prices in retained_prices.items():
					dump_retained_prices(coin_retained_prices, key)

		#---RESET SPIKE ALARMS---#
		if time.time() - t_reset_alarms > config.t_betw_res_alarm and pump_running == False:
			t_reset_alarms = time.time()
			for symb, coin in price_recorder.coins.items():
				for spike_alarm in config.spikes_alarms:
					if str(spike_alarm) in coin['previous_spikes'].keys():
						if datetime.now() - coin['previous_spikes'][str(spike_alarm)] > t_betw_res_alarm_delta:
							coin['previous_spikes'].pop(str(spike_alarm), None)


if __name__ == '__main__':
  main()
