
class Message:
	def __init__(self, imap, uid):
		self.__imap = imap
		self.__uid = uid
		print("uid = " + str(uid))
		#self.__msg = imap.downloadMail(uid)
		
		self.From = "Foo"
		self.to = "Bar"
		self.read = False
				
	def __str__(self):
		return str(self.__uid)
	
	def setRead(self, r):
		if r == None: return
		self.read = r
	
	def move(self, folder, account = None):
		if account == None:
			imap.copy([self.__uid], folder)
		else:
			pass
