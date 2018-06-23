import sys, time, datetime
from protocol import RpcClient

# Global variables
cart = []
lastCmd = ''

# Commands
def stock(client):
	stock = client.stock()

	print('{0: <35}'.format("Product")+'{0: <6}'.format("Stock")+'{0: <8}'.format("G-price")+'{0: <8}'.format("M-price")+'{0: <7}'.format("Worth")+'{0: <7}'.format("Exp L.")+'{0: <7}'.format("Exp H."))
	print('=============================================================================')
	for product in stock['products']:
		print('{0: <35}'.format(product['name'])+'{0: <6}'.format(str(product['stock']))+'{0: <8}'.format(str(product['standard_price']))+'{0: <8}'.format(str(product['member_price']))+'{0: <7}'.format(str(product['worth']))+'{0: <7}'.format(str(product['worth_expected_low']))+'{0: <7}'.format(str(product['worth_expected_high'])))
	print('=============================================================================')
	print('{0: <35}'.format("TOTAL")+'{0: <6}'.format(stock['stock'])+'{0: <7}'.format(stock['worth'])+'{0: <7}'.format(stock['worth_expected_low'])+'{0: <7}'.format(stock['worth_expected_high']))

	print('\n\n\n')
	
def blame(client):
	blame = client.blame()
	print('{0: <35}'.format("Nickname")+'{0: <6}'.format("Saldo"))
	print('==============================================================')
	for user in blame:
		print('{0: <35}'.format(user['nick_name'])+'{0: <6}'.format(user['amount']))
	print('==============================================================')
	
def abort():
	global cart
	cart = []
	sys.stdout.write("\r\n\u001b[31mTransaction canceled!\u001b[39m\r\n\r\n")
	
# Types
def product(client, name):
	global cart
	results = client.productFind(name)
	if len(results) > 0:
		if len(results) > 1:
			#sys.stdout.write("\r\n\u001b[31mError: multiple results for query!\u001b[39m\r\n\r\n")
			#return True
			
			sys.stdout.write("\r\n\u001b[33m=== MULTIPLE RESULTS ===\u001b[39m\r\n\r\n")
			for i in range(0,len(results)):
				product = client.productDetails(results[i])
				mbr_pr = str(round(float(product['member_price']),2))
				std_pr = str(round(float(product['standard_price']),2))
				print(str(i+1)+". "+'{0: <25}'.format(product['name'])+'{0: <6}'.format("€ "+mbr_pr)+" / "+'{0: <6}'.format("€ "+std_pr))
			try:
				choice = int(prompt(client, "\r\nPick one (or abort):"))-1
				if (choice >= 0) and (choice < len(results)):
					result = results[choice]
				else:
					print("\u001b[31mCanceled\u001b[39m")
					return True
			except:
				print("\u001b[31mCanceled\u001b[39m")
				return True
				
		else:
			result = results[0]
			
			
		cart.append(result)
			
		product = client.productDetails(result)
		mbr_pr = str(round(float(product['member_price']),2))
		std_pr = str(round(float(product['standard_price']),2))
		print("\u001b[32mAdded\u001b[39m "+product['name']+" (€ "+mbr_pr+" / € "+std_pr+")\u001b[32m to your cart.\u001b[39m")
		return True
		
	return False

def printJournalItem(client, item, showFrom=False, showTo=False):
	sender = ""
	if (showFrom):
		if not item['sender_id'] is None:
			sender = "from "
			try:
				sender += client.personDetails(int(item['sender_id']))['nick_name']
			except:
				sender += "\u001b[31mdeleted person\u001b[39m"
	if (showTo):
		if not item['recipient_id'] is None:
			if (sender != ""):
				sender += " "
			sender += "to "
			try:
				sender += client.personDetails(int(item['recipient_id']))['nick_name']
			except:
				sender += "\u001b[31mdeleted person\u001b[39m"
	product = "\u001b[31mNone\u001b[39m"
	if (item['product_id']>0):
		try:
			product = client.productDetails(item['product_id'])['name']
		except:
			product = "\u001b[31mdeleted product\u001b[39m"
	try:
		moment = datetime.datetime.fromtimestamp(int(item['moment']))
	except:
		try:
			moment = datetime.datetime.strptime(item['moment'],"%Y-%m-%dT%H:%M:%S.%fZ")
		except:
			product = "\u001b[31munknown\u001b[39m"
	print('{0: <17}'.format(moment.strftime("%d-%m-%Y %H:%M"))+" "+item['items']+"x "+'{0: <25}'.format(product)+'{0: <7}'.format("€ "+item['amount'])+" "+sender)
	#print(item)
	#print(product)

