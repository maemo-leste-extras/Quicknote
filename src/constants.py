import os

__pretty_app_name__ = "Quicknote"
__app_name__ = "quicknote"
__version__ = "0.7.13"
__build__ = 1
_data_path_ = os.path.join(os.path.expanduser("~"), ".quicknote")
__app_magic__ = 0xdeadbeef
_user_logpath_ = "%s/quicknote.log" % _data_path_
