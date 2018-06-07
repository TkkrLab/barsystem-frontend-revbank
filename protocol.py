import requests, json, time

class ApiError(Exception):
	def __init__(self, error):
		if 'message' in error:
			message = error['message']
		else:
			message = error
		if 'code' in error:
			code = error['code']
		else:
			code = -1
		super().__init__(message)

class RpcClient:
	def __init__(self, uri="http://127.0.0.1:9876", apiUser="", apiSecret=""):
		self._uri = uri
		self._apiUser = apiUser
		self._apiSecret = apiSecret
		
	def _request(self, method, params):
		id = round(time.time())
		data = {"jsonrpc":"2.0", "id": id, "method": method, "params": params}
		request = requests.post(self._uri, auth=(self._apiUser, self._apiSecret), json=data)
		data = json.loads(request.text)
		if (data['id']!=id):
			raise ApiError("API returned incorrect id!")
		if (data['jsonrpc']!="2.0"):
			raise ApiError("Invalid response")
		if 'error' in data:
			raise ApiError(data['error'])
		if 'result' in data:
			return data['result']
		return None
	
	def ping(self):
		try:
			if self._request("ping", []) == "pong":
				return True
		except:
			pass
		return False
	
	def stock(self):
		return self._request("products/stock", [])
	
	def blame(self):
		return self._request("persons/blame", [-13.37])
	
	def productFind(self, search):
		return self._request("products/find", [search])

	def productDetails(self, search):
		return self._request("products/details", [search])
	
	def personFind(self, search):
		return self._request("persons/find", [search])

	def personDetails(self, search):
		return self._request("persons/details", [search])
	
	def personSaldoSet(self, id, saldo):
		return self._request("persons/saldo/set", [id, saldo])
	
	def journalList(self, f, t, amount = 5):
		return self._request("journal/list", [f, t, amount])
	
	def journalAddProduct(self, source, target, amount, product, product_count):
		return self._request("journal/add", [source, target, amount, product, product_count])

