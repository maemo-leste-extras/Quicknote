#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
 Copyright (C) 2007 Christoph Würstle

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
"""


import logging

import gobject
import gtk


try:
	_
except NameError:
	_ = lambda x: x


class Kopfzeile(gtk.HBox):

	__gsignals__ = {
		'reload_notes' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
	}

	def __init__(self, db):
		self.lastCategory = ""
		self.db = db

		gtk.HBox.__init__(self, homogeneous = False, spacing = 3)
		logging.info("libkopfzeile, init")

		categoryHBox = gtk.HBox()
		self.pack_start(categoryHBox, expand = False, fill = True, padding = 0)

		label = gtk.Label(_("Category:  "))
		categoryHBox.pack_start(label, expand = False, fill = True, padding = 0)

		self.comboCategory = gtk.combo_box_entry_new_text()
		categoryHBox.pack_start(self.comboCategory, expand = True, fill = True, padding = 0)
		self.loadCategories()
		self.comboCategory.connect("changed", self.comboCategoryChanged, None)

		searchHBox = gtk.HBox()
		self.pack_start(searchHBox, expand = True, fill = True, padding = 0)

		label = gtk.Label(_("Search:  "))
		searchHBox.pack_start(label, expand = False, fill = True, padding = 0)

		self.searchEntry = gtk.Entry()
		searchHBox.pack_start(self.searchEntry, expand = True, fill = True, padding = 0)
		self.searchEntry.connect("changed", self.searchEntryChanged, None)

	def comboCategoryChanged(self, widget = None, data = None):
		logging.debug("comboCategoryChanged")
		if self.lastCategory != self.comboCategory.get_active():
			sql = "UPDATE categories SET liste = ? WHERE id = 1"
			self.db.speichereSQL(sql, (self.comboCategory.get_active(), ))

		self.emit("reload_notes")

	def searchEntryChanged(self, widget = None, data = None):
		logging.debug("searchEntryChanged")
		self.emit("reload_notes")

	def getCategory(self):
		entry = self.comboCategory.get_child()
		category = entry.get_text()
		if category == _("all"):
			category = "%"
		if category == "":
			category = "undefined"
			self.comboCategory.set_active(1)
			self.comboCategory.show()
		return category

	def defineThisCategory(self):
		category = self.getCategory()

		model = self.comboCategory.get_model()
		n = len(self.comboCategory.get_model())
		i = 0
		active = -1
		cats = []
		while i < n:
			if (model[i][0] == category):
				#self.comboCategory.set_active(i)
				active = i
			if (model[i][0]!= "%"):
				cats.append(model[i][0])
			i += 1

		if (active == -1) and (category!= "%"):
			self.comboCategory.append_text(category)
			sql = "INSERT INTO categories  (id, liste) VALUES (0, ?)"
			self.db.speichereSQL(sql, (category, ))
			self.comboCategory.set_active(i)

	def getSearchPattern(self):
		return self.searchEntry.get_text()

	def loadCategories(self):
		sql = "CREATE TABLE categories (id TEXT , liste TEXT)"
		self.db.speichereSQL(sql)

		sql = "SELECT id, liste FROM categories WHERE id = 0 ORDER BY liste"
		rows = self.db.ladeSQL(sql)
		cats = []
		if rows is not None and 0 < len(rows):
			for row in rows:
				cats.append(row[1])

		sql = "SELECT * FROM categories WHERE id = 1"
		rows = self.db.ladeSQL(sql)
		if rows is None or len(rows) == 0:
			sql = "INSERT INTO categories (id, liste) VALUES (1, 1)"
			self.db.speichereSQL(sql)

		#self.comboCategory.clear()
		while 0 < len(self.comboCategory.get_model()):
			self.comboCategory.remove_text(0)

		self.comboCategory.append_text(_('all'))
		self.comboCategory.append_text('undefined')

		if cats is not None and 0 < len(cats):
			for cat in cats:
				self.comboCategory.append_text(cat)

		sql = "SELECT * FROM categories WHERE id = 1"
		rows = self.db.ladeSQL(sql)
		if rows is not None and 0 < len(rows):
			self.comboCategory.set_active(int(rows[0][1]))
		else:
			self.comboCategory.set_active(1)

		self.lastCategory = self.comboCategory.get_active()
