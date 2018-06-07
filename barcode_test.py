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
		print("No results.")
	else:
		for result in results:
			products = client.productDetails(result)
			for item in products:
				mbr_pr = str(round(float(item['member_price']),2))
				std_pr = str(round(float(item['standard_price']),2))
				print('{0: <25}'.format(item['name'])+'{0: <6}'.format("€ "+mbr_pr)+" / "+'{0: <6}'.format("€ "+std_pr))

