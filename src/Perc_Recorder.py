import config

def unicode_to_float(string):
	if '.' in string:
		aux = string.split('.')
		decimals = len(aux[1])
		return float(aux[0]) + float(aux[1])/pow(10,len(aux[1]))
	else:
		return float(string)

class Price_Recorder:

	def __init__(self, logtime = 1, num_of_records = 10):
		self.logtime = logtime
		self.num_of_records = num_of_records
		self.prices_ready = False
		self.init_counter = 0
		self.coins = {}

	def initialize_coins(self, tickers, coins_to_track, exchange_info,  pair2 = config.market):
		for ticker in tickers:
			for coin_to_track in coins_to_track:
				if ticker['symbol'] == coin_to_track + pair2:
					coin = {}
					coin['price'] = unicode_to_float(ticker['price'])
					coin['previous_prices'] = [coin['price']] * self.num_of_records
					coin['mean'] = coin['price']
					coin['minQty'] = 0.0
					coin['tickSize'] = 0.0
					coin['previous_spikes'] = {}
					self.coins[str(coin_to_track)] = coin

		self.get_min_price(exchange_info, coins_to_track)
		self.get_tick_size(exchange_info, coins_to_track)

	def get_min_price(self, exchange_info, coins_to_track):
		for pair in exchange_info:
			if pair['symbol'].endswith(config.market):
				symb = pair['symbol'].replace(config.market, '') 
				if symb in coins_to_track:
					minQty = unicode_to_float(pair['filters'][1]['minQty'])
					self.coins[symb]['minQty'] = minQty

	def get_tick_size(self, exchange_info, coins_to_track):
		for pair in exchange_info:
			if pair['symbol'].endswith(config.market):
				symb = pair['symbol'].replace(config.market, '') 
				if symb in coins_to_track:
					tickSize = unicode_to_float(pair['filters'][0]['tickSize'])
					self.coins[symb]['tickSize'] = tickSize


	#--MISC--#	
	def get_mean(self, coin):
		mean = 0
		previous_prices = coin['previous_prices']
		for price in previous_prices[:-4]:
			mean += price
			coin['mean'] = mean / (len(previous_prices)-4)

	#--CORE--#
	def update_previous_prices(self):
		if self.prices_ready == True:
			for key, coin in self.coins.items():
				coin['previous_prices'].pop(0) #Get rid of the first and append the new at the end
				coin['previous_prices'].append(coin['price'])
				self.get_mean(coin)
				self.coins[str(key)] = coin #Update coin
		else:
			for key, coin in self.coins.items():
				coin['previous_prices'][self.init_counter] = coin['price']
				self.coins[str(key)] = coin #Update coin

			self.init_counter += 1
			# print self.init_counter * self.logtime, "s"
			if self.init_counter >= self.num_of_records:
				print ("Array of Records initialized!")
				self.prices_ready = True



		