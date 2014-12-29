"""
This class represents a set of filters and actions.
If a mail that is processed passes all filters, all the actions are performed.

It provides generic routines filter() and action().
Both take a single argument, a function expecting an Message as single argument.
The filter function shall return True, if the message passed the filter.

Furthermore, convenience functions are provided for common tasks.
For example: subject(), fromto(), mark(), move(), ...
"""

import re

class HandlerRule:
	def __init__(self, filters = [], actions = []):
		self.__filters = filters
		self.__actions = actions
	
	def check(self, msg, core):
		for f in self.__filters:
			if not f(msg, core):
				return False
		return True
		
	def execute(self, msg, core):
		if not self.check(msg, core): return False
		for a in self.__actions:
			a(msg, core)
		return True

	### filters
	def __match(self, regex):
		r = re.compile(regex)
		return lambda s: r.match(s)

	def filter(self, f):
		return HandlerRule(self.__filters + [f], self.__actions)
	
	def account(self, account):
		f = lambda m, c: m.imap().name() == account
		return self.filter(f)

	def flags(self, seen = None):
		f = lambda m, c: seen == None or m.isflagged("\\Seen") == seen
		return self.filter(f)
	
	def subject(self, regex):
		f = lambda m, c: self.__match(regex)(m["subject"]) != None
		return self.filter(f)
	
	def fromto(self, regex):
		f = lambda m, c: self.__match(regex)(m["from"]) or  self.__match(regex)(m["to"])
		return self.filter(f)
	
	### actions
	def action(self, a):
		return HandlerRule(self.__filters, self.__actions + [a])

	def mark(self, seen = None):
		a = lambda m, c: m.flag("\\Seen")
		return self.action(a)
	
	def move(self, path, account = None):
		a = lambda m, c: m.move(path, c.client(account))
		return self.action(a)

def all():
	"""Returns a handler that catches all mails."""
	return HandlerRule()

def unseen():
	"""Returns a handler that catches all unseen mails."""
	return HandlerRule().flags(seen = False)

class Handler:
	def __init__(self):
		self.__handlers = []
	def add(self, h):
		self.__handlers.append(h)
	def execute(self, m, core):
		print("Executing on \"" + str(m) + "\"")
		for h in self.__handlers:
			if h.execute(m, core): return True
		return False
