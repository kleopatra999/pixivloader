# -*- encoding: utf-8 -*-

import collections, threading

class ImageQueue(object):

	def __init__(self):
		self.condition = threading.Condition()
		self.imgQueue = collections.deque()
		self.stopWaiting = False

	def dequeueImage(self, waitForImage=True):
		""" Get an image from the queue, optionally waiting until new images become available. """
		self.condition.acquire()
		while waitForImage and not self.stopWaiting and len(self) == 0:
			self.condition.wait()

		if len(self) > 0:
			img = self.imgQueue.popleft()
		else:
			img = None
		self.condition.release()

		return img

	def queueFirst(self, imgList):
		""" Add images to the front of the queue. """
		self.imgQueue.extendleft(reversed(imgList))
		self._notifyWaiters()

	def queue(self, imgList):
		""" Add images to the end of the queue. """
		self.imgQueue.extend(imgList)
		self._notifyWaiters()

	def waitNoLonger(self):
		""" The queue no longer waits for new objects when dequeueing images. """
		self.stopWaiting = True
		self._notifyWaiters()

	def _notifyWaiters(self):
		""" Notifies all clients waiting for new images. """
		self.condition.acquire()
		self.condition.notifyAll()
		self.condition.release()

	def __len__(self):
		return len(self.imgQueue)
