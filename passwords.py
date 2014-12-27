#!/usr/bin/python
"""
This module contains everything related to passwords:
- obtaining a password from the user,
- encrypting and decrypting files,
- parsing json dictionaries and storing the passwords in an account dictionary.

Usually, you only need to call readPasswords(filename, accounts) from the
outside. This will ask the user for a password, decrypt the file and store
the decrypted passwords in the accounts dictionary.

This file can also be used as a stand-alone utility to encrypt and decrypt
files to actually change the password file.
"""

import getpass
import hashlib
import random
import simplejson
import struct
import sys

from Crypto.Cipher import AES
from Crypto.Protocol import KDF

def readCryptedFile(filename):
	"""Read file and extract IV, length and encrypted data."""
	f = open(filename, "r")
	iv = f.read(16)
	salt = f.read(16)
	len = struct.unpack('<Q', f.read(struct.calcsize('Q')))[0]
	data = f.read()
	return (data,len,iv,salt)

def writeCryptedFile(filename, data, length, iv, salt):
	"""Write IV, length and encrypted data to file."""
	f = open(filename, "w")
	f.write(iv)
	f.write(salt)
	f.write(struct.pack('<Q', length))
	f.write(data)

def getKey(salt = None):
	"""Obtains a password from the user and creates an AES key from it."""
	# Use SHA256 to create a 256bit key for AES
	password = getpass.getpass("Password: ")
	if salt == None:
		salt = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
		key = KDF.PBKDF2(password, salt)
		return (key, salt)
	else:
		return KDF.PBKDF2(password, salt)

def decrypt(filename):
	"""Decrypts the content of the file."""
	data,len,iv,salt = readCryptedFile(filename)
	dec = AES.new(getKey(salt), AES.MODE_CBC, IV=iv)
	return dec.decrypt(data)[:len]
		
def encrypt(source, dest):
	"""Encrypts the source file and stores the result in the destination file."""
	plain = open(source, "r").read()
	length = len(plain)
	plain += ' ' * (16 - length % 16)
	iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
	key, salt = getKey()
	enc = AES.new(key, AES.MODE_CBC, IV=iv)
	writeCryptedFile(dest, enc.encrypt(plain), length, iv, salt)

def readPasswords(filename, accounts):
	"""Decrypts the passwords and stores them in the given accounts dictionary."""
	j = decrypt(filename)
	p = simplejson.loads(j)
	for a in accounts:
		pid = accounts[a]["password"]
		if pid not in p:
			print("Password configured for " + a + " was not found in the passwords file.")
		else:
			accounts[a]["password"] = p[pid]

if __name__ == "__main__":
	if len(sys.argv) < 4:
		print("Usage:")
		print("Encrypt: " + sys.argv[0] + " enc <plain file> <crypted file>")
		print("Decrypt: " + sys.argv[0] + " dec <crypted file> <plain file>")
		sys.exit(1)

	mode = sys.argv[1]
	src = sys.argv[2]
	dest = sys.argv[3]
	
	if mode == "enc":
		encrypt(src, dest)
	elif mode == "dec":
		plain = decrypt(src)
		open(dest, "w").write(plain)
	else:
		print("Invalid mode " + mode)
