#! /usr/bin/env python2
# Example application for GtkTome

import random

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import gi
gi.require_version ('Gtk', '3.0')
from gi.repository import Gtk

win = Gtk.Window ()
win.connect ("delete-event", Gtk.main_quit)

from __init__ import Tome

windowbox = Gtk.VBox ()
win.add (windowbox)

tabbar = Gtk.HBox ()
windowbox.pack_start (tabbar, False, False, 0)

tome = Tome (133, True)
tabbar.pack_start (tome, True, True, 0)

lastbutton = Gtk.Button (label = "Last")
tabbar.pack_end (lastbutton, False, False, 0)
lastbutton.connect ("clicked", lambda button: tome.set_current_page (tome.get_n_pages () - 1))

shufflebutton = Gtk.Button (label = "Random")
tabbar.pack_end (shufflebutton, False, False, 0)

def shuffletabs (button = None):
    tome.set_current_page (random.randint (0, tome.get_n_pages () - 1))
    return True
shufflebutton.connect ("clicked", shuffletabs)

firstbutton = Gtk.Button (label = "First")
tabbar.pack_end (firstbutton, False, False, 0)
firstbutton.connect ("clicked", lambda button: tome.set_current_page (0))

removebutton = Gtk.Button (image = Gtk.Image (stock = Gtk.STOCK_REMOVE))
tabbar.pack_end (removebutton, False, False, 0)

def removetab (button = None):
    tome.remove_page (tome.get_current_page ())
    return True
removebutton.connect ("clicked", removetab)

addbutton = Gtk.Button (image = Gtk.Image (stock = Gtk.STOCK_ADD))
tabbar.pack_end (addbutton, False, False, 0)

total_append_count = 1000000
def addtab (button = None):
    global total_append_count
    npages = tome.get_n_pages ()
    tome.append_page (Gtk.Label ("Appended tab {} (tab {})".format (total_append_count, npages)))
    total_append_count += 1
    return True
addbutton.connect ("clicked", addtab)

mainarea = Gtk.VBox ()
windowbox.pack_start (mainarea, True, True, 0)

contents_label = Gtk.Label ()
mainarea.add (contents_label)

def switchtab (tome, tab_number):
    contents_label.set_label ("Tab {} contents go here...".format (tab_number))
    return True
tome.connect ("switch-tome-page", switchtab)

def make_label_closure (append_tab_num):
    def make_label (_tome, page_num):
        return Gtk.Label ("Appended tab {} (tab {})".format (append_tab_num,
                                                             page_num))
    return make_label
tome.bulk_append_pages ([make_label_closure (i) for i in xrange (1000000)])

tome.prepend_page (Gtk.Label ("Prepend tab title"))
tome.insert_page (Gtk.Label ("Insert tab title"), 1)

def fixtitles (tome, page_num):
    for i in xrange (page_num, tome.get_n_pages ()):
        label = tome.get_tab_label (i)
        if callable (label):
            continue
        text = tome.get_tab_label_text (i)
        if text.startswith ("Appended"):
            pfx, _ = text.rsplit (None, 1)
            tome.set_tab_label_text (i, "{} {})".format (pfx, i))
    return True
tome.connect ("tome-page-removed", fixtitles)

def addpage (tome, page_num):
    print "added", page_num
    return True
tome.connect ("tome-page-added", addpage)

def reorder (tome, old_page_num, new_page_num):
    lower = min (old_page_num, new_page_num)
    upper = max (old_page_num, new_page_num) + 1
    for i in xrange (lower, upper):
        label = tome.get_tab_label (i)
        if callable (label):
            continue
        text = tome.get_tab_label_text (i)
        if text.startswith ("Appended"):
            pfx, _ = text.rsplit (None, 1)
            tome.set_tab_label_text (i, "{} {})".format (pfx, i))
    return True
tome.connect ("tome-page-reordered", reorder)

win.show_all ()

Gtk.main ()
