from handler import *
import passwords
import core

accounts = {
	"user@example.com": {
		"server": "mail.example.com",
		"type": "ssl",
		"port": 993,
		"username": "user",
		"password": "example.com",
	}
}

# Decrypt passwords and store in accounts dictionary.
passwords.readPasswords("passwords.crypt", accounts)

# Configure handler.
h = Handler()
# Mark all unread messages as read.
h.add(unread().mark(read = True))

# Create core object.
c = core.Core(accounts, h)
# Do bootup on all messages.
c.bootup()
# Start normal operation.
c.run()
