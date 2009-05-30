#!/usr/bin/python

from __future__ import with_statement

import sys
import traceback
import functools
import contextlib
import warnings

import gobject
import gtk


@contextlib.contextmanager
def gtk_lock():
	gtk.gdk.threads_enter()
	try:
		yield
	finally:
		gtk.gdk.threads_leave()


def find_parent_window(widget):
	while True:
		parent = widget.get_parent()
		if isinstance(parent, gtk.Window):
			return parent
		widget = parent


def make_idler(func):
	"""
	Decorator that makes a generator-function into a function that will continue execution on next call
	"""
	a = []

	@functools.wraps(func)
	def decorated_func(*args, **kwds):
		if not a:
			a.append(func(*args, **kwds))
		try:
			a[0].next()
			return True
		except StopIteration:
			del a[:]
			return False

	return decorated_func


def asynchronous_gtk_message(original_func):
	"""
	@note Idea came from http://www.aclevername.com/articles/python-webgui/
	"""

	def execute(allArgs):
		args, kwargs = allArgs
		with gtk_lock():
			original_func(*args, **kwargs)
		return False

	@functools.wraps(original_func)
	def delayed_func(*args, **kwargs):
		gobject.idle_add(execute, (args, kwargs))

	return delayed_func


def synchronous_gtk_message(original_func):
	"""
	@note Idea came from http://www.aclevername.com/articles/python-webgui/
	"""

	@functools.wraps(original_func)
	def immediate_func(*args, **kwargs):
		with gtk_lock():
			return original_func(*args, **kwargs)

	return immediate_func


class ErrorDisplay(object):

	def __init__(self, widgetTree):
		super(ErrorDisplay, self).__init__()
		self.__errorBox = widgetTree.get_widget("errorEventBox")
		self.__errorDescription = widgetTree.get_widget("errorDescription")
		self.__errorClose = widgetTree.get_widget("errorClose")
		self.__parentBox = self.__errorBox.get_parent()

		self.__errorBox.connect("button_release_event", self._on_close)

		self.__messages = []
		self.__parentBox.remove(self.__errorBox)

	def push_message_with_lock(self, message):
		with gtk_lock():
			self.push_message(message)

	def push_message(self, message):
		if 0 < len(self.__messages):
			self.__messages.append(message)
		else:
			self.__show_message(message)

	def push_exception_with_lock(self, exception = None):
		with gtk_lock():
			self.push_exception(exception)

	def push_exception(self, exception = None):
		if exception is None:
			userMessage = str(sys.exc_value)
			warningMessage = str(traceback.format_exc())
		else:
			userMessage = str(exception)
			warningMessage = str(exception)
		self.push_message(userMessage)
		warnings.warn(warningMessage, stacklevel=3)

	def pop_message(self):
		if 0 < len(self.__messages):
			self.__show_message(self.__messages[0])
			del self.__messages[0]
		else:
			self.__hide_message()

	def _on_close(self, *args):
		self.pop_message()

	def __show_message(self, message):
		self.__errorDescription.set_text(message)
		self.__parentBox.pack_start(self.__errorBox, False, False)
		self.__parentBox.reorder_child(self.__errorBox, 1)

	def __hide_message(self):
		self.__errorDescription.set_text("")
		self.__parentBox.remove(self.__errorBox)


class DummyErrorDisplay(object):

	def __init__(self):
		super(DummyErrorDisplay, self).__init__()

		self.__messages = []

	def push_message_with_lock(self, message):
		self.push_message(message)

	def push_message(self, message):
		if 0 < len(self.__messages):
			self.__messages.append(message)
		else:
			self.__show_message(message)

	def push_exception(self, exception = None):
		if exception is None:
			warningMessage = traceback.format_exc()
		else:
			warningMessage = exception
		warnings.warn(warningMessage, stacklevel=3)

	def pop_message(self):
		if 0 < len(self.__messages):
			self.__show_message(self.__messages[0])
			del self.__messages[0]

	def __show_message(self, message):
		warnings.warn(message, stacklevel=2)


class MessageBox(gtk.MessageDialog):

	def __init__(self, message):
		parent = None
		gtk.MessageDialog.__init__(
			self,
			parent,
			gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_ERROR,
			gtk.BUTTONS_OK,
			message,
		)
		self.set_default_response(gtk.RESPONSE_OK)
		self.connect('response', self._handle_clicked)

	def _handle_clicked(self, *args):
		self.destroy()


class MessageBox2(gtk.MessageDialog):

	def __init__(self, message):
		parent = None
		gtk.MessageDialog.__init__(
			self,
			parent,
			gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_ERROR,
			gtk.BUTTONS_OK,
			message,
		)
		self.set_default_response(gtk.RESPONSE_OK)
		self.connect('response', self._handle_clicked)

	def _handle_clicked(self, *args):
		self.destroy()


class PopupCalendar(object):

	def __init__(self, parent, displayDate, title = ""):
		self._displayDate = displayDate

		self._calendar = gtk.Calendar()
		self._calendar.select_month(self._displayDate.month, self._displayDate.year)
		self._calendar.select_day(self._displayDate.day)
		self._calendar.set_display_options(
			gtk.CALENDAR_SHOW_HEADING |
			gtk.CALENDAR_SHOW_DAY_NAMES |
			gtk.CALENDAR_NO_MONTH_CHANGE |
			0
		)
		self._calendar.connect("day-selected", self._on_day_selected)

		self._popupWindow = gtk.Window()
		self._popupWindow.set_title(title)
		self._popupWindow.add(self._calendar)
		self._popupWindow.set_transient_for(parent)
		self._popupWindow.set_modal(True)
		self._popupWindow.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
		self._popupWindow.set_skip_pager_hint(True)
		self._popupWindow.set_skip_taskbar_hint(True)

	def run(self):
		self._popupWindow.show_all()

	def _on_day_selected(self, *args):
		try:
			self._calendar.select_month(self._displayDate.month, self._displayDate.year)
			self._calendar.select_day(self._displayDate.day)
		except StandardError, e:
			warnings.warn(e.message)


if __name__ == "__main__":
	if False:
		import datetime
		cal = PopupCalendar(None, datetime.datetime.now())
		cal._popupWindow.connect("destroy", lambda w: gtk.main_quit())
		cal.run()

	gtk.main()
