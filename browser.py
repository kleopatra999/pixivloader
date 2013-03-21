# -*- encoding: utf-8 -*-

import mechanize
import threading

import configuration

# Shared cookie jar
_cookies = mechanize.CookieJar()

def _initialize(browser):
	""" Log in into Pixiv. """
	browser.set_cookiejar(_cookies)
	browser.addheaders = [('User-Agent', configuration.Useragent)]

	if not len(_cookies):
		print 'Using login name: {0}'.format(configuration.Username)
		browser.open("https://ssl.pixiv.net/login.php")
		browser.select_form(nr=1)
		browser["pixiv_id"] = configuration.Username
		browser["pass"] = configuration.Password
		browser.submit()

def _browser():
	""" Returns a thread-bound Browser object. The browser is initialized when created. """

	if hasattr(threading.local(), "browser"):
		return threading.local().browser
	else:
		browser = mechanize.Browser()
		_initialize(browser)
		threading.local().browser = browser

		return browser

def open(url, referer=None):
	browser = _browser()
	if referer:
		browser.addheaders = [('User-Agent', configuration.Useragent),
			('Referer', referer)]

	response = browser.open(url)
	return response.get_data()

def retrieve(url, referer=None):
	browser = _browser()

	if referer:
		browser.addheaders = [('User-Agent', configuration.Useragent),
			('Referer', referer)]
	return browser.retrieve(url)
