import os
import sys
import importlib, inspect

from requestswrapper import RequestsWrapper

import argparse
import prettyprinter

class test01:
	def __init__(self):
		self.desc = "Test #1 - GET"

	def execute(self, VERBOSE=False):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executeGet("https://httpbin.org/")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == False:
			print ("Error: Request unsuccessful")
			prettyprinter.pprint(response)
			return "FAIL"
		if response['result']['text'] == '' or \
			response['result']['text'].find('SwaggerUIBundle.plugins.DownloadUrl') < 0 or \
			response['result']['result'].find('SwaggerUIBundle.plugins.DownloadUrl') < 0 or \
			response['result']['status_code'] != 200:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test02:
	def __init__(self):
		self.desc = "Test #2 - GET with Args"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executeGet("https://httpbin.org/", {'arg1' : 202, 'arg2' : 'foo'})
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == False:
			print ("Error: Request unsuccessful")
			prettyprinter.pprint(response)
			return "FAIL"
		if response['result']['text'] == '' or \
			response['result']['text'].find('SwaggerUIBundle.plugins.DownloadUrl') < 0 or \
			response['result']['result'].find('SwaggerUIBundle.plugins.DownloadUrl') < 0 or \
			response['result']['status_code'] != 200:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test03:
	def __init__(self):
		self.desc = "Test #3 - POST with JSON"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executePost("https://httpbin.org/post", RO.MODE_JSON, {'arg1' : 202, 'arg2' : 'foo'})
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == False or \
			type(response['result']['result']) != type({}) or \
			response['result']['result']['url'] != 'https://httpbin.org/post':
				print ("Error: Test Failure")
				prettyprinter.pprint(response)
				return "FAIL"
		return "OK"

class test04:
	def __init__(self):
		self.desc = "Test #4 - POST with DATA"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executePost("https://httpbin.org/post", RO.MODE_DATA, {'arg1' : 202, 'arg2' : 'foo'})
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == False or \
			type(response['result']['result']) != type('') or \
			response['result']['result'].find('https://httpbin.org/post') < 0:
				print ("Error: Test Failure")
				prettyprinter.pprint(response)
				return "FAIL"
		return "OK"

class test05:
	def __init__(self):
		self.desc = "Test #5 - POST a File"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		FH = open("testdata.dat", "rb")
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executePost("https://httpbin.org/post", RO.MODE_FILES, {'upload_file' : FH})
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == False:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test06:
	def __init__(self):
		self.desc = "Test #6 - HEAD"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executeHead("https://httpbin.org/")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['result']['page_size'] == 0:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test07:
	def __init__(self):
		self.desc = "Test #7 - HEAD with Bad URL"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executeHead("https://httpbin.org/badurlnohead")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == True:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test08:
	def __init__(self):
		self.desc = "Test #8 - OPTIONS"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executeOptions("https://httpbin.org/")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == False or \
			set(response['result']['allowed_verbs']) != set(['GET', 'OPTIONS', 'HEAD']) or \
			set(response['result']['allowed_methods']) != set(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']):
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test09:
	def __init__(self):
		self.desc = "Test #9 - GET Common Errors"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		for CODE in [404, 403, 500]:
			if VERBOSE:
				print ("Get a %d code" % CODE)
			response = RO.executeGet("https://httpbin.org/status/%d" % CODE)
			if VERBOSE:
				print ("Response from library:")
				print ("%s" % '-' * 60)
				prettyprinter.pprint(response)
				print ("%s" % '-' * 60)
			if response['success'] == True:
				print ("Error: Test Failure")
				prettyprinter.pprint(response)
				return "FAIL"
		return "OK"

class test10:
	def __init__(self):
		self.desc = "Test #10 - POST Common Errors"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		for CODE in [404, 403, 500]:
			if VERBOSE:
				print ("Get a %d code" % CODE)
			response = RO.executePost("https://httpbin.org/status/%d" % CODE, RO.MODE_JSON)
			if VERBOSE:
				print ("Response from library:")
				print ("%s" % '-' * 60)
				prettyprinter.pprint(response)
				print ("%s" % '-' * 60)
			if response['success'] == True:
				print ("Error: Test Failure")
				prettyprinter.pprint(response)
				return "FAIL"
		return "OK"

class test11:
	def __init__(self):
		self.desc = "Test #11 - DELETE"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executeDelete("https://httpbin.org/delete")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == False:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test12:
	def __init__(self):
		self.desc = "Test #12 - DELETE with Bad URL"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executeDelete("https://httpbin.org/deletebadurl")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == True:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test13:
	def __init__(self):
		self.desc = "Test #13 - PATCH"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executePatch("https://httpbin.org/patch")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == False:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test14:
	def __init__(self):
		self.desc = "Test #14 - PATCH with Bad URL"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executePatch("https://httpbin.org/patchbadurl")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == True:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test15:
	def __init__(self):
		self.desc = "Test #15 - PUT"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executePut("https://httpbin.org/put")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == False:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"

class test16:
	def __init__(self):
		self.desc = "Test #16 - PUT with Bad URL"

	def execute(self, VERBOSE):
		print ("Begin %s" % self.desc)
		RO = RequestsWrapper.RequestsWrapper()
		response = RO.executePut("https://httpbin.org/putbadurl")
		if VERBOSE:
			print ("Response from library:")
			print ("%s" % '-' * 60)
			prettyprinter.pprint(response)
			print ("%s" % '-' * 60)
		if response['success'] == True:
			print ("Error: Test Failure")
			prettyprinter.pprint(response)
			return "FAIL"
		return "OK"


TEST_TOC = {}
for name, cls in inspect.getmembers(importlib.import_module(__name__), inspect.isclass):
	TEST_TOC[name] = {}
	OBJ = globals()[name]()
	TEST_TOC[name]['desc'] = OBJ.desc
	TEST_TOC[name]['obj'] = OBJ


parser = argparse.ArgumentParser()
for TEST in TEST_TOC.keys():
	parser.add_argument('--%s' % TEST, help=TEST_TOC[TEST]['desc'], action="store_true")
parser.add_argument('--all', help="ALL Tests", action="store_true")
parser.add_argument('--verbose', help="Verbose mode", action="store_true")
args = parser.parse_args()
ARGS = vars(args)

for TEST in TEST_TOC.keys():
	if ARGS[TEST] == True:
		result = TEST_TOC[TEST]['obj'].execute(args.verbose)
		if result == "OK":
			sys.exit(0)
		else:
			sys.exit(1)

if args.all:
	CNT = 0
	ERR = 0
	for TEST in TEST_TOC.keys():
		CNT += 1
		result = TEST_TOC[TEST]['obj'].execute(args.verbose)
		if result == "OK":
			continue
		else:
			ERR += 1
	if ERR > 0:
		print ("%d test of %d had an error result!" % (ERR, CNT))
		sys.exit(1)
	else:
		print ("%d tests run successfully" % CNT)
		sys.exit(0)

print ("No tests selected!")
parser.print_help(sys.stderr)
sys.exit(1)