# -*- coding: utf-8 -*-

import urlparse

class Image(object):

	def __init__(self, image_id, image_url, favorite_count=0, referring_url=""):
		self.imageId = image_id
		self.imageUrl = image_url
		self.favoriteCount = favorite_count
		self.referringUrl = referring_url

	def artistId(self):
		""" Gets the Pixiv id of the image's artist. """

		return self.imageUrl.split("/")[-2]

	def filename(self):
		""" Gets the image's base file name. """

		return self.imageUrl.split("/")[-1]

	def __repr__(self):
		return "<Image {0} by {1}>".format(self.imageId, self.artistId())


def image_from_search(tag):
	""" Creates an Image object from a <li> tag as encountered on a search
	result page. """

	# Get the actual image URL from the thumbnail URL
	url = tag[0][0][0].get("src")
	thumbnail = __clean_url(url)
	image_url = thumbnail.replace("_s.", ".")

	# Get the image ID
	filename = image_url.split("/")[-1]
	image_id = filename.split(".")[0]

	# Get the favorite count
	bookmarkcount = int(tag[2][0][0].text) if len(tag) > 2 else 0

	# Get the link to the medium-size page from the image link
	referring_url = urlparse.urljoin("http://www.pixiv.net",
		tag[0].get("href"))

	return Image(image_id, image_url, bookmarkcount, referring_url)

def image_from_membergallery(tag):
	""" Creates an Image object from a <li> tag as encountered on a member
	gallery. """

	# Get the actual image URL from the thumbnail URL
	url = tag[0][0].get("src")
	thumbnail = __clean_url(url)
	image_url = thumbnail.replace("_s.", ".")

	# Get the image ID
	filename = image_url.split("/")[-1]
	image_id = filename.split(".")[0]

	# Get the link to the medium-size page from the image link
	referring_url = urlparse.urljoin("http://www.pixiv.net",
		tag[0].get("href"))

	return Image(image_id, image_url, 0, referring_url)

def image_from_mangapage(url, referring_url):
	""" Creates an Image object from a source URL and a referrer URL. """

	image_url = __clean_url(url)

	filename = image_url.split("/")[-1]
	image_id = filename.split(".")[0]

	return Image(image_id, image_url, 0, referring_url)

def __clean_url(url):
	""" Strips query string from an URL. """
	_, host, path, _, _ = urlparse.urlsplit(url)
	return urlparse.urljoin("http://" + host, path)
