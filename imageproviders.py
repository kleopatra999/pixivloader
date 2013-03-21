# -*- encoding: utf-8 -*-

import lxml.html
import urllib
import re
import operator

import images
import browser

class ImageProvider(object):

	def nextPage(self):
		""" Switches to the next page. Returns True if the page exists. """
		raise NotImplementedError

	def listImages(self):
		""" Gets all images on the current page. Returns a list of images.Image objects. """
		raise NotImplementedError

class PagedProvider(ImageProvider):
	""" Base class for all image providers that deal with images
	    in a paged format. """

	def __init__(self):
		self.currentPage = 0
		self.pageHtml = None

	def nextPage(self):
		self.currentPage += 1

		url = self.searchUrl().format(self.currentPage)
		response = browser.open(url)

		self.pageHtml = lxml.html.fromstring(response)

		return self._isValidPage()

	def listImages(self):
		""" Returns a list of Image objects for the current page. """

		liTags = self.pageHtml.cssselect(self.cssForImages())
		allImages = [images.image_from_search(liTag) for liTag in liTags]
		return self._filterImages(allImages)

	def _isValidPage(self):
		""" If the pager doesn't contain the current page,
			it is considered an invalid page. """

		return bool(self.pageHtml.cssselect("nav.column-order-menu ul.page-list > li.current"))

	def _filterImages(self, images):
		""" Determines if an image is included in listImages. """

		return images

	def searchUrl(self):
		""" Returns the search URL, expecting a format entry
		    {0} where page number is to be inserted. """

		raise NotImplementedError

	def cssForImages(self):
		""" Returns the CSS selector for <li> tags which
		    contain all necessary image information. """

		raise NotImplementedError

class MemberGalleryProvider(PagedProvider):
	""" Gets images from an artist's page. """

	def __init__(self, artistId):
		super(MemberGalleryProvider, self).__init__()
		self.artistId = artistId

	def listImages(self):
		""" Returns a list of Image objects for the current page. """

		liTags = self.pageHtml.cssselect(self.cssForImages())
		return [images.image_from_membergallery(liTag) for liTag in liTags]

	def cssForImages(self):
		return "div.display_works li"

	def searchUrl(self):
		return "http://www.pixiv.net/member_illust.php" + \
			"?id={0}&p={1}".format(self.artistId, "{0}")

	def _isValidPage(self):
		""" If the pager doesn't contain the current page,
			it is considered an invalid page. """

		return bool(self.pageHtml.cssselect("div.pages > ol > li.pages-current"))

class SearchProvider(PagedProvider):
	""" Gets images from a search. """

	def __init__(self, searchString, minFavorites=0):
		super(SearchProvider, self).__init__()
		self.searchString = searchString
		self.minFavorites = minFavorites
		self._filterImages = self._filterImagesMean

	def cssForImages(self):
		return "section.column-search-result li.image-item"

	def _filterImagesPercent(self, images):
		""" Gets the top <minFavorites> percent on any page. """
		images.sort(key=operator.attrgetter('favoriteCount'), reverse=True)
		keepPercent = self.minFavorites / 100.0
		keepCount = int(len(images) * keepPercent)
		keepCount = min(keepCount, len(images))
		return images[:keepCount]

	def _filterImagesAbsolute(self, images):
		""" Gets all images with user favorites > <minFavorites>. """
		return filter(lambda i: i.favoriteCount >= self.minFavorites, images)

	def _filterImagesMean(self, images):
		""" Filters all images with more user favorites than the page's average. """

		# Cut 10% of all favorite counts from both sides of the list to smooth
		# the average.
		favorites = sorted([img.favoriteCount for img in images])
		cutoff = int(len(favorites) * 0.1)
		cut_favorites = favorites[cutoff:-cutoff]
		if not cut_favorites:
			cut_favorites = favorites
		mean = sum(favorites) / float(len(favorites))
		cut_mean = sum(cut_favorites) / float(len(cut_favorites))

		before_cut = filter(lambda i: i.favoriteCount >= mean + self.minFavorites, images)
		after_cut = filter(lambda i: i.favoriteCount >= cut_mean + self.minFavorites, images)
		print ("Average favorites on page: {0}. After cut: {1}. "
				"Selected before cut: {2}. Afterwards: {3}").format(mean, cut_mean,
				len(before_cut), len(after_cut))

		return after_cut

	def searchUrl(self):
		return "http://www.pixiv.net/search.php" + \
			"?word={0}&s_mode=s_tag&p={1}".format(urllib.quote(self.searchString), "{0}")

class TagProvider(SearchProvider):
	""" Gets images by tags. """

	def searchUrl(self):
		return "http://www.pixiv.net/search.php" + \
			"?word={0}&s_mode=s_tag_full&p={1}".format(urllib.quote(self.searchString), "{0}")

class TagR18Provider(SearchProvider):
	""" Gets images by tags. (only R-18) """

	def searchUrl(self):
		return "http://www.pixiv.net/search.php" + \
			"?word={0}&r18=1&s_mode=s_tag_full&p={1}".format(urllib.quote(self.searchString), "{0}")

class MangaPageProvider(ImageProvider):
	""" Get all pages on manga listing pages. """

	def __init__(self, imageId):
		self.imageId = imageId
		self.onFirstPage = True
		self.pageHtml = None

	def nextPage(self):
		if self.onFirstPage:
			url = self._buildMangaUrl()
			response = browser.open(url)
			self.pageHtml = lxml.html.fromstring(response)
			self.onFirstPage = False
			return True
		else:
			return False

	def listImages(self):
		""" Requires some more work, as images are loaded dynamically using JavaScript. """
		imageScripts = self.pageHtml.cssselect("section#image div.image-container > script")
		imgUrls = [ re.search(r"unshift\('([^']+)'\)", script.text).group(1)
			for script in imageScripts ]
		return [images.image_from_mangapage(imgUrl, self._buildMangaUrl()) for imgUrl in imgUrls]

	def _buildMangaUrl(self):
		return "http://www.pixiv.net/member_illust.php" +\
			"?mode=manga&illust_id={0}".format(self.imageId)
