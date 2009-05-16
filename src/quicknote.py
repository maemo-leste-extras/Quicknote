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
sys.path.append('/usr/lib/quicknote')

import locale
import gettext
gettext.install('quicknote', unicode = 1)

import libquicknote

if __name__ == "__main__":
	app = libquicknote.quicknoteclass()
	app.main()
