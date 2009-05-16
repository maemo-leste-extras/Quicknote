#/usr/bin/env python2.5
# -*- coding: utf-8 -*-

import gtk


class FileChooserDialog(gtk.FileChooserDialog):
	"""
	@bug The buttons currently don't do anything
	"""

	def __init__(self, *args, **kwds):
		super(FileChooserDialog, self).__init__(*args, **kwds)
		self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
		self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)


class Window(gtk.Window):

	def __init__(self):
		super(Window, self).__init__(gtk.WINDOW_TOPLEVEL)
		self.set_default_size(700, 500)


class Program(object):

	def __init__(self):
		pass

	def add_window(self, window):
		pass
