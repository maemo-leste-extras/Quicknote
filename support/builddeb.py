#!/usr/bin/python2.5

import os
import sys

try:
	import py2deb
except ImportError:
	import fake_py2deb as py2deb

import constants


__appname__ = constants.__app_name__
__description__ = """Simple note taking application in a similar vein as PalmOS Memos
.
Homepage: http://quicknote.garage.maemo.org/
"""
__author__ = "Christoph Wurstle"
__email__ = "n800@axique.net"
__version__ = constants.__version__
__build__ = constants.__build__
__changelog__ = """
* New icon
""".strip()


__postinstall__ = """#!/bin/sh -e

gtk-update-icon-cache -f /usr/share/icons/hicolor
rm -f ~/.quicknote/quicknote.log
"""


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


def build_package(distribution):
	try:
		os.chdir(os.path.dirname(sys.argv[0]))
	except:
		pass

	py2deb.Py2deb.SECTIONS = py2deb.SECTIONS_BY_POLICY[distribution]
	p = py2deb.Py2deb(__appname__)
	p.prettyName = constants.__pretty_app_name__
	p.description = __description__
	p.bugTracker = "https://bugs.maemo.org/enter_bug.cgi?product=quicknote"
	p.upgradeDescription = __changelog__.split("\n\n", 1)[0]
	p.author = __author__
	p.mail = __email__
	p.license = "gpl"
	p.depends = ", ".join([
		"python2.6 | python2.5",
		"python-gtk2 | python2.5-gtk2",
		"python-xml | python2.5-xml",
		"python-dbus | python2.5-dbus",
	])
	maemoSpecificDepends = ", python-osso | python2.5-osso, python-hildon | python2.5-hildon"
	p.depends += {
		"debian": ", python-glade2",
		"diablo": maemoSpecificDepends,
		"fremantle": maemoSpecificDepends + ", python-glade2",
	}[distribution]
	p.section = {
		"debian": "editors",
		"diablo": "user/office",
		"fremantle": "user/office",
	}[distribution]
	p.arch = "all"
	p.urgency = "low"
	p.distribution = "diablo fremantle debian"
	p.repository = "extras"
	p.changelog = __changelog__
	p.postinstall = __postinstall__
	p.icon = {
		"debian": "24_quicknote.png",
		"diablo": "32_quicknote.png",
		"fremantle": "48_quicknote.png", # Fremantle natively uses 48x48
	}[distribution]
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
	p["/usr/share/icons/hicolor/24x24/hildon"] = ["24_quicknote.png|quicknote.png"]
	p["/usr/share/icons/hicolor/32x32/hildon"] = ["32_quicknote.png|quicknote.png"]
	p["/usr/share/icons/hicolor/48x48/hildon"] = ["48_quicknote.png|quicknote.png"]
	p["/usr/share/icons/hicolor/72x72/hildon"] = ["72_quicknote.png|quicknote.png"]

	if distribution == "debian":
		print p
		print p.generate(
			version="%s-%s" % (__version__, __build__),
			changelog=__changelog__,
			build=True,
			tar=False,
			changes=False,
			dsc=False,
		)
		print "Building for %s finished" % distribution
	else:
		print p
		print p.generate(
			version="%s-%s" % (__version__, __build__),
			changelog=__changelog__,
			build=False,
			tar=True,
			changes=True,
			dsc=True,
		)
		print "Building for %s finished" % distribution


if __name__ == "__main__":
	if len(sys.argv) > 1:
		try:
			import optparse
		except ImportError:
			optparse = None

		if optparse is not None:
			parser = optparse.OptionParser()
			(commandOptions, commandArgs) = parser.parse_args()
	else:
		commandArgs = None
		commandArgs = ["diablo"]
	build_package(commandArgs[0])
