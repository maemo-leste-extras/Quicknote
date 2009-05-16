#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
 Copyright (C) 2007 Christoph Würstle

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.

@todo Add hiding of the history button on zoom
"""

import time
import logging
import uuid

import gobject
import gtk

import simple_list


try:
	_
except NameError:
	_ = lambda x: x


class Notizen(gtk.HBox):

	def __init__(self, db, topBox):
		self.db = db
		self.topBox = topBox
		self.noteid = -1
		self.pos = -1
		self.note = None #Last notetext
		self.category = ""

		gtk.HBox.__init__(self, homogeneous = False, spacing = 0)
		logging.info("libnotizen, init")

		self.noteslist = simple_list.SimpleList()
		self.noteslist.set_eventfunction__cursor_changed(self.noteslist_changed)

		self.noteslist.set_size_request(250, -1)

		vbox = gtk.VBox(homogeneous = False, spacing = 0)

		frame = gtk.Frame(_("Titles"))
		frame.add(self.noteslist)
		vbox.pack_start(frame, expand = True, fill = True, padding = 3)

		buttonHBox = gtk.HBox()
		vbox.pack_start(buttonHBox, expand = False, fill = True, padding = 3)

		button = gtk.Button(stock = gtk.STOCK_ADD)
		button.connect("clicked", self.add_note, None)
		buttonHBox.pack_start(button, expand = True, fill = True, padding = 3)

		button = gtk.Button(stock = gtk.STOCK_DELETE)
		button.connect("clicked", self.del_note, None)
		buttonHBox.pack_start(button, expand = True, fill = True, padding = 3)

		self.pack_start(vbox, expand = False, fill = True, padding = 3)

		self.textviewNote = gtk.TextView()
		self.textviewNote.connect("focus-out-event", self.saveNote, "focus-out-event")
		buf = self.textviewNote.get_buffer()
		buf.set_text("")
		buf.connect("changed", self.noteChanged, None)

		#self.textviewNotiz.set_size_request(-1, 50)
		self.scrolled_window = gtk.ScrolledWindow()
		self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrolled_window.add(self.textviewNote)

		frame = gtk.Frame(_("Note"))
		frame.add(self.scrolled_window)

		vbox = gtk.VBox(homogeneous = False, spacing = 0)
		vbox.pack_start(frame, expand = True, fill = True, padding = 3)

		hbox = gtk.HBox(homogeneous = False, spacing = 0)

		self.statuslabel = gtk.Label("Test")
		self.statuslabel.set_alignment(0.0, 0.5)
		hbox.pack_start(self.statuslabel, expand = True, fill = True, padding = 3)

		button = gtk.Button(_("History"))
		button.connect("clicked", self.show_history, None)
		hbox.pack_start(button, expand = True, fill = True, padding = 3)

		vbox.pack_start(hbox, expand = False, fill = True, padding = 3)

		self.pack_start(vbox, expand = True, fill = True, padding = 3)

		self.loadNotes()
		self.topBox.connect("reload_notes", self.loadNotes)

	def set_wordwrap(self, enableWordWrap):
		if enableWordWrap:
			self.scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
			self.textviewNote.set_wrap_mode(gtk.WRAP_WORD)
		else:
			self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			self.textviewNote.set_wrap_mode(gtk.WRAP_NONE)

	def getTitle(self, buf):
		eol = buf.find("\n")
		if -1 == eol:
			eol = len(buf)
		title = buf[:eol]
		return title

	def noteChanged(self, widget = None, data = None):
		if self.pos == -1 or self.noteid == -1:
			return

		buf = self.textviewNote.get_buffer().get_text(self.textviewNote.get_buffer().get_start_iter(), self.textviewNote.get_buffer().get_end_iter())

		title = self.getTitle(buf)
		value, key = self.noteslist.get_item(self.pos)

		if value != title:
			self.noteslist.change_item(self.pos, title, self.noteid)

	def saveNote(self, widget = None, data = None, data2 = None):
		logging.info("saveNote params: pos:"+str(self.pos)+" noteid:"+str(self.noteid))
		#print "params:", data, data2
		buf = self.textviewNote.get_buffer().get_text(self.textviewNote.get_buffer().get_start_iter(), self.textviewNote.get_buffer().get_end_iter())
		if buf is None or len(buf) == 0:
			return

		if buf == self.note:
			return

		logging.info("Saving note: "+buf)
		if self.pos == -1 or self.noteid == -1:
			self.pos = -1
			self.noteid = str(uuid.uuid4())
			self.db.saveNote(self.noteid, buf, self.category)
			self.noteslist.append_item(self.getTitle(buf), self.noteid)
			self.pos = self.noteslist.select_last_item()
		else:
			self.db.saveNote(self.noteid, buf, self.category)

		self.topBox.defineThisCategory()

	def setFocus(self):
		self.textviewNote.grab_focus()
		return False

	def noteslist_changed(self, data = None, data2 = None):
		if self.pos != -1:
			self.saveNote()

		try:
			(pos, key, value) = self.noteslist.get_selection_data()
			if (pos == -1):
				return
		except StandardError:
			if data != "new":
				return
			key = None

		if key == "new" or data == "new":
			#both methods supported click add note or new note (first one disabled)
			self.noteid = str(uuid.uuid4())
			self.db.saveNote(self.noteid, "", self.category)
			self.pos = -1
			self.noteslist.append_item("", self.noteid)
			self.textviewNote.get_buffer().set_text("")
			self.pos = self.noteslist.select_last_item()
		else:
			self.pos = pos
			self.noteid, pcdatum, self.category, self.note = self.db.loadNote(key)
			self.statuslabel.set_text(time.strftime(_("Last change: %d.%m.%y %H:%M"), time.localtime(pcdatum)))
			buf = self.textviewNote.get_buffer()
			buf.set_text(self.note)

		gobject.timeout_add(200, self.setFocus)

	def add_note(self, widget = None, data = None):
		self.noteslist_changed("new")

	def del_note(self, widget = None, data = None):
		if (self.noteid == -1):
			return
		mbox = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO, _("Really delete?"))
		response = mbox.run()
		mbox.hide()
		mbox.destroy()
		if response == gtk.RESPONSE_YES:
			self.db.delNote(self.noteid)
			self.noteid = -1
			self.noteslist.remove_item(self.pos)
			self.pos = -1
			self.textviewNote.get_buffer().set_text("")

	def loadNotes(self, data = None):
		logging.info("loadNotes params: pos:"+str(self.pos)+" noteid:"+str(self.noteid))
		self.noteslist.clear_items()
		self.noteslist.append_item(_("new Note"), "new")

		self.category = self.topBox.getCategory()
		search = self.topBox.getSearchPattern()
		notes = self.db.searchNotes(search, self.category)

		if notes is not None:
			for note in notes:
				noteid, category, noteText = note
				title = self.getTitle(noteText)
				self.noteslist.append_item(title, noteid)

		self.noteid = -1
		self.pos = -1
		self.textviewNote.get_buffer().set_text("")

	def show_history(self, widget = None, data = None, label = None):
		if self.noteid == -1:
			mbox =  gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, _("No note selected."))
			response = mbox.run()
			mbox.hide()
			mbox.destroy()
			return

		rows = self.db.getNoteHistory(self.noteid)

		import libhistory
		dialog = libhistory.Dialog()

		lastNoteStr = ""
		for row in rows:
			#for x in row:
			#	print x
			daten = row[4][1]
			if (daten != "")and(lastNoteStr != daten):
				lastNoteStr = daten
				dialog.liststore.append([row[0], row[1], row[2], row[3], daten+"\n"])

		dialog.vbox.show_all()
		dialog.set_size_request(600, 380)

		if dialog.run() == gtk.RESPONSE_ACCEPT:
			print "saving"
			self.saveNote()
			data = dialog.get_selected_row()
			if data is not None:
				self.db.speichereSQL(data[2], data[3].split(" <<Tren-ner>> "), rowid = self.noteid)
				logging.info("loading History")
				self.noteslist_changed()

		dialog.destroy()
