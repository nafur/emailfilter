import imap
import select

class Core:
	def __init__(self, accounts, handler):
		self.__accounts = accounts
		self.__handler = handler
		self.__clients = {}
		self.__connect()
		self.__flag = "X-Emailfilter-Seen"
	
	def __connect(self):
		for a in self.__accounts:
			self.__clients[a] = imap.runClient(a, self.__accounts[a])
	
	def __del__(self):
		for a in self.__accounts:
			del self.__clients[a]
	
	def client(self, account):
		if account == None: return None
		return self.__clients[account]
	
	def resetFlags(self):
		for c in self.__clients:
			for m in self.__clients[c].searchFlagged(self.__flag):
				m.unflag(self.__flag)
	
	def backup(self, account, mbox):
		self.client(account).dumpMbox(mbox)
	
	def restore(self, account, mbox, path):
		self.client(account).restoreMbox(mbox, path)
	
	def run(self):
		print("Entering main loop...")
		sockets = {}
		for c in self.__clients:
			sockets[ self.__clients[c].socket() ] = self.__clients[c]
		active = sockets.keys()
		
		while True:
			print(sockets)
			for s in active:
				for m in sockets[s].searchUnflagged(self.__flag):
					self.__handler.execute(m, self)
					m.flag(self.__flag)

			for c in self.__clients:
				self.__clients[c].idle()
			active = select.select(sockets.keys(), [], [])[0]
			for c in self.__clients:
				self.__clients[c].idle_done()

