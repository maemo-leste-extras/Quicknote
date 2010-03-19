#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
 Copyright (C) 2007 Christoph Würstle and in big parts by Gerold Penz

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
"""

import logging

import pango
import gtk

import hildonize
import gtk_toolbox


try:
	_
except NameError:
	_ = lambda x: x


_moduleLogger = logging.getLogger(__name__)


class SimpleList(object):
	"""
	Stellt eine einfache Liste mit Laufbalken dar. Das wird mit
	den Objekten ScrolledWindow und TreeView erreicht.
	"""

	KEY_IDX = 0
	VALUE_IDX = 1

	def __init__(self):
		"""
		Initialisieren
		"""
		self._selectedItem = None # (<Position>, <Key>, <Value>)

		# Treeview
		self._itemlist = gtk.ListStore(str, str)
		self._itemView = gtk.TreeView(self._itemlist)
		self._itemView.set_headers_visible(False)
		self._itemView.get_selection().set_mode(gtk.SELECTION_SINGLE)
		self._itemView.connect("cursor-changed", self._on_cursor_changed)
		self._itemView.connect("row-activated", self._on_row_activated)
		self._itemView.show()

		# Key-Spalte hinzuf�gen
		self._keyCell = gtk.CellRendererText()
		self._keyColumn = gtk.TreeViewColumn("Key")
		self._keyColumn.pack_start(self._keyCell, True)
		self._keyColumn.add_attribute(self._keyCell, "text", self.KEY_IDX)
		self._keyColumn.set_visible(False)
		self._itemView.append_column(self._keyColumn)

		# Value-Spalte hinzufügen
		self._valueCell = gtk.CellRendererText()
		self._valueCell.set_property("ellipsize", pango.ELLIPSIZE_END)
		self._valueColumn = gtk.TreeViewColumn("Caption")
		self._valueColumn.pack_start(self._valueCell, True)
		self._valueColumn.add_attribute(self._valueCell, "text", self.VALUE_IDX)
		self._itemView.append_column(self._valueColumn)

		# Suchspalte setzen
		# Leider funktioniert die Suche im Moment nicht so 
		# wie ich das möchte. Deshalb habe ich die Suche abgeschaltet.
		self._itemView.set_enable_search(False)

		self._maemo5HackVBox = gtk.VBox()
		self._maemo5HackVBox.pack_start(self._itemView)
		self._maemo5HackViewport = gtk.Viewport()
		self._maemo5HackViewport.add(self._maemo5HackVBox)

		# ScrolledWindow
		self._scrolledWindow = gtk.ScrolledWindow()
		self._scrolledWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		self._scrolledWindow.set_shadow_type(gtk.SHADOW_IN)
		self._scrolledWindow.add(self._maemo5HackViewport)

		self._scrolledWindow = hildonize.hildonize_scrollwindow(self._scrolledWindow)
		self._scrolledWindow.show()

	@property
	def widget(self):
		return self._scrolledWindow

	def append_item(self, value, key = ""):
		"""
		F�gt der Liste Werte und wenn gew�nscht, Schl�ssel hinzu.
		"""

		self._itemlist.append([key, value])

	def select_last_item(self):
		path = str(len(self._itemlist)-1)
		self._itemView.set_cursor(path, self._valueColumn)
		return len(self._itemlist)-1

	def change_item(self, pos, value, key = ""):
		self._itemlist[pos] = [key, value]

	def remove_item(self, pos):
		model = self._itemView.get_model()
		self._itemlist.remove(model.get_iter(str(pos)))

	def get_item(self, pos):
		return self._itemlist[pos]

	def clear_items(self):
		self._itemlist.clear()

	def get_selection_data(self):
		"""
		Gibt die Variable self._selectedItem zur�ck.
		Diese enth�lt ein Tupel. (<Position>, <Key>, <Value>)
		"""

		return self._selectedItem  # (<Position>, <Key>, <Value>)

	def set_eventfunction_cursor_changed(self, function):
		"""
		Verbindet die �bergebene Funktion mit dem 
		Signal "cursor-changed".
		"""

		self._itemView.connect("cursor-changed", function)
		self._itemView.connect("row-activated", function)

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_row_activated(self, treeview, path, view_column, data = None):
		"""
		Sets the value of self._selectedItems. This value can
		be retrieved using the method "get_selection_data.
		"""

		iter = self._itemlist.get_iter(path)
		if not iter:
			return

		self._selectedItem = (
			path[0], # Position
			self._itemlist.get_value(iter, self.KEY_IDX), # Key
			self._itemlist.get_value(iter, self.VALUE_IDX) # Value
		)

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_cursor_changed(self, widget, data1 = None, data2 = None):
		"""
		Sets the value of self._selectedItems. This value can
		be retrieved using the method "get_selection_data.
		"""

		selection = widget.get_selection()
		(model, iter) = selection.get_selected()
		if not iter:
			return

		self._selectedItem = (
			int(selection.get_selected_rows()[1][0][0]), # Position
			str(model.get_value(iter, self.KEY_IDX)), # Key
			str(model.get_value(iter, self.VALUE_IDX)) # Value
		)
