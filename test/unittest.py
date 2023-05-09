from lzma import MODE_FAST
import os
import sys

from RequestsWrapper import RequestsWrapper

import argparse
import prettyprinter


parser = argparse.ArgumentParser()
parser.add_argument('--test1', help="execute test #1 - GET", action="store_true")
parser.add_argument('--test2', help="execute test #2 - GET with Args", action="store_true")
parser.add_argument('--test3', help="execute test #3 - POST JSON", action="store_true")
parser.add_argument('--test4', help="execute test #4 - POST DATA", action="store_true")
parser.add_argument('--test5', help="execute test #5 - POST File", action="store_true")
parser.add_argument('--test6', help="execute test #6 - HEAD", action="store_true")
parser.add_argument('--test7', help="execute test #7 - HEAD Bad", action="store_true")
parser.add_argument('--test8', help="execute test #8 - OPTIONS", action="store_true")
parser.add_argument('--test9', help="execute test #9 - GET Common Errors", action="store_true")
parser.add_argument('--test10', help="execute test #10 - POST Common Errors", action="store_true")
parser.add_argument('--test11', help="execute test #11 - DELETE", action="store_true")
parser.add_argument('--test12', help="execute test #12 - DELETE BAD", action="store_true")
parser.add_argument('--test13', help="execute test #13 - PATCH", action="store_true")
parser.add_argument('--test14', help="execute test #14 - PATCH BAD", action="store_true")
parser.add_argument('--test15', help="execute test #15 - PUT", action="store_true")
parser.add_argument('--test16', help="execute test #16 - PUT BAD", action="store_true")
args = parser.parse_args()

if args.test1:
	print ("Test 1")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executeGet("https://httpbin.org/")
	#prettyprinter.pprint(response)
	assert(response['success'] == True)
	assert(response['result']['text'] != '')
	assert(response['result']['text'].find('SwaggerUIBundle.plugins.DownloadUrl') > 0)
	assert(response['result']['result'].find('SwaggerUIBundle.plugins.DownloadUrl') > 0)
	assert(response['result']['status_code'] == 200)
elif args.test2:
	print ("Test 2")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executeGet("https://httpbin.org/", {'arg1' : 202, 'arg2' : 'foo'})
	#prettyprinter.pprint(response)
	assert(response['success'] == True)
	assert(response['result']['text'] != '')
	assert(response['result']['text'].find('SwaggerUIBundle.plugins.DownloadUrl') > 0)
	assert(response['result']['result'].find('SwaggerUIBundle.plugins.DownloadUrl') > 0)
	assert(response['result']['status_code'] == 200)
elif args.test3:
	print ("Test 3")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executePost("https://httpbin.org/post", RO.MODE_JSON, {'arg1' : 202, 'arg2' : 'foo'})
	#prettyprinter.pprint(response)
	assert(response['success'] == True)
	assert(type(response['result']['result']) == type({}))
	assert(response['result']['result']['url'] == 'https://httpbin.org/post')
	#prettyprinter.pprint (response['result']['result'])
elif args.test4:
	print ("Test 4")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executePost("https://httpbin.org/post", RO.MODE_DATA, {'arg1' : 202, 'arg2' : 'foo'})
	assert(response['success'] == True)
	assert(type(response['result']['result']) == type(''))
	#prettyprinter.pprint(response)
	assert(response['result']['result'].find('https://httpbin.org/post') > 0)
	#prettyprinter.pprint (response['result']['result'])
elif args.test5:
	print ("Test 5")
	FH = open("testdata.dat", "rb")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executePost("https://httpbin.org/post", RO.MODE_FILES, {'upload_file' : FH})
	prettyprinter.pprint(response)
elif args.test6:
	print ("Test 6")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executeHead("https://httpbin.org/")
	#prettyprinter.pprint(response)
	assert(response['result']['page_size'] > 0)
elif args.test7:
	print ("Test 7")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executeHead("https://httpbin.org/badurlnohead")
	prettyprinter.pprint(response)
	assert(response['success'] == False)
elif args.test8:
	print ("Test 8")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executeOptions("https://httpbin.org/")
	prettyprinter.pprint(response)
	assert(response['success'] == True)
	assert(set(response['result']['allowed_verbs']) == set(['GET', 'OPTIONS', 'HEAD']))
	assert(set(response['result']['allowed_methods']) == set(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']))
	
elif args.test9:
	print ("Test 9")
	RO = RequestsWrapper.RequestWrapper()
	for CODE in [404, 403, 500]:
		response = RO.executeGet("https://httpbin.org/status/%d" % CODE)
		assert(response['success'] == False)
elif args.test10:
	print ("Test 10")
	RO = RequestsWrapper.RequestWrapper()
	for CODE in [404, 403, 500]:
		response = RO.executePost("https://httpbin.org/status/%d" % CODE, RO.MODE_JSON)
		assert(response['success'] == False)
elif args.test11:
	print ("Test 11")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executeDelete("https://httpbin.org/delete")
	prettyprinter.pprint(response)
	assert(response['success'] == True)
elif args.test12:
	print ("Test 12")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executeDelete("https://httpbin.org/deletebadurl")
	prettyprinter.pprint(response)
	assert(response['success'] == False)
elif args.test13:
	print ("Test 13")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executePatch("https://httpbin.org/patch")
	prettyprinter.pprint(response)
	assert(response['success'] == True)
elif args.test14:
	print ("Test 14")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executePatch("https://httpbin.org/patchbadurl")
	prettyprinter.pprint(response)
	assert(response['success'] == False)
elif args.test15:
	print ("Test 15")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executePut("https://httpbin.org/put")
	prettyprinter.pprint(response)
	assert(response['success'] == True)
elif args.test16:
	print ("Test 16")
	RO = RequestsWrapper.RequestWrapper()
	response = RO.executePut("https://httpbin.org/putbadurl")
	prettyprinter.pprint(response)
	assert(response['success'] == False)
else:
	print ("No test specified")
