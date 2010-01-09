#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Copyright (C) 2007 Christoph Würstle

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.

@todo Add Note Export (txt File) and Export All (json dump?)
@todo Remove confirmation on deleting empty notes
@todo Try to switch to more passive notifications (rather than message boxes)
"""

from __future__ import with_statement

import os
import gc
import logging
import warnings
import ConfigParser

import gtk

try:
	import hildon
except ImportError:
	import fakehildon as hildon

try:
	import osso
except ImportError:
	osso = None

import constants
import hildonize
import gtk_toolbox

import speichern
import kopfzeile
import notizen
import search
import sync


try:
	_
except NameError:
	_ = lambda x: x


_moduleLogger = logging.getLogger("quicknote_gtk")


class QuicknoteProgram(hildonize.get_app_class()):

	_user_data = os.path.join(os.path.expanduser("~"), ".%s" % constants.__app_name__)
	_user_settings = "%s/settings.ini" % _user_data

	def __init__(self):
		super(QuicknoteProgram, self).__init__()
		self._clipboard = gtk.clipboard_get()

		dblog = os.path.join(self._user_data, "quicknote.log")

		_moduleLogger.info('Starting quicknote')
		self._wordWrapEnabled = False

		self._window_in_fullscreen = False #The window isn't in full screen mode initially.

		self._db = speichern.Speichern()
		self._syncDialog = None

		#Create GUI main vbox
		vbox = gtk.VBox(homogeneous = False, spacing = 0)

		if hildonize.GTK_MENU_USED:
			#Create Menu and apply it for hildon
			filemenu = gtk.Menu()

			menu_items = gtk.MenuItem(_("Set DB file"))
			filemenu.append(menu_items)
			menu_items.connect("activate", self.set_db_file, None)

			menu_items = gtk.MenuItem(_("SQL History"))
			filemenu.append(menu_items)
			menu_items.connect("activate", self._on_view_sql_history, None)

			menu_items = gtk.MenuItem(_("Sync notes"))
			filemenu.append(menu_items)
			menu_items.connect("activate", self._on_sync_notes, None)

			menu_items = gtk.MenuItem(_("Quit"))
			filemenu.append(menu_items)
			menu_items.connect("activate", self._on_destroy, None)

			file_menu = gtk.MenuItem(_("File"))
			file_menu.show()
			file_menu.set_submenu(filemenu)

			categorymenu = gtk.Menu()

			menu_items = gtk.MenuItem(_("Search"))
			categorymenu.append(menu_items)
			menu_items.connect("activate", self._on_toggle_search)

			menu_items = gtk.MenuItem(_("Move To Category"))
			categorymenu.append(menu_items)
			menu_items.connect("activate", self._on_move_category)

			menu_items = gtk.MenuItem(_("Delete"))
			categorymenu.append(menu_items)
			menu_items.connect("activate", self._on_delete_category)

			category_menu = gtk.MenuItem(_("Category"))
			category_menu.show()
			category_menu.set_submenu(categorymenu)

			viewmenu = gtk.Menu()

			menu_items = gtk.MenuItem(_("Word Wrap"))
			viewmenu.append(menu_items)
			menu_items.connect("activate", self._on_toggle_word_wrap)

			menu_items = gtk.MenuItem(_("History"))
			viewmenu.append(menu_items)
			menu_items.connect("activate", self._on_show_history)

			view_menu = gtk.MenuItem(_("Note"))
			view_menu.show()
			view_menu.set_submenu(viewmenu)

			helpmenu = gtk.Menu()

			menu_items = gtk.MenuItem(_("About"))
			helpmenu.append(menu_items)
			menu_items.connect("activate", self._on_show_about, None)

			help_menu = gtk.MenuItem(_("Help"))
			help_menu.show()
			help_menu.set_submenu(helpmenu)

			menuBar = gtk.MenuBar()
			menuBar.show()
			menuBar.append (file_menu)
			menuBar.append (category_menu)
			menuBar.append (view_menu)
			menuBar.append (help_menu)

			vbox.pack_start(menuBar, False, False, 0)
		else:
			menuBar = gtk.MenuBar()
			menuBar.show()
			vbox.pack_start(menuBar, False, False, 0)

		#Create GUI elements
		self._category = kopfzeile.Kopfzeile(self._db)
		self._search = search.Search()
		self._notizen = notizen.Notizen(self._db, self._category, self._search)

		# notizen packs in the category
		vbox.pack_start(self._notizen, expand = True, fill = True)
		vbox.pack_start(self._search, expand = False, fill = True)

		#Get the Main Window, and connect the "destroy" event
		self._window = gtk.Window()
		self._window.add(vbox)

		self._on_toggle_word_wrap()

		try:
			os.makedirs(self._user_data)
		except OSError, e:
			if e.errno != 17:
				raise

		self._window = hildonize.hildonize_window(self, self._window)
		hildonize.set_application_title(self._window, "%s" % constants.__pretty_app_name__)
		menuBar = hildonize.hildonize_menu(
			self._window,
			menuBar,
		)
		if hildonize.IS_FREMANTLE_SUPPORTED:
			moveToCategoryButton = gtk.Button(_("Move Note"))
			moveToCategoryButton.connect("clicked", self._on_move_category)
			menuBar.append(moveToCategoryButton)

			historyButton= gtk.Button(_("Note History"))
			historyButton.connect("clicked", self._on_show_history)
			menuBar.append(historyButton)

			searchButton= gtk.Button(_("Search Category"))
			searchButton.connect("clicked", self._on_toggle_search)
			menuBar.append(searchButton)

			deleteCategoryButton = gtk.Button(_("Delete Category"))
			deleteCategoryButton.connect("clicked", self._on_delete_category)
			menuBar.append(deleteCategoryButton)

			menuBar.show_all()

		if not hildonize.IS_HILDON_SUPPORTED:
			_moduleLogger.info("No hildonization support")

		if osso is not None:
			self._osso_c = osso.Context(constants.__app_name__, constants.__version__, False)
			self._deviceState = osso.DeviceState(self._osso_c)
			self._deviceState.set_device_state_callback(self._on_device_state_change, 0)
		else:
			_moduleLogger.info("No osso support")
			self._osso_c = None
			self._deviceState = None

		self._prepare_sync_dialog()

		self._window.connect("delete-event", self._on_delete_event)
		self._window.connect("destroy", self._on_destroy)
		self._window.connect("key-press-event", self._on_key_press)
		self._window.connect("window-state-event", self._on_window_state_change)

		self._window.show_all()
		self._search.hide()
		self._load_settings()

	def _save_settings(self):
		config = ConfigParser.SafeConfigParser()
		self.save_settings(config)
		with open(self._user_settings, "wb") as configFile:
			config.write(configFile)

	def save_settings(self, config):
		config.add_section(constants.__pretty_app_name__)
		config.set(constants.__pretty_app_name__, "wordwrap", str(self._wordWrapEnabled))
		config.set(constants.__pretty_app_name__, "fullscreen", str(self._window_in_fullscreen))

	def _load_settings(self):
		config = ConfigParser.SafeConfigParser()
		config.read(self._user_settings)
		self.load_settings(config)

	def load_settings(self, config):
		try:
			self._wordWrapEnabled = config.getboolean(constants.__pretty_app_name__, "wordwrap")
			self._window_in_fullscreen = config.getboolean(constants.__pretty_app_name__, "fullscreen")
		except ConfigParser.NoSectionError, e:
			warnings.warn(
				"Settings file %s is missing section %s" % (
					self._user_settings,
					e.section,
				),
				stacklevel=2
			)

		self._notizen.set_wordwrap(self._wordWrapEnabled)

		if self._window_in_fullscreen:
			self._window.fullscreen()
		else:
			self._window.unfullscreen()

	def set_db_file(self, widget = None, data = None):
		dlg = hildon.FileChooserDialog(parent=self._window, action=gtk.FILE_CHOOSER_ACTION_SAVE)

		if self._db.ladeDirekt('datenbank'):
			dlg.set_filename(self._db.ladeDirekt('datenbank'))

		dlg.set_title(_("Choose database file"))
		if dlg.run() == gtk.RESPONSE_OK:
			fileName = dlg.get_filename()
			self._db.speichereDirekt('datenbank', fileName)

			self._db.openDB()
			self._category.load_categories()
			self._notizen.load_notes()
		dlg.destroy()

	def _prepare_sync_dialog(self):
		self._syncDialog = gtk.Dialog(_("Sync"), None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

		self._syncDialog.set_position(gtk.WIN_POS_CENTER)
		syncer = sync.Sync(self._db, self._window, 50504)
		self._syncDialog.vbox.pack_start(syncer, True, True, 0)
		self._syncDialog.set_size_request(500, 350)
		self._syncDialog.vbox.show_all()
		syncer.connect("syncFinished", self._on_sync_finished)

	def _toggle_search(self):
		if self._search.get_property("visible"):
			self._search.hide()
		else:
			self._search.show()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_device_state_change(self, shutdown, save_unsaved_data, memory_low, system_inactivity, message, userData):
		"""
		For system_inactivity, we have no background tasks to pause

		@note Hildon specific
		"""
		if memory_low:
			gc.collect()

		if save_unsaved_data or shutdown:
			self._save_settings()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_window_state_change(self, widget, event, *args):
		if event.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN:
			self._window_in_fullscreen = True
		else:
			self._window_in_fullscreen = False

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_key_press(self, widget, event, *args):
		RETURN_TYPES = (gtk.keysyms.Return, gtk.keysyms.ISO_Enter, gtk.keysyms.KP_Enter)
		isCtrl = bool(event.get_state() & gtk.gdk.CONTROL_MASK)
		if (
			event.keyval == gtk.keysyms.F6 or
			event.keyval in RETURN_TYPES and isCtrl
		):
			# The "Full screen" hardware key has been pressed 
			if self._window_in_fullscreen:
				self._window.unfullscreen ()
			else:
				self._window.fullscreen ()
			return True
		elif event.keyval == gtk.keysyms.f and isCtrl:
			self._toggle_search()
			return True
		elif (
			event.keyval in (gtk.keysyms.w, gtk.keysyms.q) and
			event.get_state() & gtk.gdk.CONTROL_MASK
		):
			self._window.destroy()
		elif event.keyval == gtk.keysyms.l and event.get_state() & gtk.gdk.CONTROL_MASK:
			with open(constants._user_logpath_, "r") as f:
				logLines = f.xreadlines()
				log = "".join(logLines)
				self._clipboard.set_text(str(log))
			return True

	def _on_toggle_search(self, *args):
		self._toggle_search()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_show_history(self, *args):
		self._notizen.show_history()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_view_sql_history(self, widget = None, data = None, data2 = None):
		import sqldialog
		sqldiag = sqldialog.SqlDialog(self._db)
		res = sqldiag.run()
		sqldiag.hide()
		if res == sqldiag.EXPORT_RESPONSE:
			_moduleLogger.info("exporting sql")

			dlg = hildon.FileChooserDialog(parent=self._window, action=gtk.FILE_CHOOSER_ACTION_SAVE)

			dlg.set_title(_("Select SQL export file"))
			if dlg.run() == gtk.RESPONSE_OK:
				fileName = dlg.get_filename()
				sqldiag.exportSQL(fileName)
			dlg.destroy()

		sqldiag.destroy()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_move_category(self, *args):
		comboCategory = gtk.combo_box_new_text()
		comboCategory.append_text('undefined')
		sql = "SELECT id, liste FROM categories WHERE id = 0 ORDER BY liste"
		rows = self._db.ladeSQL(sql)
		for row in rows:
			comboCategory.append_text(row[1])

		dialog = gtk.Dialog(_("Choose category"), self._window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		try:
			dialog.set_position(gtk.WIN_POS_CENTER)

			dialog.vbox.pack_start(comboCategory, True, True, 0)
			dialog.vbox.show_all()

			userResponse = dialog.run()
		finally:
			dialog.destroy()

		if userResponse != gtk.RESPONSE_ACCEPT:
			return

		n = comboCategory.get_active()
		if -1 < n and self._notizen.noteId != -1:
			model = comboCategory.get_model()
			active = comboCategory.get_active()
			if active < 0:
				return None
			cat_id = model[active][0]

			noteid, pcdatum, category, note = self._db.loadNote(self._notizen.noteId)
			self._db.saveNote(noteid, note, cat_id, pcdatum = None)
			self._category.set_category() # force it to update
		else:
			mbox = gtk.MessageDialog(self._window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("No note selected."))
			response = mbox.run()
			mbox.hide()
			mbox.destroy()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_delete_category(self, *args):
		if self._category.get_category() == "%" or self._category.get_category() == "undefined":
			mbox = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("This category can not be deleted"))
			try:
				response = mbox.run()
			finally:
				mbox.hide()
				mbox.destroy()
			return

		mbox = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO, _("Are you sure to delete the current category?"))
		try:
			response = mbox.run()
		finally:
			mbox.hide()
			mbox.destroy()
		if response == gtk.RESPONSE_YES:
			self._category.delete_this_category()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_sync_finished(self, data = None, data2 = None):
		self._category.load_categories()
		self._notizen.load_notes()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_sync_notes(self, widget = None, data = None):
		self._syncDialog.run()
		self._syncDialog.hide()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_toggle_word_wrap(self, *args):
		self._wordWrapEnabled = not self._wordWrapEnabled
		self._notizen.set_wordwrap(self._wordWrapEnabled)

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_delete_event(self, widget, event, data = None):
		return False

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_destroy(self, widget = None, data = None):
		try:
			self._db.close()
			self._save_settings()

			try:
				self._deviceState.close()
			except AttributeError:
				pass # Either None or close was removed (in Fremantle)
			try:
				self._osso_c.close()
			except AttributeError:
				pass # Either None or close was removed (in Fremantle)
		finally:
			gtk.main_quit()

	@gtk_toolbox.log_exception(_moduleLogger)
	def _on_show_about(self, widget = None, data = None):
		dialog = gtk.AboutDialog()
		dialog.set_position(gtk.WIN_POS_CENTER)
		dialog.set_name(constants.__pretty_app_name__)
		dialog.set_version(constants.__version__)
		dialog.set_copyright("")
		dialog.set_website("http://axique.de/index.php?f=Quicknote")
		comments = _("%s is a note taking program; it is optimised for quick save and search of notes") % constants.__pretty_app_name__
		dialog.set_comments(comments)
		dialog.set_authors(["Christoph Wurstle <n800@axique.net>", "Ed Page <eopage@byu.net> (Blame him for the most recent bugs)"])
		dialog.run()
		dialog.destroy()


def run_quicknote():
	if hildonize.IS_HILDON_SUPPORTED:
		gtk.set_application_name(constants.__pretty_app_name__)
	app = QuicknoteProgram()
	gtk.main()


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	run_quicknote()
