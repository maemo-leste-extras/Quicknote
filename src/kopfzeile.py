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
		self._db = db
		self._lastCategory = 1

		_moduleLogger.info("libkopfzeile, init")
		gtk.HBox.__init__(self, homogeneous = False, spacing = 3)

		categoryHBox = gtk.HBox()
		self.pack_start(categoryHBox, expand = False, fill = True, padding = 0)

		self._categories = [self.ALL_CATEGORIES, self.UNDEFINED_CATEGORY]
		self._categorySelectorButton = gtk.Button(self.UNDEFINED_CATEGORY)
		self._categorySelectorButton.connect("clicked", self._on_category_selector)
		categoryHBox.pack_start(self._categorySelectorButton)

		self.load_categories()

		searchHBox = gtk.HBox()
		self.pack_start(searchHBox, expand = True, fill = True, padding = 0)

		label = gtk.Label(_("Search:  "))
		searchHBox.pack_start(label, expand = False, fill = True, padding = 0)

		self._searchEntry = gtk.Entry()
		searchHBox.pack_start(self._searchEntry, expand = True, fill = True, padding = 0)
		self._searchEntry.connect("changed", self.search_entry_changed, None)

	def get_category(self):
		category = self._categorySelectorButton.get_label()
		if category == self.ALL_CATEGORIES:
			category = "%"
		if category == "":
			category = self.UNDEFINED_CATEGORY
			self._categorySelectorButton.set_label(category)
		return category

	def _get_category_index(self):
		categoryName = self._categorySelectorButton.get_label()
		try:
			return self._categories.index(categoryName)
		except ValueError:
			return -1

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_category_selector(self, *args):
		window = gtk_toolbox.find_parent_window(self)
		userSelection = hildonize.touch_selector_entry(
			window,
			"Categories",
			self._categories,
			self._categorySelectorButton.get_label(),
		)
		self.set_category(userSelection)

	def set_category(self, categoryName = None):
		if categoryName is not None and categoryName != self._categorySelectorButton.get_label():
			self._categorySelectorButton.set_label(categoryName)
			sql = "UPDATE categories SET liste = ? WHERE id = 1"
			self._db.speichereSQL(sql, (self._get_category_index(), ))
		self.emit("category_changed")

	def search_entry_changed(self, widget = None, data = None):
		_moduleLogger.debug("search_entry_changed")
		self.emit("category_changed")

	def define_this_category(self):
		category = self.get_category()
		catIndex = self._get_category_index()
		cats = self._categories[1:] # Skip ALL_CATEGORIES

		if catIndex == -1 and category != "%":
			self._categories.append(category)
			sql = "INSERT INTO categories  (id, liste) VALUES (0, ?)"
			self._db.speichereSQL(sql, (category, ))
			self._categorySelectorButton.set_label(category)

	def delete_this_category(self):
		category = self.get_category()

		sql = "UPDATE notes SET category = ? WHERE category = ?"
		self._db.speichereSQL(sql, (self.UNDEFINED_CATEGORY, category))
		sql = "DELETE FROM categories WHERE liste = ?"
		self._db.speichereSQL(sql, (category, ))

		pos = self._get_category_index()
		if 1 < pos:
			del self._categories[pos]
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

		del self._categories[2:] # Leave ALL_CATEGORIES and UNDEFINED_CATEGORY in

		if cats is not None:
			for cat in cats:
				self._categories.append(cat)

		sql = "SELECT * FROM categories WHERE id = 1"
		rows = self._db.ladeSQL(sql)
		if rows is not None and 0 < len(rows):
			index = int(rows[0][1])
			self._categorySelectorButton.set_label(self._categories[index])
		else:
			self._categorySelectorButton.set_label(self.UNDEFINED_CATEGORY)

		self._lastCategory = self._get_category_index()
