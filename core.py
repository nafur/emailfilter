import imap

class Core:
	def __init__(self, accounts, handler):
		self.__accounts = accounts
		self.__handler = handler
		self.__clients = {}
		self.__connect()
	
	def __connect(self):
		for a in self.__accounts:
			self.__clients[a] = imap.runClient(self.__accounts[a])
	
	def __destroy__(self):
		for a in self.__accounts:
			del self.__clients[a]
	
	def __idleCallback(self, client, messages):
		for m in messages:
			self.__handler.execute(m)
		client.idle(lambda m: self.__idleCallback(client, m))
	
	def bootup(self, handler = None):
		for c in self.__clients.values():
			for m in c.all():
				if handler == None or handler.check(m):
					self.__handler.execute(m)
	
	def run(self, accounts):
		for c in self.__clients.values():
			c.idle(lambda m: self.__idleCallback(c, m))
