import email.parser
import imaplib
import sys

class Message:
	def __init__(self, imap, uid):
		self.__imap = imap
		assert(uid != None)
		self.__uid = uid
		h = self.__imap.downloadHeader(uid)[0][1]
		p = email.parser.BytesParser()
		self.__msg = p.parsebytes(h, headersonly=True)
		self.__flags = self.__imap.getFlags(self.__uid)[1]
				
	def __str__(self):
		return str(self.__msg["subject"])
	
	def __getitem__(self, s):
		return self.__msg[s]
	
	def uid(self):
		return self.__uid
	
	def imap(self):
		return self.__imap
	
	def isflagged(self, flag):
		return flag in self.__flags
	
	def flag(self, flag):
		return self.__imap.store(self.__uid, "+FLAGS", flag)

	def unflag(self, flag):
		return self.__imap.store(self.__uid, "-FLAGS", flag)
	
	def move(self, folder, account = None):
		if account == None:
			status,r = self.__imap.copy(self.__uid, folder)
			if status == False: return False
		else:
			status,msg = self.__imap.downloadMail(self.__uid)
			if status == False: return False
			status,r = account.append(folder, "()", msg[0][1])
			if status == False: return False
		self.flag("\\Deleted")
		self.__imap.expunge()
