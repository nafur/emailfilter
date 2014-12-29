import logging
import imaplib
import os
import shutil
import threading
import time
import message

def IMAPCommand(f):
	def inner(*args, **kwargs):
		status, response = f(*args, **kwargs)
		if status != "OK":
			logging.error("IMAP " + f.__name__ + " failed: " + str(status) + ", " + str(response))
			return False,None
		logging.debug("IMAP " + f.__name__ + " succeeded: " + str(status) + ", " + str(response))
		return True,response
	return inner

class IMAP:
	def __init__(self, name, account):
		self.__name = name
		self.__account = account
		if self.a("type") == "ssl":
			self.__conn = imaplib.IMAP4_SSL(self.a("server"))
		elif self.a("type") == "plain":
			self.__conn = imaplib.IMAP4(self.a("server"))
		self.__conn.login(self.a("username"), self.a("password"))
		self.__conn.select("inbox")
		self.__conn.debug = 10
	
	def __del__(self):
		self.__conn.logout()
	
	def a(self, s):
		return self.__account[s]
	
	def name(self):
		return self.__name
	
	def socket(self):
		return self.__conn.socket().fileno()

	def searchFlagged(self, flag):
		status,res = self.__conn.uid("search", None, "KEYWORD " + flag)
		return map(lambda uid: message.Message(self, uid), res[0].split())

	def searchUnflagged(self, flag):
		status,res = self.__conn.uid("search", None, "NOT KEYWORD " + flag)
		return map(lambda uid: message.Message(self, uid), res[0].split())
	
	@IMAPCommand
	def searchAll(self):
		return self.__conn.uid("search", None, "ALL")
	
	def dumpMbox(self, destination):
		logging.info("Dumping folder to " + destination)
		if not os.path.isdir(destination):
			os.mkdir(destination)
		status,all = self.searchAll()
		if not status:
			logging.error("Failed to enumerate mails.")
			return False
		for m in all[0].split():
			status,msg = self.downloadMail(m)
			if not status:
				logging.error("Failed to dump message " + str(m))
				continue
			f = open(destination + "/" + m.decode("utf-8"), "wb")
			f.write(msg[0][1])
			f.close()
	
	def restoreMbox(self, source, destination):
		logging.info("Restoring folder from " + source + " to " + destination)
		self.create(destination)
		for filename in os.listdir(source):
			f = open(source + "/" + filename, "rb")
			msg = f.read()
			f.close()
			status, resp = self.append(destination, "\\Seen", msg)
			if not status:
				logging.error("Failed to restore message " + str(filename))
	
	# IMAP Commands
	
	@IMAPCommand
	def append(self, folder, flags, msg):
		return self.__conn.append(folder, flags, imaplib.Time2Internaldate(time.time()), msg)
	
	@IMAPCommand
	def copy(self, uid, path):
		return self.__conn.uid("copy", uid, path)
	
	@IMAPCommand
	def create(self, path):
		return self.__conn.create(path)
	
	@IMAPCommand
	def expunge(self):
		return self.__conn.expunge()
	
	@IMAPCommand
	def idle(self):
		return self.__conn.idle()
	
	@IMAPCommand
	def idle_done(self):
		return self.__conn.idle_done()
	
	@IMAPCommand
	def store(self, uid, type, data):
		return self.__conn.uid("store", uid, type, data)
	
	@IMAPCommand
	def getFlags(self, uid):
		return self.__conn.uid("fetch", uid, "(FLAGS)")
	
	@IMAPCommand
	def downloadMail(self, uid):
		return self.__conn.uid("fetch", uid, "(RFC822)")

	def downloadHeader(self, uid):
		res,data = self.__conn.uid("fetch", uid, "(BODY[HEADER])")
		return data
	
	def listUnseen(self, folder):
		self.__conn.select(folder)
		res,data = self.__conn.uid("search", None, "UNSEEN")
		data = filter(lambda x: x != "", data)
		if res == "OK":
			return map(lambda x: message.Message(self, x), data)
		else:
			return []
	
	
def runClient(name, account):
	return IMAP(name, account)
