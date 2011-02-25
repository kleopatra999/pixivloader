# -*- encoding: utf-8 -*-

import os.path

import configuration

class ImageNaming(object):
	""" Determines an image's directory and filename """

	def __init__(self, baseNaming=None):
		self.baseNaming = baseNaming

	def directory(self, img):
		if self.baseNaming:
			return self.baseNaming.directory(img)
		else:
			return os.path.normpath(os.path.abspath(configuration.Basedir))

	def filename(self, img):
		return img.filename()

class SearchTagNaming(ImageNaming):
	""" Search term determines the image's directory """

	def __init__(self, searchTerm, baseNaming=None):
		super(SearchTagNaming, self).__init__(baseNaming)
		self.searchTerm = searchTerm

	def directory(self, img):
		return os.path.join(
			super(SearchTagNaming, self).directory(img),
			self.searchTerm)

class MemberNaming(ImageNaming):
	""" Directory is based on Pixiv ID """
	def __init__(self, memberId, baseNaming=None):
		super(MemberNaming, self).__init__(baseNaming)
		self.memberId = memberId

	def directory(self, img):
		pixivId = img.imageUrl.split("/")[-2]
		return os.path.join(
			super(MemberNaming, self).directory(img),
			"{0}-{1}".format(self.memberId, pixivId))
