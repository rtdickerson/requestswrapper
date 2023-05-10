import os
import sys
from http import HTTPStatus
import prettyprinter 

import requests 

class RequestsWrapper(object):
	"""
	The RequestsWrapper class is a convenience class that wrappers the python requests library.  Making calls and handling cookies, etc.
	can require a lot of overhead and this class simplifies that.
	The class is derived from object, so it can be subclasses to customize into different uses.
	"""

	def __init__(self, PROXIES=None):
		'''
		Initialization.  You can customize headers here.
		'''
		self.PROXIES = PROXIES
		self.SESSION = requests.Session()
		self.SESSION.proxies = PROXIES
		self.HEADERS = {
			'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0',
			'Accept' : 'text/html,application/xhtml+xml,application/xml;application/json;q=0.9,*/*;q=0.8'
		}
		self.REDIRECTS = True
		self.AUTH = None
		self.CERT = None
		self.COOKIES = None 
		self.STREAM = False
		self.TIMEOUT = None
		self.VERIFY = True
		self.MODE_JSON = 0
		self.MODE_DATA = 1
		self.MODE_FILES = 2
		self.COOKIEJAR = requests.cookies.RequestsCookieJar()
		self.RETURN_AS_JSON = False

	def addHeader(self, KEY, VAL):
		"""
		Add a custom header to the global header list.

		KEY - The Header Key like 'User-Agent'
		VAL - The value to set.
		"""
		self.HEADERS[KEY] = VAL

	def addCookie(self, cookiename, key, DOMAIN, PATH):
		"""
		Add a custom cookie
		"""
		self.COOKIEJAR.set(cookiename, key, DOMAIN, PATH)

	def returnError(self, ERRMSG, ERRDATA=None):
		'''
		This convenience function ensures error responses follow the same format.
		'''
		return {'success' : False, 'error' : ERRMSG, 'details' : ERRDATA}

	def requestExceptionHandler(self, ex, url, details):
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		# Create the basic response
		response = {}
		response['success'] = False
		response['url'] = url
		response['file'] = fname
		response['type'] = exc_type
		response['lineno'] = exc_tb.tb_lineno
		response['url'] = url
		response['details'] = details

		if type(ex) == requests.ConnectionError:
			response['error'] = "Connection error attempting GET"
			response['request'] = ex.request
			response['response'] = ex.response
			return response
		elif type(ex) == requests.exceptions.Timeout:
			response['error'] = "Timeout error attempting GET"
			response['request'] = ex.request
			response['response'] = ex.response
			return response
		elif type(ex) == requests.exceptions.TooManyRedirects:
			response['error'] = "Invalid URL"
			response['request'] = ex.request
			response['response'] = ex.response
			return response
		elif type(ex) == requests.ReadTimeout:
			response['error'] = "Read Timeout"
			response['request'] = ex.request
			response['response'] = ex.response
			return response
		elif type(ex) == requests.JSONDecodeError:
			response['error'] = "JSON Decode Error"
			response['request'] = ex.request
			response['response'] = ex.response
			return response
		elif type(ex) == requests.RequestException:
			response['error'] = "Generic Request Exception"
			response['request'] = ex.request
			response['response'] = ex.response
			return response
		else:
			# Unhandled exception, raise
			raise ex

	def returnSuccess(self, RETURN):
		'''
		This convenience function ensures success responses follow the same format.
		'''
		return {'success' : True, 'result' : RETURN}

	
	def executeGet(self, URL, ARGLIST=None):
		'''
		This function executes an HTTP GET request.  It can handle a single URL, or the URL can have an argument list passed
		as a python DICT to append the ?key=val&key2=val2.
		'''
		OPTS = {
			'allow_redirects' : self.REDIRECTS,
			'auth' : self.AUTH,
			'cert' : self.CERT,
			'cookies' : self.COOKIEJAR,
			'headers' : self.HEADERS,
			'stream' : self.STREAM,
			'timeout' : self.TIMEOUT,
			'verify' : self.VERIFY,
		  }
		try:
			if ARGLIST == None:
				webresult = self.SESSION.get(URL, **OPTS)
			else:
				webresult = self.SESSION.get(URL, params=ARGLIST, **OPTS)
		except Exception as ex:
			return self.requestExceptionHandler(ex, URL, {'arglist' : ARGLIST})

		if not webresult.status_code in [200]:
			return self.returnError("HTTP response %d - %s" % (webresult.status_code, HTTPStatus(webresult.status_code).phrase),
					{'url' : URL, 'history' : webresult.history})
		RET = {}
		RET['headers'] = webresult.headers
		RET['text'] = webresult.text
		RET['status_code'] = webresult.status_code
		RET['url'] = webresult.url
		RET['history'] = webresult.history

		if self.RETURN_AS_JSON == True:
			try:
				RESULT = webresult.json()
			except Exception as ex:
				return self.returnError('Error converting response to JSON', { 'url' : URL, 'history' : webresult.history,
									'raw' : webresult.content, 'text' : webresult.text})
		else:
			RESULT = webresult.text
		RET['result'] = RESULT
		return self.returnSuccess(RET)

	def executePost(self, URL, MODE, POSTDATA=None):
		'''
		This function executes an HTTP POST request.  It can handle a single URL, or the URL can have POST data.  Given you
		can post a JSON, or DATA, or a file, this function handles all 3.
		
		There are 3 modes defined in the class:
			MODE_JSON : POSTDATA is sent using the json= keyword
			MODE_DATA : POSTDATA is sent using the data= keyword
			MODE_FILES : POSTDATA is sent using a DICT and the files= keyword
		'''
		OPTS = {
			'allow_redirects' : self.REDIRECTS,
			'auth' : self.AUTH,
			'cert' : self.CERT,
			'cookies' : self.COOKIEJAR,
			'headers' : self.HEADERS,
			'stream' : self.STREAM,
			'timeout' : self.TIMEOUT,
			'verify' : self.VERIFY,
		  }
		if MODE == self.MODE_JSON:
			OPTS['json'] = POSTDATA
			RETURN_JSON = True
		elif MODE == self.MODE_DATA:
			OPTS['data'] = POSTDATA
			RETURN_JSON = False
		elif MODE == self.MODE_FILES:
			OPTS['files'] = POSTDATA
			RETURN_JSON = True
		else:
			return [False, "Unvalid value %d passed on executePost" % MODE]

		try:
			webresult = self.SESSION.post(URL, OPTS)
		except Exception as ex:
			return self.requestExceptionHandler(ex, URL, {'arglist' : ARGLIST, 'mode' : MODE})

		if not webresult.status_code in [200]:
			return self.returnError("HTTP response %d - %s" % (webresult.status_code, HTTPStatus(webresult.status_code).phrase),
					{'url' : URL, 'history' : webresult.history})

		RET = {}
		RET['headers'] = webresult.headers
		RET['text'] = webresult.text
		RET['status_code'] = webresult.status_code

		if RETURN_JSON == True:
			try:
				RESULT = webresult.json()
			except Exception as ex:
				return self.returnError('Error converting response to JSON', { 'url' : URL, 'history' : webresult.history,
									'raw' : webresult.content, 'text' : webresult.text})
		else:
			RESULT = webresult.text
		RET['result'] = RESULT
		return self.returnSuccess(RET)


	def executeHead(self, URL, ARGLIST=None):
		'''
		This function executes an HTTP HEAD request.  It can handle a single URL, or the URL can have an argument list passed
		as a python DICT to append the ?key=val&key2=val2.
		'''
		OPTS = {
			'allow_redirects' : self.REDIRECTS,
			'auth' : self.AUTH,
			'cert' : self.CERT,
			'cookies' : self.COOKIEJAR,
			'headers' : self.HEADERS,
			'stream' : self.STREAM,
			'timeout' : self.TIMEOUT,
			'verify' : self.VERIFY,
		  }
		try:
			if ARGLIST == None:
				webresult = self.SESSION.head(URL, **OPTS)
			else:
				webresult = self.SESSION.head(URL, param=ARGLIST, **OPTS)
		except Exception as ex:
			return self.requestExceptionHandler(ex, URL, {'arglist' : ARGLIST})

		if not webresult.status_code in [200]:
			return self.returnError("HTTP response %d - %s" % (webresult.status_code, HTTPStatus(webresult.status_code).phrase),
					{'url' : URL, 'history' : webresult.history})
		RET = {}
		RET['headers'] = webresult.headers
		RET['text'] = webresult.text
		RET['status_code'] = webresult.status_code
		VS = webresult.headers.get('Content-Length', '0')
		RET['page_size'] = int(VS)
		return self.returnSuccess(RET)

	def executeOptions(self, URL, ARGLIST=None):
		'''
		This function executes an HTTP OPTIONS request.  It can handle a single URL, or the URL can have an argument list passed
		as a python DICT to append the ?key=val&key2=val2.
		'''
		OPTS = {
			'allow_redirects' : self.REDIRECTS,
			'auth' : self.AUTH,
			'cert' : self.CERT,
			'cookies' : self.COOKIEJAR,
			'headers' : self.HEADERS,
			'stream' : self.STREAM,
			'timeout' : self.TIMEOUT,
			'verify' : self.VERIFY,
		  }
		try:
			if ARGLIST == None:
				webresult = self.SESSION.options(URL, **OPTS)
			else:
				webresult = self.SESSION.options(URL, param=ARGLIST, **OPTS)
		except Exception as ex:
			return self.requestExceptionHandler(ex, URL, {'arglist' : ARGLIST})

		if not webresult.status_code in [200]:
			return self.returnError("HTTP response %d - %s" % (webresult.status_code, HTTPStatus(webresult.status_code).phrase),
					{'url' : URL, 'history' : webresult.history})
		RET = {}
		RET['headers'] = webresult.headers
		RET['text'] = webresult.text
		RET['status_code'] = webresult.status_code
		WS = webresult.headers.get('Allow', None)
		if WS == None:
			RET['allowed_verbs'] = []
		else:
			RET['allowed_verbs'] = [PART.strip() for PART in WS.split(',')]
