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

import gtk_toolbox
import hildonize

try:
	_
except NameError:
	_ = lambda x: x


_moduleLogger = logging.getLogger("kopfzeile")


class Kopfzeile(gtk.HBox):
	"""
	Category/Search box
	"""

	__gsignals__ = {
		'category_changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
	}

	ALL_CATEGORIES = _("all")
	UNDEFINED_CATEGORY = "undefined"

	def __init__(self, db):
		self._lastCategory = ""
		self._db = db

		_moduleLogger.info("libkopfzeile, init")
		gtk.HBox.__init__(self, homogeneous = False, spacing = 3)

		categoryHBox = gtk.HBox()
		self.pack_start(categoryHBox, expand = False, fill = True, padding = 0)

		label = gtk.Label(_("Category:  "))
		categoryHBox.pack_start(label, expand = False, fill = True, padding = 0)

		self._categories = [self.ALL_CATEGORIES, self.UNDEFINED_CATEGORY]
		self._categorySelectorButton = gtk.Button(self.UNDEFINED_CATEGORY)
		self._categorySelectorButton.connect("clicked", self._on_category_selector)
		#categoryHBox.pack_start(self._categorySelectorButton)

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

	def get_category(self):
		entry = self.categoryCombo.get_child()
		category = entry.get_text()
		if category == self.ALL_CATEGORIES:
			category = "%"
		if category == "":
			category = self.UNDEFINED_CATEGORY
			self._categorySelectorButton.set_label(category)
			self.categoryCombo.set_active(1)
			self.categoryCombo.show()
		return category

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_category_selector(self, *args):
		window = gtk_toolbox.find_parent_window(self)
		userSelection = hildonize.touch_selector_entry(
			window,
			"Categories",
			self._categories,
			self._categorySelectorButton.get_label(),
		)
		if userSelection == self._categorySelectorButton.get_label():
			return

		sql = "UPDATE categories SET liste = ? WHERE id = 1"
		self._db.speichereSQL(sql, (self.categoryCombo.get_active(), ))

		self.emit("category_changed")

	def category_combo_changed(self, widget = None, data = None):
		_moduleLogger.debug("comboCategoryChanged")
		if self._lastCategory != self.categoryCombo.get_active():
			sql = "UPDATE categories SET liste = ? WHERE id = 1"
			self._db.speichereSQL(sql, (self.categoryCombo.get_active(), ))

		self.emit("category_changed")

	def search_entry_changed(self, widget = None, data = None):
		_moduleLogger.debug("search_entry_changed")
		self.emit("category_changed")

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
			self._categories.append(category)
			sql = "INSERT INTO categories  (id, liste) VALUES (0, ?)"
			self._db.speichereSQL(sql, (category, ))
			self.categoryCombo.set_active(i)
			self._categorySelectorButton.set_label(category)

	def delete_this_category(self):
		category = self.get_category()

		sql = "UPDATE notes SET category = ? WHERE category = ?"
		self._db.speichereSQL(sql, (self.UNDEFINED_CATEGORY, category))
		sql = "DELETE FROM categories WHERE liste = ?"
		self._db.speichereSQL(sql, (category, ))
		model = self.categoryCombo.get_model()
		pos = self.categoryCombo.get_active()
		if 1 < pos:
			self.categoryCombo.remove_text(pos)
			self.categoryCombo.set_active(0)
			self._categorySelectorButton.set_label(self.ALL_CATEGORIES)

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
		del self._categories[2:]

		self.categoryCombo.append_text(self.ALL_CATEGORIES)
		self.categoryCombo.append_text(self.UNDEFINED_CATEGORY)

		if cats is not None:
			for cat in cats:
				self.categoryCombo.append_text(cat)
				self._categories.append(cat)

		sql = "SELECT * FROM categories WHERE id = 1"
		rows = self._db.ladeSQL(sql)
		if rows is not None and 0 < len(rows):
			index = int(rows[0][1])
			self.categoryCombo.set_active(index)
			self._categorySelectorButton.set_label(self._categories[index])
		else:
			self.categoryCombo.set_active(1)
			self._categorySelectorButton.set_label(self.UNDEFINED_CATEGORY)

		self._lastCategory = self.categoryCombo.get_active()
