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

				# Count manga as only one image
				with ImageDownloader.lock:
					if not ("_p" in filename and "_p0." not in filename):
						ImageDownloader._downloaded += 1
		except mechanize.HTTPError as error:
			if error.getcode() == 404 and self.downloadManga:
				self._loadImagesFromMangaPage(img.imageId, img.favoriteCount)


	def _loadImagesFromMangaPage(self, imageId, favoriteCount):
		""" Try to get images from a manga page """

		mangaProvider = imageproviders.MangaPageProvider(imageId)
		mangaProvider.nextPage()
		images = mangaProvider.listImages()
		for img in images:
			img.favoriteCount = favoriteCount

		self.imgQueue.queueFirst(images)

	def _createDirectory(self, img):
		""" Creates the directory the image should be saved to, if necessary """
		directory = self.imgNaming.directory(img).decode('utf-8')
		directory = directory.replace('?', '')

		with ImageDownloader.lock:
			if not os.path.exists(directory):
				os.makedirs(directory)

		return directory

	def _shouldStop(self):
		""" Checks various stop conditions for this thread. """
		with ImageDownloader.lock:
			if configuration.Imagelimit > 0 and \
				ImageDownloader._downloaded >= configuration.Imagelimit:
				return True

		return False
