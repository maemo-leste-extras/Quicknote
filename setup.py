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
		('share/icons/hicolor/26x26/hildon', ['data/low/quicknote.png']),
		('share/icons/hicolor/40x40/hildon', ['data/40/quicknote.png']),
		#('share/icons/hicolor/48x48/apps', ['data/48/quicknote.png']),
		('share/icons/hicolor/scalable/hildon', ['data/scale/quicknote.png']),
		('share/applications/hildon', ['data/quicknote.desktop']),
		('share/dbus-1/services', ['data/quicknote.service']),
		# I18N
		('share/locale/de/LC_MESSAGES', ['locale/de/LC_MESSAGES/quicknote.mo']),
		('share/locale/ru/LC_MESSAGES', ['locale/ru/LC_MESSAGES/quicknote.mo']),
	]
)
