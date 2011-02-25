# -*- encoding: utf-8 -*-

import os.path, sys
import getpass

# Login information
Username = ''
Password = ''

# Download directory
Basedir = "."

# User agent used by the browser
Useragent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'

# Limits for downloading and crawling (0 to disable limits)
Imagelimit = 0
Pagelimit = 0
Threads = 4

def _configDir():
	baseConfigDir = "%APPDATA%\\PixivLoader" if sys.platform == "win32" else "$HOME/.config/pixivloader"
	return os.path.normpath(os.path.expandvars(baseConfigDir))

def _initConfiguration():
	directory, filename = _configDir(), "pixivloader.conf"
	
	global Username, Password
	if not Username or not Password:
		print "Please enter your login details."
		Username = raw_input("Username: ")
		Password = getpass.getpass("Password: ")
