#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Copyright (C) 2007 Christoph Würstle

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
"""


import sys
import os
import time
import sqlite3
import shelve
import logging


try:
	_
except NameError:
	_ = lambda x: x


class Speichern():

	def __init__(self):
		home_dir = os.path.expanduser('~')
		filename = os.path.join(home_dir, ".quicknote.dat")
		self.d = shelve.open(filename)
		self.openDB()

	def speichereDirekt(self, schluessel, daten):
		self.d[schluessel] = daten
		logging.info("speichereDirekt "+str(schluessel)+" "+str(daten)+" lesen: "+str(self.d[schluessel]))

	def ladeDirekt(self, schluessel, default = ""):
		if (self.d.has_key(schluessel) == True):
			data = self.d[schluessel]
			return data
		else:
			return default

	def speichereSQL(self, sql, tupel = None, commit = True, host = "self", log = True, pcdatum = None, rowid = ""):
		try:
			programSQLError = True
			if tupel is None:
				self.cur.execute(sql)
			else:
				self.cur.execute(sql, tupel)
			programSQLError = False

			if (log == True):
				strtupel = []
				if tupel is not None:
					for t in tupel:
						strtupel.append(str(t))

				if pcdatum is None:
					pcdatum = int(time.time())
				self.cur.execute("INSERT INTO logtable ( pcdatum, sql, param, host, rowid ) VALUES (?, ?, ?, ?, ?)", (pcdatum, sql, " <<Tren-ner>> ".join(strtupel), host, str(rowid) ))
			if commit:
				self.conn.commit()

			return True
		except StandardError:
			s = str(sys.exc_info())
			if s.find(" already exists") == -1:
				if (programSQLError == True):
					logging.error("speichereSQL-Exception "+str(sys.exc_info())+" "+str(sql)+" "+str(tupel))
				else:
					logging.error("speichereSQL-Exception in Logging!!!! :"+str(sys.exc_info())+" "+str(sql)+" "+str(tupel))
			return False

	def commitSQL(self):
		self.conn.commit()

	def ladeSQL(self, sql, tupel = None):
		#print sql, tupel
		try:
			if tupel is None:
				self.cur.execute(sql)
			else:
				self.cur.execute(sql, tupel)
			return self.cur.fetchall()
		except StandardError:
			logging.error("ladeSQL-Exception "+str(sys.exc_info())+" "+str(sql)+" "+str(tupel))
			return ()

	def ladeHistory(self, sql_condition, param_condition):
		sql = "SELECT * FROM logtable WHERE sql LIKE '%"+str(sql_condition)+"%' AND param LIKE '%"+str(param_condition)+"%'"
		rows = self.ladeSQL(sql)
		#print rows 
		erg = []
		for row in rows:
			datum = time.strftime("%d.%m.%y %H:%M:%S", (time.localtime(row[1])))
			erg.append([row[1], datum, row[2], row[3], row[3].split(" <<Tren-ner>> ")])

		return erg

	def openDB(self):
		try:
			self.cur.close()
		except StandardError:
			pass
		try:
			self.conn.close()
		except StandardError:
			pass

		db = self.ladeDirekt("datenbank")
		if db == "":
			home_dir = os.path.expanduser('~')

			#on hildon user not home-dir but /home/user/MyDocs
			if home_dir == "/home/user":
				if os.path.exists(home_dir+os.sep+"MyDocs/"):
					home_dir = home_dir+os.sep+"MyDocs/"
			db = os.path.join(home_dir, "quicknote.s3db")

		self.conn = sqlite3.connect(db)
		self.cur = self.conn.cursor()
		try:
			sql = "CREATE TABLE logtable (id INTEGER PRIMARY KEY AUTOINCREMENT, pcdatum INTEGER , sql TEXT, param TEXT, host TEXT, rowid TEXT)"
			self.cur.execute(sql)
			self.conn.commit()
		except StandardError:
			pass

		#Add rowid line (not in old versions included)
		try:
			sql = "ALTER TABLE logtable ADD rowid TEXT"
			self.cur.execute(sql)
			self.conn.commit()
		except StandardError:
			pass

		#Create notes table
		try:
			sql = "CREATE TABLE notes (noteid TEXT, pcdatum INTEGER , category TEXT, note TEXT)"
			self.cur.execute(sql)
			self.conn.commit()
		except StandardError:
			pass

	def saveNote(self, noteid, note, category, pcdatum = None):
		if category == "%":
			category = ""
		sql = "SELECT noteid, pcdatum, category, note FROM notes WHERE noteid = ?"
		rows = self.ladeSQL(sql, (noteid, ))

		if rows is None or len(rows) == 0:
			sql = "INSERT INTO notes (noteid, pcdatum, category, note) VALUES (?, ?, ?, ?)"
			if pcdatum is None:
				pcdatum = int(time.time())
			self.speichereSQL(sql, (noteid, pcdatum, category, note), rowid = noteid)
		else:
			sql = "UPDATE notes SET category = ?, note = ?, pcdatum = ? WHERE noteid = ?"
			self.speichereSQL(sql, (category, note, str(int(time.time())), noteid), rowid = noteid)

	def loadNote(self, noteid):
		if noteid is None or str(noteid) == "":
			return (None, None, None)
		sql = "SELECT noteid, pcdatum, category, note FROM notes WHERE noteid = ?"
		rows = self.ladeSQL(sql, (noteid, ))
		if rows is None or len(rows) == 0:
			return None
		else:
			noteid, pcdatum, category, note = rows[0]
			return (noteid, pcdatum, category, note)

	def delNote(self, noteid):
		sql = "DELETE FROM notes WHERE noteid = ?"
		self.speichereSQL(sql, (noteid, ), rowid = noteid)

	def searchNotes(self, searchstring, category):
		sql = "SELECT noteid, category, note FROM notes WHERE note like ? AND category like ? ORDER BY note"
		rows = self.ladeSQL(sql, ("%"+searchstring+"%", category))
		if rows is None or len(rows) == 0:
			return None
		else:
			return rows

	def getNoteHistory(self, noteid):
		return self.ladeHistory("UPDATE notes ", noteid)

	def close(self):
		try:
			self.d.close()
		except StandardError:
			pass
		try:
			self.cur.close()
		except StandardError:
			pass
		try:
			self.conn.close()
		except StandardError:
			pass
		logging.info("Alle Data saved")

	def __del__(self):
		self.close()
