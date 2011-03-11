# -*- encoding: utf-8 -*-

import threading
import os.path, shutil
import mechanize

import imageproviders
import browser
import configuration

class ImageDownloader(threading.Thread):
	""" A thread that downloads images from a central image queue. """

	_downloaded = 0
	lock = threading.Lock()

	def __init__(self, imgQueue, imgNaming):
		threading.Thread.__init__(self)
		self.imgQueue = imgQueue
		self.imgNaming = imgNaming

		self.downloadManga = True

	def run(self):
		""" Starts downloading images from the queue. """

		while not self._shouldStop():
			img = self.imgQueue.dequeueImage()
			if img:
				self._saveFile(img)
			else:
				return

	def _saveFile(self, img):
		""" Download selected image. """
		try:
			filename, directory = self.imgNaming.filename(img), self._createDirectory(img)
			fullpath = os.path.join(directory, filename)

			if not os.path.exists(fullpath):
				with ImageDownloader.lock:
					print img.imageUrl
				temppath, headers = browser.retrieve(img.imageUrl, img.referringUrl)
				shutil.move(temppath, fullpath)

				with ImageDownloader.lock:
					self._downloaded += 1
		except mechanize.HTTPError as error:
			if error.getcode() == 404 and self.downloadManga:
				self._loadImagesFromMangaPage(img.imageId)


	def _loadImagesFromMangaPage(self, imageId):
		""" Try to get images from a manga page """

		mangaProvider = imageproviders.MangaPageProvider(imageId)
		mangaProvider.nextPage()
		self.imgQueue.queueFirst(mangaProvider.listImages())

	def _createDirectory(self, img):
		""" Creates the directory the image should be saved to, if necessary """
		directory = self.imgNaming.directory(img).decode('utf-8')

		with ImageDownloader.lock:
			if not os.path.exists(directory):
				os.makedirs(directory)

		return directory

	def _shouldStop(self):
		""" Checks various stop conditions for this thread. """

		if configuration.Imagelimit > 0 and \
			self._downloaded >= configuration.Imagelimit: return True

		return False
