# -*- encoding: utf-8 -*-

import os.path, sys
import getpass
import ConfigParser

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
Threads = 8

def _configDir():
	""" Returns a suitable directory for storing the configuration
	file in. """
	baseConfigDir = "%APPDATA%\\PixivLoader" if sys.platform == "win32" else "$HOME/.config/pixivloader"
	return os.path.normpath(os.path.expandvars(baseConfigDir))

def _configName():
	""" Name of the configuration file. """
	return "pixivloader.conf"

def _get(config, option, default=None):
	""" Returns the config option <option> from the default section.
	If the option does not exist, returns <default>. """
	if config.has_option("DEFAULT", option):
		return config.get("DEFAULT", option)
	else:
		return default

def _set(config, option, value):
	""" Convenience method for setting values in the default section. """
	config.set("DEFAULT", option, value)

def _loadConfigFile():
	""" Populates the configration options from the config file. """
	cfg = ConfigParser.SafeConfigParser()
	cfg.read(os.path.join(_configDir(), _configName()))

	global Username, Password, Basedir
	Username = _get(cfg, "Username", "")
	Password = _get(cfg, "Password", "")
	Basedir = _get(cfg, "Basedir", ".")

def _saveConfigFile():
	""" Stores the current configuration in the config file. """
	cfg = ConfigParser.SafeConfigParser()
	_set(cfg, "Username", Username)
	_set(cfg, "Password", Password)
	_set(cfg, "Basedir", Basedir)

	directory, filename = _configDir(), _configName()
	if not os.path.exists(directory):
		os.makedirs(directory, 0700)
	fp = open(os.path.join(directory, filename), "w")
	cfg.write(fp)
	fp.close()
	os.chmod(os.path.join(directory, filename), 0600)

def initConfiguration():
	""" Initializes the module. """
	_loadConfigFile()
	global Username, Password
	if not Username or not Password:
		print "Please enter your login details."
		Username = raw_input("Username: ")
		Password = getpass.getpass("Password: ")

		save = raw_input("Do you want to save these login details? [Y/n]: ")
		if not save or save.lower() == "y":
			_saveConfigFile()