#			for PART in WS.split(','):
#				RET['allowed_verbs'].append(PART.strip())
		RET['allowed_origin'] = webresult.headers.get('Access-Control-Allow-Origin', None)
		WS = webresult.headers.get('Access-Control-Allow-Methods', None)
		if WS == None:
			RET['allowed_methods'] = []
		else:
			RET['allowed_methods'] = [PART.strip() for PART in WS.split(',')]
		return self.returnSuccess(RET)

	def executeDelete(self, URL, ARGLIST=None):
		'''
		This function executes an HTTP DELETE request.  It can handle a single URL, or the URL can have an argument list passed
		as a python DICT to append the ?key=val&key2=val2.
		'''
		OPTS = {
			'allow_redirects' : self.REDIRECTS,
			'auth' : self.AUTH,
			'cert' : self.CERT,
			'cookies' : self.COOKIEJAR,
			'headers' : self.HEADERS,
			'stream' : self.STREAM,
			'timeout' : self.TIMEOUT,
			'verify' : self.VERIFY,
		  }
		try:
			if ARGLIST == None:
				webresult = self.SESSION.delete(URL, **OPTS)
			else:
				webresult = self.SESSION.delete(URL, params=ARGLIST, **OPTS)
		except Exception as ex:
			return self.requestExceptionHandler(ex, URL, {'arglist' : ARGLIST})

		if not webresult.status_code in [200]:
			return self.returnError("HTTP response %d - %s" % (webresult.status_code, HTTPStatus(webresult.status_code).phrase),
					{'url' : URL, 'history' : webresult.history})
		RET = {}
		RET['headers'] = webresult.headers
		RET['text'] = webresult.text
		RET['status_code'] = webresult.status_code

		try:
			RESULT = webresult.json()
		except Exception as ex:
			return self.returnError('Error converting response to JSON', { 'url' : URL, 'history' : webresult.history,
									'raw' : webresult.content, 'text' : webresult.text})
		RET['result'] = RESULT
		return self.returnSuccess(RET)

	def executePatch(self, URL, ARGLIST=None):
		'''
		This function executes an HTTP PATCH request.  It can handle a single URL, or the URL can have an argument list passed
		as a python DICT to append the ?key=val&key2=val2.
		'''
		OPTS = {
			'allow_redirects' : self.REDIRECTS,
			'auth' : self.AUTH,
			'cert' : self.CERT,
			'cookies' : self.COOKIEJAR,
			'headers' : self.HEADERS,
			'stream' : self.STREAM,
			'timeout' : self.TIMEOUT,
			'verify' : self.VERIFY,
		  }
		try:
			if ARGLIST == None:
				webresult = self.SESSION.patch(URL, **OPTS)
			else:
				webresult = self.SESSION.patch(URL, param=ARGLIST, **OPTS)
		except Exception as ex:
			return self.requestExceptionHandler(ex, URL, {'arglist' : ARGLIST})

		if not webresult.status_code in [200]:
			return self.returnError("HTTP response %d - %s" % (webresult.status_code, HTTPStatus(webresult.status_code).phrase),
					{'url' : URL, 'history' : webresult.history})
		RET = {}
		RET['headers'] = webresult.headers
		RET['text'] = webresult.text
		RET['status_code'] = webresult.status_code

		if self.RETURN_AS_JSON == True:
			try:
				RESULT = webresult.json()
			except Exception as ex:
				return self.returnError('Error converting response to JSON', { 'url' : URL, 'history' : webresult.history,
									'raw' : webresult.content, 'text' : webresult.text})
		else:
			RESULT = webresult.text
		RET['result'] = RESULT
		return self.returnSuccess(RET)

	def executePut(self, URL, ARGLIST=None):
		'''
		This function executes an HTTP PUT request.  It can handle a single URL, or the URL can have an argument list passed
		as a python DICT to append the ?key=val&key2=val2.
		'''
		OPTS = {
			'allow_redirects' : self.REDIRECTS,
			'auth' : self.AUTH,
			'cert' : self.CERT,
			'cookies' : self.COOKIEJAR,
			'headers' : self.HEADERS,
			'stream' : self.STREAM,
			'timeout' : self.TIMEOUT,
			'verify' : self.VERIFY,
		  }
		try:
			if ARGLIST == None:
				webresult = self.SESSION.put(URL, **OPTS)
			else:
				webresult = self.SESSION.put(URL, param=ARGLIST, **OPTS)

		except Exception as ex:
			return self.requestExceptionHandler(ex, URL, {'arglist' : ARGLIST})

		if not webresult.status_code in [200]:
			return self.returnError("HTTP response %d - %s" % (webresult.status_code, HTTPStatus(webresult.status_code).phrase),
					{'url' : URL, 'history' : webresult.history})

		RET = {}
		RET['headers'] = webresult.headers
		RET['text'] = webresult.text
		RET['status_code'] = webresult.status_code

		if self.RETURN_AS_JSON == True:
			try:
				RESULT = webresult.json()
			except Exception as ex:
				return self.returnError('Error converting response to JSON', { 'url' : URL, 'history' : webresult.history,
									'raw' : webresult.content, 'text' : webresult.text})
		else:
			RESULT = webresult.text
		RET['result'] = RESULT
		return self.returnSuccess(RET)

