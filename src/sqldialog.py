#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Copyright (C) 2007 Christoph Würstle

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
"""


import time
import logging

import gtk


try:
	_
except NameError:
	_ = lambda x: x


_moduleLogger = logging.getLogger(__name__)


class SqlDialog(gtk.Dialog):

	EXPORT_RESPONSE = 444

	def __init__(self, db):
		self.db = db

		_moduleLogger.info("sqldialog, init")

		gtk.Dialog.__init__(self, _("SQL History (the past two days):"), None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)

		self.add_button(_("Export"), self.EXPORT_RESPONSE)
		self.add_button(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
		self.set_position(gtk.WIN_POS_CENTER)

		self.liststore = gtk.ListStore(str, str, str)

		# create the TreeView using liststore
		self.treeview = gtk.TreeView(self.liststore)
		self.treeview.set_rules_hint(True)

		# create a CellRenderers to render the data
		self.cell1 = gtk.CellRendererText()
		self.cell2 = gtk.CellRendererText()
		self.cell3 = gtk.CellRendererText()

		# create the TreeViewColumns to display the data
		self.tvcolumn1 = gtk.TreeViewColumn(_('Timestamp'))
		self.tvcolumn2 = gtk.TreeViewColumn('SQL')
		self.tvcolumn3 = gtk.TreeViewColumn(_('Parameter'))

		# add columns to treeview
		self.treeview.append_column(self.tvcolumn1)
		self.treeview.append_column(self.tvcolumn2)
		self.treeview.append_column(self.tvcolumn3)


		self.tvcolumn1.pack_start(self.cell1, True)
		self.tvcolumn2.pack_start(self.cell2, True)
		self.tvcolumn3.pack_start(self.cell3, True)

		self.tvcolumn1.set_attributes(self.cell1, text = 0) #Spalten setzten hier!!!!
		self.tvcolumn2.set_attributes(self.cell2, text = 1)
		self.tvcolumn3.set_attributes(self.cell3, text = 2)

		# Allow NOT drag and drop reordering of rows
		self.treeview.set_reorderable(False)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolled_window.add(self.treeview)

		self.vbox.pack_start(scrolled_window, True, True, 0)

		self.vbox.show_all()

		msgstring = ""
		sql = "SELECT pcdatum, sql, param FROM logtable WHERE pcdatum>? ORDER BY pcdatum DESC"
		rows = db.ladeSQL(sql, (time.time()-3*24*3600, ))
		for row in rows:
			pcdatum, sql, param = row
			datum = str(time.strftime(_("%d.%m.%y %H:%M:%S "), (time.localtime(pcdatum))))
			self.liststore.append([datum, sql, param])

		self.set_size_request(500, 400)

	def exportSQL(self, filename):
		f = open(filename, 'w')
		try:
			msgstring = ""
			sql = "SELECT pcdatum, sql, param FROM logtable WHERE pcdatum>? ORDER BY pcdatum DESC"
			rows = self.db.ladeSQL(sql, (time.time()-2*24*3600, ))
			for row in rows:
				pcdatum, sql, param = row
				datum = str(time.strftime("%d.%m.%y %H:%M:%S ", (time.localtime(pcdatum))))
				f.write( datum +"\t" + sql + "\t\t" + param+ "\n")
		finally:
			f.close()
