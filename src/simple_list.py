#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
 Copyright (C) 2007 Christoph Würstle and in big parts by Gerold Penz

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
"""


import pygtk
pygtk.require("2.0")
import gtk


try:
	_
except NameError:
	_ = lambda x: x


class SimpleList(gtk.ScrolledWindow):
	"""
	Stellt eine einfache Liste mit Laufbalken dar. Das wird mit
	den Objekten ScrolledWindow und TreeView erreicht.
	"""

	def __init__(self):
		"""
		Initialisieren
		"""

		gtk.ScrolledWindow.__init__(self)
		self.selected_item = None # (<Position>, <Key>, <Value>)

		# Liste
		self.list_store = gtk.ListStore(str, str)

		# ScrolledWindow
		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.set_shadow_type(gtk.SHADOW_IN)

		# Treeview
		self.tree_view = gtk.TreeView(self.list_store)
		self.tree_view.set_headers_visible(False)
		self.tree_view.get_selection().set_mode(gtk.SELECTION_BROWSE)
		self.tree_view.connect("cursor-changed", self._on_cursor_changed)
		self.tree_view.connect("row-activated", self._on_row_activated)
		self.tree_view.show()

		# Key-Spalte hinzuf�gen
		self.key_cell = gtk.CellRendererText()
		self.key_column = gtk.TreeViewColumn("Key")
		self.key_column.pack_start(self.key_cell, True)
		self.key_column.add_attribute(self.key_cell, "text", 0)
		self.key_column.set_visible(False)
		self.tree_view.append_column(self.key_column)

		# Value-Spalte hinzufügen
		self.value_cell = gtk.CellRendererText()
		self.value_column = gtk.TreeViewColumn("Caption")
		self.value_column.pack_start(self.value_cell, True)
		self.value_column.add_attribute(self.value_cell, "text", 1)
		self.tree_view.append_column(self.value_column)

		# Suchspalte setzen
		# Leider funktioniert die Suche im Moment nicht so 
		# wie ich das möchte. Deshalb habe ich die Suche abgeschaltet.
		self.tree_view.set_enable_search(False)

		# Anzeigen
		self.add(self.tree_view)
		self.show()

	def append_item(self, value, key = ""):
		"""
		F�gt der Liste Werte und wenn gew�nscht, Schl�ssel hinzu.
		"""

		self.list_store.append([key, value])

	def select_last_item(self):
		path = str(len(self.list_store)-1)
		self.tree_view.set_cursor(path, self.value_column)
		return len(self.list_store)-1

	def change_item(self, pos, value, key = ""):
		self.list_store[pos] = [key, value]

	def remove_item(self, pos):
		model = self.tree_view.get_model()
		self.list_store.remove(model.get_iter(str(pos)))

	def get_item(self, pos):
		return self.list_store[pos]

	def clear_items(self):
		self.list_store.clear()

	def _on_row_activated(self, treeview, path, view_column, data = None):
		"""
		Setzt den Wert von self.selected_items. Dieser Wert kann
		mit der Methode "get_selection_data" abgerufen werden.
		"""

		iter = self.list_store.get_iter(path)

		if iter:
			self.selected_item = (
				path[0], # Position
				self.list_store.get_value(iter, 0), # Key
				self.list_store.get_value(iter, 1) # Value
			)

	def _on_cursor_changed(self, widget, data1 = None, data2 = None):
		"""
		Setzt den Wert von self.selected_items. Dieser Wert kann
		mit der Methode "get_selection_data" abgerufen werden.
		"""

		selection = widget.get_selection()
		(model, iter) = selection.get_selected()

		if iter:
			self.selected_item = (
				int(selection.get_selected_rows()[1][0][0]), # Position
				str(model.get_value(iter, 0)), # Key
				str(model.get_value(iter, 1)) # Value
			)

	def get_selection_data(self):
		"""
		Gibt die Variable self.selected_item zur�ck.
		Diese enth�lt ein Tupel. (<Position>, <Key>, <Value>)
		"""

		return self.selected_item  # (<Position>, <Key>, <Value>)

	def set_eventfunction__cursor_changed(self, function):
		"""
		Verbindet die �bergebene Funktion mit dem 
		Signal "cursor-changed".
		"""

		self.tree_view.connect("cursor-changed", function)
