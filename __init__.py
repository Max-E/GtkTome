import math

import gi
gi.require_version ('Gtk', '3.0')
from gi.repository import Gtk, GObject

class Tome (Gtk.Notebook):

    __gsignals__ = {
        "switch-tome-page": (GObject.SIGNAL_RUN_LAST, None, (int,)),
        "tome-page-added": (GObject.SIGNAL_RUN_LAST, None, (int,)),
        "tome-page-removed": (GObject.SIGNAL_RUN_LAST, None, (int,)),
        "tome-page-reordered": (GObject.SIGNAL_RUN_LAST, None, (int, int,)),
    }

    def __init__ (self, tab_width, reorderable, *args, **kwargs):
        super (Tome, self).__init__ (*args, **kwargs)
        self.tab_width = tab_width
        self.true_idx = -1
        self.right_idx = 0
        self.label_widgets = []
        self.labels = []
        self.label_state = None
        self.suppress_switch = False
        self.connect_after ("switch-page", self._switch_page_cb)
        self.suppress_resize = False
        self.connect_after ("size-allocate", self._resize_cb)
        self.connect_after ("page-reordered", self._reorder_cb)
        self.reorderable = reorderable
        # tomes are always scrollable
        self.set_scrollable (True)
        self.set_scrollable = None
        # some APIs just don't make sense for tomes
        self.get_nth_page = None

    def _n_real_tabs (self):
        return super (Tome, self).get_n_pages ()

    def _update_labels (self):
        left_idx = self._get_left_idx ()
        # Suppress unnecessary label updating if nothing needs to change. This
        # is actually necessary because updating the label state during drag-
        # and-drop reordering breaks rendering.
        label_state = (left_idx, self.right_idx)
        if self.label_state == label_state:
            return
        self.label_state = label_state
        for i in xrange (self._n_real_tabs ()):
            dummychild = super (Tome, self).get_nth_page (i)
            super (Tome, self).set_tab_label (dummychild, None)
        for i in xrange (self._n_real_tabs ()):
            dummychild = super (Tome, self).get_nth_page (i)
            label = self.labels[i + left_idx]
            label.set_size_request (self.tab_width, -1)
            super (Tome, self).set_tab_label (dummychild, label)
        # We only want GTK's built-in resize calculations to happen here, not
        # any of our own stuff.
        old_suppress = self.suppress_resize
        self.suppress_resize = True
        self.resize_children ()
        self.suppress_resize = old_suppress

    def _update_tabs (self):
        old_suppress = self.suppress_switch
        self.suppress_switch = True
        true_idx = self.true_idx
        width = self.tab_width * self._n_real_tabs ()
        tabbar_width = self.get_allocation ().width
        targ = float (tabbar_width + 2 * self.tab_width - width) / self.tab_width
        targ_mag = int (math.ceil (abs (targ))) - 1
        if targ < 0:
            targ = self._n_real_tabs () - targ_mag - 1
            sub = self._n_real_tabs () - targ
            for _ in xrange (sub):
                self.right_idx = max (self.right_idx - 1, true_idx)
                super (Tome, self).remove_page (-1)
        else:
            targ = min (self.get_n_pages (), self._n_real_tabs () + targ_mag)
            add = targ - self._n_real_tabs ()
            for _ in xrange (add):
                dummychild = Gtk.Box ()
                # abuse unrelated object to hold data
                dummychild.childnum = self._n_real_tabs ()
                self.right_idx = min (self.right_idx + 1, self.get_n_pages ())
                super (Tome, self).append_page (dummychild, None)
                super (Tome, self).set_tab_reorderable (dummychild, self.reorderable)
        self.show_all ()
        self.realize ()
        self.set_current_page (true_idx)
        self.suppress_switch = old_suppress

    def _get_left_idx (self):
        assert self.right_idx is not None
        return self.right_idx - super (Tome, self).get_n_pages ()

    def _update_position (self):
        old_suppress = self.suppress_switch
        self.suppress_switch = True
        left_idx = self._get_left_idx ()
        page_num = self.true_idx - left_idx
        if page_num >= self._n_real_tabs () - 1 and self.right_idx < self.get_n_pages ():
            self.right_idx = min (self.true_idx + 2, self.get_n_pages ())
            super (Tome, self).set_current_page (0)
            super (Tome, self).set_current_page (self.true_idx - self._get_left_idx ())
        elif page_num <= 0 and left_idx > 0:
            last_real_tab = self._n_real_tabs () - 1
            # we want true_idx to be the first real tab
            self.right_idx = max (self.true_idx + last_real_tab, self._n_real_tabs ())
            super (Tome, self).set_current_page (last_real_tab)
            super (Tome, self).set_current_page (1)
        else:
            super (Tome, self).set_current_page (page_num)
        self._update_labels ()
        self.suppress_switch = old_suppress
        self.emit ("switch-tome-page", self.true_idx)

    def _switch_page_cb (self, _book, _, page_num):
        if self.suppress_switch:
            return False
        self.true_idx = self._get_left_idx () + page_num
        self._update_position ()
        return True

    def _resize_cb (self, *args):
        if self.suppress_resize:
            return
        self._update_tabs ()
        return True

    def _reorder_cb (self, _book, dummychild, page_num):
        left_idx = self._get_left_idx ()
        old_idx = left_idx + dummychild.childnum
        new_idx = left_idx + page_num
        label = self.labels.pop (old_idx)
        self.labels.insert (new_idx, label)
        for i in xrange (self._n_real_tabs ()):
            super (Tome, self).get_nth_page (i).childnum = i
        self.label_state = None
        self.set_current_page (new_idx)
        self.emit ("tome-page-reordered", old_idx, new_idx)
        return True

    def append_page (self, label):
        self.labels.append (label)
        self.emit ("tome-page-added", self.get_n_pages () - 1)
        self.right_idx = self.get_n_pages ()
        self._update_tabs ()
        self.set_current_page (-1)

    def prepend_page (self, label):
        return self.insert_page (label, 0)

    def insert_page (self, label, position):
        if position == -1:
            return self.append_page (label)
        if position < 0:
            position += self.get_n_pages ()
        self.labels.insert (position, label)
        self.emit ("tome-page-added", position)
        self.right_idx = max (self._n_real_tabs (), position)
        self.set_current_page (position)

    def bulk_append_pages (self, labels):
        inserted_page = self.get_n_pages () - 1 + min (1, len (labels))
        self.labels += labels
        self._update_tabs ()
        self.set_current_page (inserted_page)

    def bulk_prepend_pages (self, labels):
        return self.bukl_insert_pages (labels, 0)

    def bulk_insert_pages (self, labels, position):
        if position == -1:
            return self.bulk_append_pages (labels)
        if position < 0:
            position += self.get_n_pages ()
        self.labels = self.labels[:position] + labels + self.labels[position:]
        for i in xrange (position, len (labels)):
            self.emit ("tome-page-added", i)
        self.right_idx = max (self._n_real_tabs (), position)
        self.set_current_page (position)

    def get_n_pages (self):
        return len (self.labels)

    def get_current_page (self):
        left_idx = self._get_left_idx ()
        return left_idx + super (Tome, self).get_current_page ()

    def set_current_page (self, page_num):
        if page_num < 0:
            page_num += self.get_n_pages ()
        assert page_num < self.get_n_pages ()
        self.true_idx = page_num
        self._update_position ()

    def remove_page (self, page_num):
        if page_num < 0:
            page_num += self.get_n_pages ()
        assert page_num < self.get_n_pages ()
        removing_last = page_num + 1 == self.get_n_pages ()
        if self.true_idx > page_num or self.true_idx == page_num and removing_last:
            self.true_idx -= 1
        if self.right_idx > page_num:
            self.right_idx = max (self._n_real_tabs (), self.right_idx - 1)
        self.labels.pop (page_num)
        self.label_state = None
        self._update_tabs ()
        self.emit ("tome-page-removed", page_num)

    def set_tab_label (self, page_num, tab_label):
        if page_num < 0:
            page_num += self.get_n_pages ()
        assert page_num < self.get_n_pages ()
        self.labels[page_num] = tab_label
        if page_num >= self._get_left_idx () and page_num < self.right_idx:
            self.label_state = None
            self._update_labels ()

    def get_tab_label (self, page_num):
        if page_num < 0:
            page_num += self.get_n_pages ()
        assert page_num < self.get_n_pages ()
        return self.labels[page_num]

    def set_tab_label_text (self, page_num, tab_text):
        self.set_tab_label (page_num, Gtk.Label (tab_text))

    def get_tab_label_text (self, page_num):
        label = self.get_tab_label (page_num)
        if isinstance (label, Gtk.Label):
            return label.get_text ()
