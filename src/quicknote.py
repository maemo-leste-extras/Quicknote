#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2007 Christoph Würstle
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
"""

import os
import sys
import logging
import gettext

_moduleLogger = logging.getLogger("quicknote")
gettext.install('quicknote', unicode = 1)
sys.path.append('/usr/lib/quicknote')


import constants
import quicknote_gtk


if __name__ == "__main__":
	try:
		os.makedirs(constants._data_path_)
	except OSError, e:
		if e.errno != 17:
			raise

	logging.basicConfig(level=logging.DEBUG, filename=constants._user_logpath_)
	_moduleLogger.info("quicknote %s-%s" % (constants.__version__, constants.__build__))

	quicknote_gtk.run_quicknote()
