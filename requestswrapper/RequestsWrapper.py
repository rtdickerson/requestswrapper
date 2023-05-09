import os
import sys
from http import HTTPStatus
import prettyprinter 

import requests 

class RequestWrapper(object):

	def __init__(self, PROXIES=None):
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
		self.HEADERS[KEY] = VAL

	def addCookie(self, cookiename, key, DOMAIN, PATH):
		self.COOKIEJAR.set(cookiename, key, DOMAIN, PATH)

	def returnError(self, ERRMSG, ERRDATA=None):
		return {'success' : False, 'error' : ERRMSG, 'details' : ERRDATA}

	def returnSuccess(self, RETURN):
		return {'success' : True, 'result' : RETURN}

	def executeGet(self, URL, ARGLIST=None):
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
		except requests.ConnectionError:
			return self.returnError("Connection error attempting GET", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.Timeout:
			return self.returnError("Timeout error attempting GET", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.TooManyRedirects:
			return self.returnError("Invalid URL", {'url' : URL, 'history' : webresult.history})
		except requests.ReadTimeout:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history})
		except requests.JSONDecodeError:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history, 'text' : webresult.text})
		except requests.RequestException as ex:
			return self.returnError("Requests Error %s" % ex,  {'url' : URL, 'history' : webresult.history})

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
			RETURN_JSON = False
		else:
			return [False, "Unvalid value %d passed on executePost" % MODE]

		try:
			webresult = self.SESSION.post(URL, OPTS)
		except requests.ConnectionError:
			return self.returnError("Connection error attempting POST", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.Timeout:
			return self.returnError("Timeout error attempting POST", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.TooManyRedirects:
			return self.returnError("Invalid URL", {'url' : URL, 'history' : webresult.history})
		except requests.ReadTimeout:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history})
		except requests.JSONDecodeError:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history, 'text' : webresult.text})
		except requests.RequestException as ex:
			return self.returnError("Requests Error %s" % ex,  {'url' : URL, 'history' : webresult.history})
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
		except requests.ConnectionError:
			return self.returnError("Connection error attempting HEAD", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.Timeout:
			return self.returnError("Timeout error attempting HEAD", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.TooManyRedirects:
			return self.returnError("Invalid URL", {'url' : URL, 'history' : webresult.history})
		except requests.ReadTimeout:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history})
		except requests.JSONDecodeError:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history, 'text' : webresult.text})
		except requests.RequestException as ex:
			return self.returnError("Requests Error %s" % ex,  {'url' : URL, 'history' : webresult.history})
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
		except requests.ConnectionError:
			return self.returnError("Connection error attempting OPTIONS", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.Timeout:
			return self.returnError("Timeout error attempting OPTIONS", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.TooManyRedirects:
			return self.returnError("Invalid URL", {'url' : URL, 'history' : webresult.history})
		except requests.ReadTimeout:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history})
		except requests.JSONDecodeError:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history, 'text' : webresult.text})
		except requests.RequestException as ex:
			return self.returnError("Requests Error %s" % ex,  {'url' : URL, 'history' : webresult.history})
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
		except requests.ConnectionError:
			return self.returnError("Connection error attempting GET", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.Timeout:
			return self.returnError("Timeout error attempting GET", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.TooManyRedirects:
			return self.returnError("Invalid URL", {'url' : URL, 'history' : webresult.history})
		except requests.ReadTimeout:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history})
		except requests.JSONDecodeError:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history, 'text' : webresult.text})
		except requests.RequestException as ex:
			return self.returnError("Requests Error %s" % ex,  {'url' : URL, 'history' : webresult.history})
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
		except requests.ConnectionError:
			return self.returnError("Connection error attempting GET", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.Timeout:
			return self.returnError("Timeout error attempting GET", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.TooManyRedirects:
			return self.returnError("Invalid URL", {'url' : URL, 'history' : webresult.history})
		except requests.ReadTimeout:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history})
		except requests.JSONDecodeError:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history, 'text' : webresult.text})
		except requests.RequestException as ex:
			return self.returnError("Requests Error %s" % ex,  {'url' : URL, 'history' : webresult.history})
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
		except requests.ConnectionError:
			return self.returnError("Connection error attempting GET", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.Timeout:
			return self.returnError("Timeout error attempting GET", {'url' : URL, 'history' : webresult.history})
		except requests.exceptions.TooManyRedirects:
			return self.returnError("Invalid URL", {'url' : URL, 'history' : webresult.history})
		except requests.ReadTimeout:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history})
		except requests.JSONDecodeError:
			return self.returnError("Read Timeout", {'url' : URL, 'history' : webresult.history, 'text' : webresult.text})
		except requests.RequestException as ex:
			return self.returnError("Requests Error %s" % ex,  {'url' : URL, 'history' : webresult.history})
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

