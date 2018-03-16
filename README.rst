Cryptogini Binance
==================
**Pump Bot for Binance exchange**

Configuration
---------------
In ``config.py`` change the following parameters before the pump::

	next_pump = {'year': 2018, 'month': 2, 'day': 3, 'hour' : 11, 'min' : 18, 'sec' : 30, ...}

Place the exact date of the pump.::

	perc_to_pump = 0.9 

	pump_percentage = 0.03	
	pump_change_abort = 0.06 

In the following order, the % of the total balance which will be used,
the % which will trigger the bot to buy a coin and the % of increase
to avoid buying the coin.::

	sell_amounts = [0.4, 0.3, 0.3] 
	price_amounts = [1.12, 1.15, 1.18]

Divide the sell limits, you can place the number of sell_amounts you want.
Make sure the sum of all equals to 1. The price amounts represent the % of 
gain which every sell limit will be placed (1.10 = 10%). 

Finally, 30 min before the pump find all the coins with 1000 btc of volume
or more and insert them in the excluded coins.::

	excluded_coins =   ['ICX', 'ETH', 'LSK', 'TRX', 'VEN', 'ELF']
