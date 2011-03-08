# -*- encoding: utf-8 -*-

import re
import mechanize
import urlparse

class Image(object):

	def __init__(self, tag):
		""" Creates an Image instance from a HTML LI element as
		    commonly encountered on Pixiv. """

		self.imageId = self._getId(tag)
		self.imageUrl = self._getUrl(tag)
		self.favoriteCount = self._getFavoriteCount(tag)
		self.referringUrl = self._getPageLink(tag)

	def artistId(self):
		""" Gets the Pixiv id of the image's artist. """

		return self.imageUrl.split("/")[-2]

	def filename(self):
		""" Gets the image's base file name. """

		return self.imageUrl.split("/")[-1]

	def _getId(self, liTag):
		""" Extracts the ID from the image tag. """

		filename = self._getUrl(liTag).split("/")[-1]
		return filename.split(".")[0]

	def _getPageLink(self, liTag):
		""" Extracts the page linked to by the image. """

		return urlparse.urljoin("http://www.pixiv.net",
			liTag[0].get("href"))

	def _getUrl(self, liTag):
		""" Extracts the URL from the image tag. """

		thumbnail = self._cleanUrl(liTag[0][0].get("src"))
		return thumbnail.replace("_s.", ".")

	def _getFavoriteCount(self, liTag):
		""" Extracts the number of times an image has been favorited. """

		if len(liTag) > 2:
			spanFavorites = liTag[2][0]
			return int(re.search(r"\d+",
				spanFavorites.text).group(0))
		else:
			return 0

	def _cleanUrl(self, url):
		""" Removes query strings from an URL """
		_, host, path, _, _ = urlparse.urlsplit(url)
		return urlparse.urljoin("http://" + host, path)

	def __repr__(self):
		return "<Image {0} by {1}>".format(self.imageId, self.artistId())

class MangaImage(Image):

	def __init__(self, imgSrc, referringUrl):
		""" Construct an image from a manga page. """

		super(MangaImage, self).__init__(imgSrc)
		self.referringUrl = referringUrl

	def _getFavoriteCount(self, imgTag):
		return 0

	def _getUrl(self, imgSrc):
		return self._cleanUrl(imgSrc)

	def _getPageLink(self, imgTag):
		return ""

