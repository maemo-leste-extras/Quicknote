import os

__pretty_app_name__ = "Quicknote"
__app_name__ = "quicknote"
__version__ = "0.7.13"
__build__ = 1
__app_magic__ = 0xdeadbeef
_data_path_ = os.path.join(os.path.expanduser("~"), ".%s" % __app_name__)
_user_logpath_ = "%s/%s.log" % (_data_path_, __app_name__)

