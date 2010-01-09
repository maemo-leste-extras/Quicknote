#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
 Copyright (C) 2007 Christoph Würstle

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
"""


import logging

import gtk


try:
	_
except NameError:
	_ = lambda x: x


_moduleLogger = logging.getLogger("history")


class HistorySelectionDialog(gtk.Dialog):

	def __init__(self, daten = None):
		super(HistorySelectionDialog, self).__init__(
			_("History:"),
			None,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT),
		)
		self.set_position(gtk.WIN_POS_CENTER)

		self.noteHistory = gtk.ListStore(
			int, #pcdatum
			str, #datum
			str, #sql
			str, #param
			str #param schön
		)

		self._historyView = gtk.TreeView(self.noteHistory)
		self._historyView.set_rules_hint(True)

		self._timestampCell = gtk.CellRendererText()
		self._timestampColumn = gtk.TreeViewColumn(_('Timestamp'))
		self._timestampColumn.pack_start(self._timestampCell, True)
		self._timestampColumn.set_attributes(self._timestampCell, text = 1) #Spalten setzten hier!!!!

		self._noteCell = gtk.CellRendererText()
		self._noteColumn = gtk.TreeViewColumn(_('Note'))
		self._noteColumn.pack_start(self._noteCell, True)
		self._noteColumn.set_attributes(self._noteCell, text = 4)

		# add columns to treeview
		self._historyView.append_column(self._timestampColumn)
		self._historyView.append_column(self._noteColumn)
		self._historyView.set_reorderable(False)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolled_window.add(self._historyView)
		self.vbox.pack_start(scrolled_window, expand = True, fill = True, padding = 0)

		self.noteHistory.clear()

		if daten is not None:
			for data in daten:
				self.noteHistory.append(data)

	def get_selected_row(self):
		path = self._historyView.get_cursor()[0]
		if path is None or path == "":
			return None

		iter1 = self._historyView.get_model().get_iter(path)
		return self._historyView.get_model().get(iter1, 0, 1, 2, 3, 4)
