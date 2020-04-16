#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-


from distutils.core import setup


setup(
	name='quicknote',
	version='1.0',
	scripts=['src/quicknote.py'],
	packages=['quicknote'],
	package_dir={'quicknote': 'src/'},
	data_files = [
		('share/icons/hicolor/32x32/hildon', ['data/32x32/quicknote.png']),
		('share/icons/hicolor/48x48/apps', ['data/48x48/quicknote.png']),
		('share/applications/hildon', ['data/quicknote.desktop']),
		('share/dbus-1/services', ['data/quicknote.service']),
		# I18N
		('share/locale/de/LC_MESSAGES', ['po/locale-de-LC_MESSAGES-quicknote.mo']),
		('share/locale/ru/LC_MESSAGES', ['po/locale-ru-LC_MESSAGES-quicknote.mo']),
	]
)