def executeTransaction(client, personId):
	global cart
	
	person = client.personDetails(personId)
	amount = float(person['amount'])
	member = int(person['member']) > 0
	
	price_source = 'standard_price'
	if member and (amount>=0):
		price_source = 'member_price'
	
	#print(person)
	
	if member and (amount<0):
		sys.stdout.write("\r\n\u001b[31mYour balance is negative, you're missing out on discount prices!!\u001b[39m\r\n")
	
	amountNew = amount
	
	print("\r\n=== TRANSACTION RECEIPT ===")
	products = {}
	
	for i in cart:
		if i in products:
			products[i]+=1
		else:
			products[i]=1
	
	total = 0	
	
	for i in products:
		product = client.productDetails(i)
		price = float(product[price_source])
		total += price*products[i]		
		print(str(products[i])+"x "+'{0: <25}'.format(product['name'])+'{0: <6}'.format("€ "+str(round(price,2))))
		client.journalAddProduct(0, personId, price*products[i], i, products[i])
	
	amountNew -= total
	
	client.personSaldoSet(personId, amountNew)
	
	print("\r\nTransaction total:\t\t€ "+str(round(total,2)))
	print("Saldo before transaction:\t€ "+str(round(amount,2)))
	print("Saldo after transaction:\t€ "+str(round(amountNew,2)))
	
	cart = []

def person(client, name):
	global cart
	results = client.personFind(name)
	if (len(results) > 0):
		if (len(results) > 1):
			sys.stdout.write("\r\n\u001b[31mError: multiple persons with same nickname!\u001b[39m\r\n\r\n")
			return True
		
		result = results[0]
		if (len(cart)<1):
			person = client.personDetails(result)
			amount = float(person['amount'])
			journal = client.journalList(0, result, 10)
			if (len(journal)>0):
				print("=== RECEIVED ===")
				for item in journal:
					printJournalItem(client, item, True, False)
				
			journal = client.journalList(result, 0, 10)
			if (len(journal)>0):
				print("=== SENT ===")
				for item in journal:
					printJournalItem(client, item, False, True)
			print("")
			print("Full name:\t"+person['first_name']+" "+person['last_name'])
			print("Saldo:\t\t"+'{0: <6}'.format("€ "+str(round(amount,2))))
		else:
			executeTransaction(client, result)
		return True
	return False

def printCart(client):
	global cart
	print("\r\n=== CART ===")
	products = {}
	
	for i in cart:
		if i in products:
			products[i]+=1
		else:
			products[i]=1
	
	mbr_total = 0
	std_total = 0
	
	for i in products:
		product = client.productDetails(i)
		mbr_pr = float(product['member_price'])
		mbr_total += mbr_pr*products[i]
		std_pr = float(product['standard_price'])
		std_total += std_pr*products[i]
		print(str(products[i])+"x "+'{0: <25}'.format(product['name'])+'{0: <6}'.format("€ "+str(round(mbr_pr,2)))+" / "+'{0: <6}'.format("€ "+str(round(std_pr,2))))
	
	print("\r\nTotal: "+'{0: <6}'.format("€ "+str(round(mbr_total,2)))+" / "+'{0: <6}'.format("€ "+str(round(std_total,2))))
	
# Shell helper functions

def help():
	print("")
	print("\u001b[103m\u001b[30m  ~~~  Welcome to the Tkkrlab barsystem  ~~~  \u001b[49m\u001b[39m")
	print("")
	print("Available commands are:")
	print(" - stock")
	print(" - blame")
	print(" - clear")
	print(" - abort")
	print(" - help")
	
def command(client, cmd):
	global lastCmd
	lastCmd = cmd
	if (cmd=="stock"):
		stock(client)
		return True
	elif (cmd=="blame"):
		blame(client)
		return True
	elif (cmd=="cls") or (cmd=="clear"):
		clear()
		return True
	elif (cmd=="abort"):
		abort()
		return True
	elif (cmd=="help"):
		help()
		return True
	elif (cmd=="cyber"):
		print("\u001b[103m\u001b[30m         \u001b[49m\u001b[39m")
		print("\u001b[103m\u001b[30m  CYBER  \u001b[49m\u001b[39m")
		print("\u001b[103m\u001b[30m         \u001b[49m\u001b[39m")
		return True
	#print("? '"+cmd+"'")
	lastCmd = ''
	return False	

def clear():
	sys.stdout.write("\033c")

def prompt(client, prompt=">",header=False, headerCart=False):
	if (header):
		#clear()
		sys.stdout.write("\r\n\u001b[33mTkkrlab\u001b[39m barsystem\r\n")
		
	if (headerCart):
		if len(cart) > 0:
			printCart(client)
		print("")
		
	sys.stdout.write("\u001b[36m"+prompt+"\u001b[39m ")
	sys.stdout.flush()
	i = sys.stdin.readline().replace("\r","").replace("\n","")
	print("")
	sys.stdout.flush()
	return i

# Main function

def main():
	global lastCmd
	showHeader = True
	client = RpcClient("http://127.0.0.1:9876", "python", "test")
	while 1:
		while not client.ping():
			print("Server unavailable. Reconnecting in 2 seconds...")
			time.sleep(2)
		
		i = prompt(client, "Command, user or product? >",showHeader,True)
		showHeader = True
		
		if (len(i)>0):
			if not command(client, i):
				if not person(client, i):
					if not product(client, i):
						print("\u001b[31mError: unknown command, user or product.\u001b[39m")
						showHeader = False
					else:
						showHeader = False
				else:
					showHeader = False
			else:
				if ((lastCmd == 'clear') or (lastCmd == 'cls')):
					showHeader = True
				else:
					showHeader = False
				

main()
