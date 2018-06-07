import sys
from protocol import RpcClient

client = RpcClient("http://127.0.0.1:9876", "python", "test")

if not client.ping():
	print("Server unavailable.")
	sys.exit(1)

while 1:
	sys.stdout.write("> ")
	sys.stdout.flush()
	i = sys.stdin.readline().replace("\r","").replace("\n","")
	#print("Searching for '"+i+"'")
	results = client.productFind(i)
	if len(results) < 1:
		results = client.personFind(i)
		if (len(results) < 1):
			print("No results.")
		else:
			print("Found a person matching your query:")
			for result in results:
				person = client.personDetails(result)
				amount = str(round(float(person['amount']),2))
				print('{0: <25}'.format(person['first_name']+" "+person['last_name'])+": "+'{0: <6}'.format("€ "+amount))
	else:
		print("Found a product matching your query:")
		for result in results:
			product = client.productDetails(result)
			mbr_pr = str(round(float(product['member_price']),2))
			std_pr = str(round(float(product['standard_price']),2))
			print('{0: <25}'.format(product['name'])+'{0: <6}'.format("€ "+mbr_pr)+" / "+'{0: <6}'.format("€ "+std_pr))

