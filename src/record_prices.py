from datetime import datetime
import time, os

#--WRITE FILE--#
def get_time_stamp():
	return datetime.now().strftime("%H:%M:%S:") + '{:02d}'.format(int(time.time()*100)%100)
def record_coin_price(price, symb):

	path = './records' + './' + str(symb) + '.txt'
	with open(path, 'a+') as f: #To append text in an existing file
		f.seek(0,2)
		time = get_time_stamp()
		text = time + " -> " + str(price) + '\n'
		f.write(text)
		f.flush()

def retain_coin_price(price, retained_coin_info, symb):
	time = get_time_stamp()
	text = time + " -> " + str(price) + '\n'
	retained_coin_info.append(text)

def dump_retained_prices(retained_coin_info, symb):
	path = './records' + './' + str(symb) + '.txt'
	for line in retained_coin_info:
		with open(path, 'a+') as f: 
			f.seek(0,2)
			f.write(line)
			f.flush()
	retained_coin_info[:] = [] #Reset the array, the information has been dumped

#--READ FILE--#
def get_number_of_lines(symb):
	filename = './records' +  './' + str(symb) + '.txt'
	i = 0
	if os.path.isfile(filename): 
		with open(filename, 'r') as f:
			for a, b in enumerate(f):
				i += 1
	return i

def get_line(symb, line_numb):
	path =  './records' +  './' + str(symb) + '.txt'
	return linecache.getline(path, line_numb)[15:]

def find_line_from_time(symb, time):
	filename = './records' +  './' + str(symb) + '.txt'
	if os.path.isfile(filename): 
		with open(filename, 'r') as f:
			for a, line in enumerate(f):
				if line[:11] == time:
					return a

def print_all_file(symb):
	filename = './records' +  './' + str(symb) + '.txt'
	if os.path.isfile(filename): 
		with open(filename, 'r') as f:
			for line in f:
				print (line)

