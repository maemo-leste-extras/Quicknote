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
	Category box
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

		self._categories = [self.ALL_CATEGORIES, self.UNDEFINED_CATEGORY]
		self._categorySelectorButton = gtk.Button(self.UNDEFINED_CATEGORY)
		self._categorySelectorButton.connect("clicked", self._on_category_selector)
		self.pack_start(self._categorySelectorButton, expand = True, fill = True)

		self.load_categories()

	def get_category_name(self):
		category = self._categorySelectorButton.get_label()
		assert category != ""
		return category

	def get_queryable_category(self):
		category = self.get_category_name()
		if category == self.ALL_CATEGORIES:
			category = "%"
		assert category != ""
		return category

	def get_categories(self):
		return iter(self._categories)

	def _get_this_category_index(self):
		categoryName = self.get_category_name()
		try:
			return self._categories.index(categoryName)
		except ValueError:
			return -1

	def _get_category_index(self, categoryName):
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
			self.get_category_name(),
		)
		self.set_category(userSelection)

	def set_category(self, categoryName = None):
		if categoryName is not None:
			if not categoryName:
				categoryName = self.UNDEFINED_CATEGORY
			if categoryName != self.get_category_name():
				self.add_category(categoryName)
				self._categorySelectorButton.set_label(categoryName)
				sql = "UPDATE categories SET liste = ? WHERE id = 1"
				self._db.speichereSQL(sql, (self._get_this_category_index(), ))
		self.emit("category_changed")

	def add_category(self, categoryName):
		if categoryName in self._categories:
			return
		assert "%" not in categoryName, "Not sure, but maybe %s can't be in names"
		self._categories.append(categoryName)
		sql = "INSERT INTO categories  (id, liste) VALUES (0, ?)"
		self._db.speichereSQL(sql, (categoryName, ))

	def delete_this_category(self):
		category = self.get_category_name()
		assert category not in (self.ALL_CATEGORIES, self.UNDEFINED_CATEGORY)

		sql = "UPDATE notes SET category = ? WHERE category = ?"
		self._db.speichereSQL(sql, (self.UNDEFINED_CATEGORY, category))
		sql = "DELETE FROM categories WHERE liste = ?"
		self._db.speichereSQL(sql, (category, ))

		self._categories.remove(category)
		self.set_category(self.ALL_CATEGORIES)

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

		self._lastCategory = self._get_this_category_index()
