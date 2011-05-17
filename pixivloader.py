#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys, os.path, shutil, optparse
import threading, collections, mechanize

import browser
import imageproviders
import downloader
import naming
import configuration
import imagequeue

def collectImages(provider, imgQueue):
	""" Collects all images from a specified provider and adds them to the image queue. """

	while provider.nextPage():
		imgs = provider.listImages()

		if len(imgs) > 0:
			imgQueue.queue(imgs)

			with downloader.ImageDownloader.lock:
				print "Added {0} new images from page {1}".format(len(imgs), provider.currentPage)
		else:
			with downloader.ImageDownloader.lock:
				print "No images on page {0}".format(provider.currentPage)

		if configuration.Pagelimit > 0 and \
			provider.currentPage >= configuration.Pagelimit:
			break

def win32_unicode_argv():
    """Uses shell32.GetCommandLineArgvW to get sys.argv as a list of Unicode
    strings.

    Versions 2.x of Python don't support Unicode in sys.argv on
    Windows, with the underlying Windows API instead replacing multi-byte
    characters with '?'.
    """

    from ctypes import POINTER, byref, cdll, c_int, windll
    from ctypes.wintypes import LPCWSTR, LPWSTR

    GetCommandLineW = cdll.kernel32.GetCommandLineW
    GetCommandLineW.argtypes = []
    GetCommandLineW.restype = LPCWSTR

    CommandLineToArgvW = windll.shell32.CommandLineToArgvW
    CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
    CommandLineToArgvW.restype = POINTER(LPWSTR)

    cmd = GetCommandLineW()
    argc = c_int(0)
    argv = CommandLineToArgvW(cmd, byref(argc))
    if argc.value > 0:
        # Remove Python executable and commands if present
        start = argc.value - len(sys.argv)
        return [argv[i].encode("utf-8") for i in
                xrange(start, argc.value)]

def parseArguments():
	""" Returns a tupe of (options, arguments, parser) from the command line. """
	argv = win32_unicode_argv() if sys.platform == 'win32' else sys.argv

	parser = optparse.OptionParser(usage="%prog -s <tags> | -g <memberid>")
	parser.add_option("-f", "--minfavs", dest="minfavs", default=0,
		type="int", help="Minimum amount of favorites for an image. Default is 0.")
	parser.add_option("-s", "--search", dest="search",
		help="Search by any string.")
	parser.add_option("-g", "--gallery", dest="gallery", type="int",
		help="Search member gallery.")
	parser.add_option("-t", "--tag", dest="tag",
		help="Search by specific tag.")
	parser.add_option("--imglimit", dest="imglimit", type="int", default=0,
		help="Stop after number of downloaded images has been reached. Default is 0.")
	parser.add_option("--pagelimit", dest="pagelimit", type="int", default=25,
		help="Maximum number of searched pages. Default is 25.")
	parser.add_option("--threads", dest="threads", type="int", default=4,
		help="Maximum number of download threads. Default is 4.")

	options, args = parser.parse_args(argv[1:])

	if not options.search and not options.gallery and not options.tag:
		parser.error("One of --search, --gallery or --tag must be used.")

	if options.threads <= 0:
		parser.error("Number of --threads must be at least 1.")

	return options, args

def setupConfiguration(options):
	""" Change configuration based on command line arguments. """
	configuration.initConfiguration()
	configuration.Imagelimit = options.imglimit
	configuration.Pagelimit = options.pagelimit
	configuration.Threads = options.threads


def getProvider(options):
	"""Construct the provider from command line arguments. """

	if options.gallery:
		return imageproviders.MemberGalleryProvider(options.gallery)
	elif options.tag:
		return imageproviders.TagProvider(options.tag, options.minfavs)
	elif options.search:
		return imageproviders.SearchProvider(options.search, options.minfavs)

def getNaming(options):
	""" Get naming scheme from command line arguments """
	if options.search or options.tag:
		searchValue = options.search if options.search else options.tag
		return naming.SearchTagNaming(searchValue)
	elif options.gallery:
		return naming.MemberNaming(options.gallery)

def main():
	options, args = parseArguments()
	setupConfiguration(options)

	provider, naming = getProvider(options), getNaming(options)
	condition = threading.Condition()
	imgQueue = imagequeue.ImageQueue()

	threads = [ downloader.ImageDownloader(imgQueue, naming)
			for _ in range(configuration.Threads) ]

	# Start all threads
	for thread in threads:
		thread.daemon = True
		thread.start()

	# Start collecting images
	try:
		collectImages(provider, imgQueue)
	except KeyboardInterrupt:
		pass

	# Notify all threads that collection has finished
	imgQueue.waitNoLonger()

	# Wait for download threads to shut down
	for thread in threads:
		thread.join()

if __name__ == '__main__':
	main()
