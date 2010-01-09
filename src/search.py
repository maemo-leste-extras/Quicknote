#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-


import logging

import gobject
import gtk

import gtk_toolbox
import hildonize

try:
	_
except NameError:
	_ = lambda x: x


_moduleLogger = logging.getLogger("search")


class Search(gtk.HBox):

	__gsignals__ = {
		'search_changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
	}

	def __init__(self):
		_moduleLogger.info("search, init")
		gtk.HBox.__init__(self, homogeneous = False, spacing = 3)

		label = gtk.Label(_("Search:  "))

		self._searchEntry = gtk.Entry()
		self._searchEntry.connect("changed", self._on_search_entry_changed, None)

		searchHBox = gtk.HBox()
		searchHBox.pack_start(label, expand = False, fill = False)
		searchHBox.pack_start(self._searchEntry, expand = True, fill = True)
		self.pack_start(searchHBox, expand = True, fill = True)

	def get_search_pattern(self):
		return self._searchEntry.get_text()

	def _on_search_entry_changed(self, widget = None, data = None):
		self.emit("search_changed")
