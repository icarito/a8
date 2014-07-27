# -*- coding: utf-8 -*-
# (c) 2005-2012 PIDA Authors
# vim: ft=python sw=2 ts=2 sts=2 tw=80

import gtk
import gobject
import sys
from sugar.activity import activity
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbutton import ToolButton
from sugar.activity.widgets import ActivityButton
from sugar.activity.widgets import ActivityToolbox
from sugar.activity.widgets import TitleEntry
from sugar.activity.widgets import StopButton
from sugar.activity.widgets import ShareButton
from console.interactiveconsole import GTKInterpreterConsole

"""Abominade Monolith."""

import collections
import argparse
import os

from a8 import (terminals, files, buffers, vimembed, window, config, bookmarks,
                shortcuts, extensions, sessions)

class Abominade(activity.Activity):
  """Abominade Monolith"""

  def __init__(self, handle):
    """Set up the activity."""
    activity.Activity.__init__(self, handle)
    self.signals = collections.defaultdict(list)
    self.home = config.InstanceDirectory()
    self.config = self.home.load_config()
    self.parse_args()
    if self.args.directory:
      os.chdir(self.args.directory)
    self.shortcuts = shortcuts.ShortcutManager(self)
    self.files = files.FileManager(self)
    self.buffers = buffers.BufferManager(self)
    self.terminals = terminals.TerminalManager(self)
    self.bookmarks = bookmarks.BookmarkManager(self)
    self.vim = vimembed.VimManager(self)
    self.ui = window.ApplicationWindow(self)
    self.ui.widget.maximize()
    # do this after show so the window appears after abominade in launcher
    if self.config['terminal_window']:
      self.terminals.popinout()
    self.sessions = sessions.SessionManager(self)
    self.sessions.start()
    extensions.load_extensions(self)
    extensions.load_extension(self, "sugar-theme")
    gobject.timeout_add(1000, self.init_interpreter)
    #self.init_interpreter()

    # we do not have collaboration features
    # make the share option insensitive
    self.max_participants = 1

    # toolbar with the new toolbar redesign
    toolbar_box = ToolbarBox()

    activity_button = ActivityButton(self)
    toolbar_box.toolbar.insert(activity_button, 0)
    activity_button.show()

    title_entry = TitleEntry(self)
    toolbar_box.toolbar.insert(title_entry, -1)
    title_entry.show()

    self.editor_button = ToolButton('sources')
    self.editor_button.set_tooltip('Consola')
    self.editor_button.accelerator = "<Ctrl>grave"
    self.editor_button.connect('clicked', self.toggle_console)
    toolbar_box.toolbar.insert(self.editor_button, -1)
    self.editor_button.show()

    share_button = ShareButton(self)
    toolbar_box.toolbar.insert(share_button, -1)
    share_button.show()

    separator = gtk.SeparatorToolItem()
    separator.props.draw = False
    separator.set_expand(True)
    toolbar_box.toolbar.insert(separator, -1)
    separator.show()

    stop_button = StopButton(self)
    toolbar_box.toolbar.insert(stop_button, -1)
    stop_button.show()

    self.set_toolbar_box(toolbar_box)
    toolbar_box.show()

  def toggle_console(self, e):
    if self._interpreter.props.visible:
      self._interpreter.hide()
    else:
      self._interpreter.show()
      self._interpreter.text.grab_focus()

  def toggle_sidebar(self, e):
    if self._interpreter.props.visible:
      self._interpreter.hide()
    else:
      self._interpreter.show()
      self._interpreter.text.grab_focus()

  def redraw(self):
    pass

  def focus_interpreter(self, widget, event):
    self._interpreter.text.grab_focus()
    return True

  def init_interpreter(self):
    # diferido unos segundos para evitar ver errores superfluos al iniciar
    try:
        raise None
    except:
        frame = sys.exc_info()[2].tb_frame
    self._interpreter = GTKInterpreterConsole(self.redraw, frame)
    self._interpreter.text.connect('button-press-event', self.focus_interpreter)
    self._interpreter.show()
    vbox = self.ui.widget.get_children()[0]
    newpaned = gtk.VPaned()
    newbox = gtk.HBox()
    vbox.reparent(newbox)
    newbox.show()
    newpaned.pack1(self._interpreter)
    newpaned.pack2(newbox)
    newpaned.show()
    self.set_canvas(newpaned)
    #self.set_canvas(vbox)
    self.start()
    self.ui.hide()
    return False

  def parse_args(self):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='Working directory to start in.')
    parser.add_argument('files', nargs='*', help='Files to open.')
    parser.add_argument('-s', '--session', action='store',
        choices=('user', 'local', 'none'),
        default=None,
        help='Maintain session per-user, per-working-dir, or no session.')
    parser.add_argument('--no-session', action='store_const', dest='session',
        const='none', help='Alias for --session=none.')
    parser.add_argument('--show-toolbar', action='store_true')
    parser.add_argument('-b')
    parser.add_argument('-a')
    parser.add_argument('-o')
    self.args = parser.parse_args()
    if self.args.session is not None:
      self.config.opts['session_type'] = self.args.session
    if self.args.show_toolbar:
      self.config.opts['toolbar'] = True

  def can_close(self):
    self.stop()
    return True

  def start(self):
    """Start a8"""
    self.vim.start()
    self.files.browse()
    self.ui.start()

  def stop(self):
    """Stop a8"""
    self.sessions.save_session(polite=False)
    self.vim.stop()
    self.terminals.stop()

  def emit(self, signal, **kw):
    for callback in self.signals[signal]:
      callback(**kw)

  #def connect(self, signal, callback):
  #  self.signals[signal].append(callback)
