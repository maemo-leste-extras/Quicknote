#!/usr/bin/python2.5

import os

try:
	import py2deb
except ImportError:
	import fake_py2deb as py2deb


__appname__ = "quicknote"
__description__ = "Simple note taking application in a similar vein as PalmOS Memos"
__author__ = "Christoph Wurstle"
__email__ = "n800@axique.net"
__version__ = "0.7.7"
__build__ = 0
__changelog__ = '''
0.7.7
 * Slight modifications to the note history and SQL dialogs
 * On zoom, also hiding the history status and button
 * Touched up the note list, making it ellipsize at the end rather than scroll

0.7.6
  * Line-wrap
  * Zoom

0.7.4
  * fixed small bugs
  * move category

0.7.3
  * fixed small bugs
  * move category

0.7.2
  * improved sync, fixed a small bug

0.7.1
  * improved sync

0.7.0
  * Initial Release.
'''


__postinstall__ = '''#!/bin/sh -e

gtk-update-icon-cache -f /usr/share/icons/hicolor
exit 0
'''


def find_files(path, root):
	print path, root
	for unusedRoot, dirs, files in os.walk(path):
		for file in files:
			if file.startswith(root+"-"):
				print "\t", root, file
				fileParts = file.split("-")
				unused, relPathParts, newName = fileParts[0], fileParts[1:-1], fileParts[-1]
				assert unused == root
				relPath = os.sep.join(relPathParts)
				yield relPath, file, newName


def unflatten_files(files):
	d = {}
	for relPath, oldName, newName in files:
		if relPath not in d:
			d[relPath] = []
		d[relPath].append((oldName, newName))
	return d


if __name__ == "__main__":
	try:
		os.chdir(os.path.dirname(sys.argv[0]))
	except:
		pass

	p = py2deb.Py2deb(__appname__)
	p.description = __description__
	p.author = __author__
	p.mail = __email__
	p.license = "lgpl"
	p.depends = "python2.5, python2.5-gtk2"
	p.section = "user/other"
	p.arch = "all"
	p.urgency = "low"
	p.distribution = "chinook diablo"
	p.repository = "extras-devel"
	p.changelog = __changelog__
	p.postinstall = __postinstall__
	p.icon = "26x26-quicknote.png"
	p["/usr/bin"] = [ "quicknote.py" ]
	for relPath, files in unflatten_files(find_files(".", "locale")).iteritems():
		fullPath = "/usr/share/locale"
		if relPath:
			fullPath += os.sep+relPath
		p[fullPath] = list(
			"|".join((oldName, newName))
			for (oldName, newName) in files
		)
	for relPath, files in unflatten_files(find_files(".", "src")).iteritems():
		fullPath = "/usr/lib/quicknote"
		if relPath:
			fullPath += os.sep+relPath
		p[fullPath] = list(
			"|".join((oldName, newName))
			for (oldName, newName) in files
		)
	p["/usr/share/applications/hildon"] = ["quicknote.desktop"]
	p["/usr/share/dbus-1/services"] = ["quicknote.service"]
	p["/usr/share/icons/hicolor/26x26/hildon"] = ["26x26-quicknote.png|quicknote.png"]
	p["/usr/share/icons/hicolor/40x40/hildon"] = ["40x40-quicknote.png|quicknote.png"]
	p["/usr/share/icons/hicolor/48x48/hildon"] = ["48x48-quicknote.png|quicknote.png"]
	p["/usr/share/icons/hicolor/scalable/hildon"] = ["scale-quicknote.png|quicknote.png"]

	print p
	print p.generate(
		__version__, __build__, changelog=__changelog__,
		tar=True, dsc=True, changes=True, build=False, src=True
	)
