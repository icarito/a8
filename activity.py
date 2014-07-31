# -*- coding: utf-8 -*-
# (c) 2005-2012 PIDA Authors
# vim: ft=python sw=2 ts=2 sts=2 tw=80

import gtk
from pygtkhelpers.delegates import SlaveView
import gobject
import sys
from sugar.activity import activity
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toggletoolbutton import ToggleToolButton
from sugar.activity.widgets import ActivityButton
from sugar.activity.widgets import ActivityToolbox
from sugar.activity.widgets import TitleEntry
from sugar.activity.widgets import StopButton
from sugar.activity.widgets import ShareButton
from console.interactiveconsole import GTKInterpreterConsole


import collections
import os

from a8 import (terminals, files, buffers, vimembed, window, config, bookmarks,
                shortcuts, extensions, sessions)

class Abominade(object):
  """Abominade Monolith"""

  args = []

  def __init__(self, activity):
    self.signals = collections.defaultdict(list)
    self.home = config.InstanceDirectory()
    self.config = self.home.load_config()
    self.shortcuts = shortcuts.ShortcutManager(self)
    self.files = files.FileManager(self)
    self.buffers = buffers.BufferManager(self)
    self.terminals = terminals.TerminalManager(self)
    self.bookmarks = bookmarks.BookmarkManager(self)
    self.vim = vimembed.VimManager(self)
    self.ui = activity
    extensions.load_extensions(self)

    # do this after show so the window appears after abominade in launcher
    if self.config['terminal_window']:
      self.terminals.popinout()
    self.sessions = sessions.SessionManager(self)
    self.sessions.start()

  def start(self):
    """Start a8"""
    self.vim.start()
    self.files.browse()
    extensions.load_extension(self, "sugar-theme")

  def stop(self):
    """Stop a8"""
    self.sessions.save_session(polite=False)
    self.vim.stop()
    self.terminals.stop()

  def emit(self, signal, **kw):
    for callback in self.signals[signal]:
      callback(**kw)

  def connect(self, signal, callback):
    self.signals[signal].append(callback)

class AbominadeActivity(activity.Activity):
  """Abominade Monolith"""

  def __init__(self, handle):
    """Set up the activity."""
    activity.Activity.__init__(self, handle)

    """Create the user interface."""
    self.stack = gtk.VBox()
    self.add(self.stack)
    self.hpaned = gtk.HPaned()
    self.stack.pack_end(self.hpaned)
    self.vpaned = gtk.VPaned()
    self.hpaned.pack2(self.vpaned, shrink=False)
    self.hpaned.set_position(200)
    self.plugins = window.PluginTabs()
    self.hpaned.pack1(self.plugins.widget, shrink=False)

    self.model = Abominade(self)

    self.plugins.add_main(self.model.buffers)
    self.plugins.add_tab(self.model.files)
    self.plugins.add_tab(self.model.bookmarks)
    self.plugins.add_tab(self.model.terminals)
    self.vpaned.pack1(self.model.vim.widget, resize=True, shrink=False)
    self.vpaned.pack2(self.model.terminals.book, resize=False, shrink=False)
    # make sure buffers list isn't zero-height
    if self.plugins.stack.get_position() < 200:
      self.plugins.stack.set_position(200)
    
    self.stack.show_all()
    self.set_canvas(self.stack)

    self.init_interpreter()
    label = gtk.Label("Consola")
    self.model.terminals.book.prepend_page(self.interpreter, tab_label=label)

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

    self.sidebar_button = ToggleToolButton('folder')
    self.sidebar_button.set_active(True)
    self.sidebar_button.set_tooltip('Consola')
    self.sidebar_button.accelerator = "<Ctrl>grave"
    self.sidebar_button.connect('clicked', self.toggle_sidebar)
    toolbar_box.toolbar.insert(self.sidebar_button, -1)
    self.sidebar_button.show()

    self.bottom_button = ToggleToolButton('tray-show')
    self.bottom_button.set_active(True)
    self.bottom_button.set_tooltip('Consola')
    self.bottom_button.accelerator = "<Ctrl>grave"
    self.bottom_button.connect('clicked', self.toggle_bottom)
    toolbar_box.toolbar.insert(self.bottom_button, -1)
    self.bottom_button.show()

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

    self.model.start()

  def on_widget__delete_event(self, window, event):
    self.stop()
    return True

  def focus_files(self):
    self.plugins.focus_delegate(self.model.files)

  def focus_bookmarks(self):
    self.plugins.focus_delegate(self.model.bookmarks)

  def focus_terminals(self):
    self.plugins.focus_delegate(self.model.terminals)

  def focus_buffers(self):
    self.buffers.items.grab_focus()

  def focus_interpreter(self, widget, event):
    self.interpreter.text.grab_focus()
    return True

  def toggle_bottom(self, e):
    bottom = self.vpaned.get_child2()
    if bottom.props.visible:
      bottom.hide()
    else:
      bottom.show()

  def toggle_sidebar(self, e):
    sidebar = self.hpaned.get_child1()
    if sidebar.props.visible:
      sidebar.hide()
    else:
      sidebar.show()

  def init_interpreter(self):
    # diferido unos segundos para evitar ver errores superfluos al iniciar
    try:
        raise None
    except:
        frame = sys.exc_info()[2].tb_frame
    self.interpreter = GTKInterpreterConsole(frame)
    self.interpreter.text.connect('button-press-event', self.focus_interpreter)
    self.interpreter.show()
    return False

