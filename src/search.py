#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-


import logging

import gobject
import gtk

try:
	_
except NameError:
	_ = lambda x: x


_moduleLogger = logging.getLogger(__name__)


class Search(gtk.HBox):

	__gsignals__ = {
		'search_changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
	}

	def __init__(self):
		_moduleLogger.info("search, init")
		gtk.HBox.__init__(self, homogeneous = False, spacing = 3)
		self.connect("hide", self._on_hide)
		self.connect("show", self._on_show)

		label = gtk.Label(_("Search:  "))

		self._searchEntry = gtk.Entry()
		self._searchEntry.connect("changed", self._on_search_entry_changed, None)

		closeImage = gtk.Image()
		closeImage.set_from_stock("gtk-close", gtk.ICON_SIZE_MENU)
		closeSearch = gtk.Button()
		closeSearch.set_image(closeImage)
		closeSearch.connect("clicked", self._on_close)

		searchHBox = gtk.HBox()
		searchHBox.pack_start(label, expand = False, fill = False)
		searchHBox.pack_start(self._searchEntry, expand = True, fill = True)
		searchHBox.pack_start(closeSearch, expand = False, fill = False)
		self.pack_start(searchHBox, expand = True, fill = True)

	def get_search_pattern(self):
		return self._searchEntry.get_text()

	def _on_search_entry_changed(self, widget = None, data = None):
		self.emit("search_changed")

	def _on_close(self, *args):
		self.hide()

	def _on_show(self, *args):
		self._searchEntry.grab_focus()

	def _on_hide(self, *args):
		# HACK Disabled for now.  Clearing this resets the note list which
		# causes the current note to lose focus.
		# self._searchEntry.set_text("")
		pass
