import imaplib2
import threading
import message

class IMAP:
	def __init__(self, account):
		self.__account = account
		if self.a("type") == "ssl":
			self.__conn = imaplib2.IMAP4_SSL(self.a("server"))
		elif self.a("type") == "plain":
			self.__conn = imaplib2.IMAP4(self.a("server"))
		self.__conn.login(self.a("username"), self.a("password"))
		self.__conn.select("inbox")

	
	def __del__(self):
		self.__conn.logout()
	
	def a(self, s):
		return self.__account[s]
	
	def __run(self):
		#print(self.listAll("INBOX/gustav"))
		pass
	
	def run(self):
		threading.Thread(target = self.__run).start()
	
	def downloadMail(self, uid):
		res,data = self.__conn.uid("fetch", uid, "(RFC822)")
		return data
	
	def putMail(self, folder, mail):
		self.__conn.append(folder, None, None, mail)
	
	def listUnseen(self, folder):
		self.__conn.select(folder)
		res,data = self.__conn.uid("search", None, "UNSEEN")
		data = filter(lambda x: x != "", data)
		if res == "OK":
			return map(lambda x: message.Message(self, x), data)
		else:
			return []
	
	def listAll(self, folder):
		self.__conn.select(folder)
		return self.__conn.uid("search", None, "ALL")
	
def runClient(account):
	i = IMAP(account)
	i.run()
	return i
