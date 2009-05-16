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
		self._lastCategory = ""
		self._db = db

		gtk.HBox.__init__(self, homogeneous = False, spacing = 3)
		logging.info("libkopfzeile, init")

		categoryHBox = gtk.HBox()
		self.pack_start(categoryHBox, expand = False, fill = True, padding = 0)

		label = gtk.Label(_("Category:  "))
		categoryHBox.pack_start(label, expand = False, fill = True, padding = 0)

		self.categoryCombo = gtk.combo_box_entry_new_text()
		categoryHBox.pack_start(self.categoryCombo, expand = True, fill = True, padding = 0)
		self.load_categories()
		self.categoryCombo.connect("changed", self.category_combo_changed, None)

		searchHBox = gtk.HBox()
		self.pack_start(searchHBox, expand = True, fill = True, padding = 0)

		label = gtk.Label(_("Search:  "))
		searchHBox.pack_start(label, expand = False, fill = True, padding = 0)

		self._searchEntry = gtk.Entry()
		searchHBox.pack_start(self._searchEntry, expand = True, fill = True, padding = 0)
		self._searchEntry.connect("changed", self.search_entry_changed, None)

	def category_combo_changed(self, widget = None, data = None):
		logging.debug("comboCategoryChanged")
		if self._lastCategory != self.categoryCombo.get_active():
			sql = "UPDATE categories SET liste = ? WHERE id = 1"
			self._db.speichereSQL(sql, (self.categoryCombo.get_active(), ))

		self.emit("reload_notes")

	def search_entry_changed(self, widget = None, data = None):
		logging.debug("search_entry_changed")
		self.emit("reload_notes")

	def get_category(self):
		entry = self.categoryCombo.get_child()
		category = entry.get_text()
		if category == _("all"):
			category = "%"
		if category == "":
			category = "undefined"
			self.categoryCombo.set_active(1)
			self.categoryCombo.show()
		return category

	def define_this_category(self):
		category = self.get_category()

		model = self.categoryCombo.get_model()
		n = len(self.categoryCombo.get_model())
		i = 0
		active = -1
		cats = []
		for i, row in enumerate(model):
			if row[0] == category:
				active = i
			if row[0] != "%":
				cats.append(row[0])

		if active == -1 and category != "%":
			self.categoryCombo.append_text(category)
			sql = "INSERT INTO categories  (id, liste) VALUES (0, ?)"
			self._db.speichereSQL(sql, (category, ))
			self.categoryCombo.set_active(i)

	def get_search_pattern(self):
		return self._searchEntry.get_text()

	def load_categories(self):
		sql = "CREATE TABLE categories (id TEXT , liste TEXT)"
		self._db.speichereSQL(sql)

		sql = "SELECT id, liste FROM categories WHERE id = 0 ORDER BY liste"
		rows = self._db.ladeSQL(sql)
		cats = []
		if rows is not None and 0 < len(rows):
			for row in rows:
				cats.append(row[1])

		sql = "SELECT * FROM categories WHERE id = 1"
		rows = self._db.ladeSQL(sql)
		if rows is None or len(rows) == 0:
			sql = "INSERT INTO categories (id, liste) VALUES (1, 1)"
			self._db.speichereSQL(sql)

		#self.categoryCombo.clear()
		while 0 < len(self.categoryCombo.get_model()):
			self.categoryCombo.remove_text(0)

		self.categoryCombo.append_text(_('all'))
		self.categoryCombo.append_text('undefined')

		if cats is not None and 0 < len(cats):
			for cat in cats:
				self.categoryCombo.append_text(cat)

		sql = "SELECT * FROM categories WHERE id = 1"
		rows = self._db.ladeSQL(sql)
		if rows is not None and 0 < len(rows):
			self.categoryCombo.set_active(int(rows[0][1]))
		else:
			self.categoryCombo.set_active(1)

		self._lastCategory = self.categoryCombo.get_active()
