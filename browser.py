# -*- encoding: utf-8 -*-

import mechanize
import threading

import configuration

# Store list of browser objects for each thread.
_browsers = dict()
_lock = threading.Lock()

def _initialize(browser):
	""" Log in into Pixiv. """
	browser.addheaders = [('User-Agent', configuration.Useragent)]
	browser.open("http://www.pixiv.net/login.php")
	browser.select_form(name="loginForm")
	browser["pixiv_id"] = configuration.Username
	browser["pass"] = configuration.Password
	browser.submit()

def _browser():
	""" Returns a thread-bound Browser object. The browser is initialized when created. """
	threadid = threading.current_thread().ident

	global _browsers
	if threadid in _browsers:
		return _browsers[threadid]
	else:
		browser = mechanize.Browser()
		_initialize(browser)
		with _lock:
			_browsers[threadid] = browser

		return browser

def open(url):
	response = _browser().open(url)
	return response.get_data()

def retrieve(url, referer=None):
	browser = _browser()

	if referer:
		browser.addheaders = [('User-Agent', configuration.Useragent), ('Referer', referer)]
	return browser.retrieve(url)
