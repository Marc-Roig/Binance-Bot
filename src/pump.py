
from datetime import datetime
from datetime import timedelta

from decimal import *
import threading

import config

class pump_info:
	def __init__(self, btc_available):
		self.coin = ''
		self.initial_price = 0
		self.price_bought = 0

		self.btc_available = btc_available
		self.amount_to_buy = 0

		self.trade_info = {}
		self.pump_running = False
		self.coin_bought = False

		self.prices_to_sell = []
		self.amount_to_buy = []

	def calculate_order_parameters(self, coin, price_bought, initial_price, minQty, tickSize):
		self.coin = coin
		self.initial_price = initial_price
		self.price_bought = price_bought
		self.pump_running = True
		self.coin_bought = True
 
		self.amount_to_buy = self.truncate_to_minQty(self.btc_available / (self.price_bought / config.perc_to_pump),  minQty)
		
		config.t_betw_fetch = 0.5

		self.prices_to_sell = self.get_sell_prices(initial_price ,tickSize)
		self.amounts_to_buy = self.get_amounts_to_buy(minQty)



	#--SELL LIMIT CALCULATION--#

	def solve_float_error(self, amount, minQty):
		if minQty % 1 < 0:
			getcontext().prec = 28
			number = Decimal(str(amount)).quantize(Decimal(str(minQty)), rounding=ROUND_DOWN)
			return float(number)
		else:
			return amount - amount % minQty

	def get_sell_prices(self, initial_price, tickSize):
		num_of_orders = len(config.sell_amounts)
		sell_prices = []
		for order in range(num_of_orders):
			sell_price = self.solve_float_error(config.price_amounts[order] * initial_price, tickSize)
			sell_prices.append(self.sell_price_to_str(sell_price, tickSize))
		return sell_prices

	def get_amounts_to_buy(self, minQty):
		num_of_orders = len(config.sell_amounts)
		order_amounts = [0.0]*num_of_orders
		amount_left = self.amount_to_buy

		for order in range(num_of_orders-1, -1, -1):
			if order != 0:
				amount_to_add = self.solve_float_error(self.amount_to_buy * config.sell_amounts[order], minQty)
				order_amounts[order] = amount_to_add
				amount_left -= amount_to_add
			else:
				order_amounts[0] = self.solve_float_error(amount_left, minQty)

		return order_amounts

	#--MISC--#

	def print_parameters(self):

		print('Bought {} {} priced at {:.8f} with an initial price of {:.8f}. Sell limits at:'.format(self.amount_to_buy, self.coin, self.price_bought, self.initial_price))
		print(self.prices_to_sell)

	def sell_price_to_str(self, amount, tickSize):
		cut_value = self.truncate_to_minQty(amount, tickSize)
		return '{:.8f}'.format(cut_value)

	def truncate_to_minQty(self, amount, minQty):

		return int(amount / minQty) / (1 / minQty)

	def reset_parameters(self):
		self.coin = ''
		self.initial_price = 0
		self.price_bought = 0

		self.btc_available = 0
		self.amount_to_buy = 0

		self.prices_to_sell[:] = []
		self.amounts_to_buy[:] = []

		self.trade_info.clear()
		self.pump_running = False
		self.coin_bought = False


#--Buy the coin--#
def buy_pumped_coin(symb, pump_data, client, user):
	amount_to_buy = pump_data.amount_to_buy
	
	try:
		client.order_market_buy(symbol=symb, quantity=amount_to_buy)
	except Exception as e:
		print('Problem encountered buying {} with the {} account. Error is {}'.format(symb, user, e))

	try:
		sell_limit_procedure(client, symb, pump_data.amounts_to_buy, pump_data.prices_to_sell, amount_to_buy)
	except Exception as e:
		print('Problem encountered placing sell limit with the {} account. Error is {}'.format(user, e))


sell_limits_achieved = [0]*len(config.sell_amounts)

def cancel_limit(client, symb, id_num, position):
	global sell_limits_achieved
	try:
		client.cancel_order(symbol=symb, orderId=id_num)
	except:
		sell_limits_achieved[position] = 1

def sell_limit_procedure(client, symb, amounts_to_buy, prices_to_sell, total_amount):
	num_of_orders = len(config.sell_amounts)
	ids = []
	
	try:
		for order in range(num_of_orders):
			id_num = client.order_limit_sell(symbol=symb, quantity=amounts_to_buy[order], price=prices_to_sell[order])['orderId']
			ids.append(id_num)
	except Exception as e:
		print(e)
		raw_input('> Could not place sell limit, press enter to market sell"')
		client.order_market_sell(symbol=symb, quantity=total_amount)

	raw_input('> Press enter to cancell orders and market sell')

	all_t = []
	for order in range(num_of_orders-1, -1, -1):
		t = threading.Thread(target=cancel_limit, args=(client, symb, ids[order], order,))
		t.start()
		all_t.append(t)

	for thr in all_t:
		thr.join()

	amount_left_to_sell = total_amount

	for order in range(num_of_orders):
		if sell_limits_achieved[order]:
			amount_left_to_sell -= amounts_to_buy[order]

	try:
		client.order_market_sell(symbol=symb, quantity=amount_left_to_sell)
	except:
		print("COULD NOT MARKET SELL, DO IT MANUALLY!!")
		

def is_pump_near(next_pump, min_margin, sec_margin):
	
	year = next_pump['year']
	month = next_pump['month']
	day = next_pump['day']
	hour = next_pump['hour']
	minute = next_pump['min']
	second = next_pump['sec']

	date_pump = datetime(year, month, day, hour, minute, second)
	date_margin = timedelta(seconds = sec_margin + min_margin*60)
	if  date_pump - date_margin < datetime.now():
		return True
	return False