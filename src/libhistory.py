#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
 Copyright (C) 2007 Christoph Würstle

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
"""


import gtk


try:
	_
except NameError:
	_ = lambda x: x


class Dialog(gtk.Dialog):

	def __init__(self, daten = None):
		gtk.Dialog.__init__(self, _("History:"), None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		self.set_position(gtk.WIN_POS_CENTER)

		self.liststore = gtk.ListStore(int, str, str, str, str)
		#pcdatum, datum, sql, param # param schön

		# create the TreeView using liststore
		self.treeview = gtk.TreeView(self.liststore)
		# create a CellRenderers to render the data
		self.cell1 = gtk.CellRendererText()
		self.cell2 = gtk.CellRendererText()

		# create the TreeViewColumns to display the data
		self.tvcolumn1 = gtk.TreeViewColumn(_('Timestamp'))
		self.tvcolumn2 = gtk.TreeViewColumn(_('Note'))
		# add columns to treeview
		self.treeview.append_column(self.tvcolumn1)
		self.treeview.append_column(self.tvcolumn2)

		# add the cells to the columns - 2 in the first
		self.tvcolumn1.pack_start(self.cell1, True)
		self.tvcolumn2.pack_start(self.cell2, True)
		self.tvcolumn1.set_attributes(self.cell1, text = 1) #Spalten setzten hier!!!!
		self.tvcolumn2.set_attributes(self.cell2, text = 4)

		self.treeview.set_reorderable(False)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolled_window.add(self.treeview)
		self.vbox.pack_start(scrolled_window, expand = True, fill = True, padding = 0)

		self.liststore.clear()

		if daten is not None:
			for data in daten:
				self.liststore.append(data)

	def get_selected_row(self):
		path = self.treeview.get_cursor()[0]
		if path is None or path == "":
			return None

		iter1 = self.treeview.get_model().get_iter(path)
		return self.treeview.get_model().get(iter1, 0, 1, 2, 3, 4)
