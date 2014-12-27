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
	
	def check(self, msg):
		for f in self.__filters:
			if not f(msg):
				return False
		return True
		
	def execute(self, msg):
		if not self.check(msg): return False
		for a in self.__actions:
			a(msg)
		return True

	### filters
	def __match(self, regex):
		r = re.compile(regex)
		return lambda s: regex.match(s)

	def filter(self, f):
		return HandlerRule(self.__filters + [f], self.__actions)

	def flags(self, read = None):
		f = lambda m: read == None or m.read == read
		return self.filter(f)
	
	def subject(self, regex):
		f = lambda m: self.__match(regex, m.subject) != None
		return self.filter(f)
	
	def fromto(self, regex):
		f = lambda m: self.__match(regex, m.From) or  self.__match(regex, m.to)
		return self.filter(f)
	
	### actions
	def action(self, a):
		return HandlerRule(self.__filters, self.__actions + [a])

	def mark(self, read = None):
		a = lambda m: m.setRead(read)
		return self.action(a)
	
	def move(self, account = None, path = None):
		a = lambda m: m.move(path, account)
		return self.action(a)

def all():
	"""Returns a handler that catches all mails."""
	return HandlerRule()

def unread():
	"""Returns a handler that catches all unread mails."""
	return HandlerRule().flags(read = False)

class Handler:
	def __init__(self):
		self.__handlers = []
	def add(self, h):
		self.__handlers.append(h)
	def execute(self, m):
		for h in self.__handlers:
			if h.execute(m): return True
		return False
