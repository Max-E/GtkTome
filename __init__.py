import math

import gi
gi.require_version ('Gtk', '3.0')
from gi.repository import Gtk, GObject

class Tome (Gtk.Notebook):

    __gsignals__ = {
        "switch-tome-page": (GObject.SIGNAL_RUN_LAST, None, (int,)),
        "tome-page-added": (GObject.SIGNAL_RUN_LAST, None, (int,)),
        "tome-page-removed": (GObject.SIGNAL_RUN_LAST, None, (int,)),
    }

    def __init__ (self, tab_width, *args, **kwargs):
        super (Tome, self).__init__ (*args, **kwargs)
        self.tab_width = tab_width
        self.true_idx = -1
        self.right_idx = 0
        self.label_widgets = []
        self.labels = []
        self.suppress_switch = False
        self.connect_after ("switch-page", self._switch_page_cb)
        self.connect_after ("size-allocate", self._resize_cb)
        # tomes are always scrollable
        self.set_scrollable (True)
        self.set_scrollable = None
        # some APIs just don't make sense for tomes
        self.get_nth_page = self.get_tab_label = self.set_tab_label = None

    def _n_real_tabs (self):
        n = len (self.label_widgets)
        assert n == super (Tome, self).get_n_pages ()
        return n

    def _update_labels (self):
        left_idx = self._get_left_idx ()
        for i, widget in enumerate (self.label_widgets):
            widget.set_text (self.labels[i + left_idx])

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
                self.label_widgets.pop ()
                super (Tome, self).remove_page (-1)
        else:
            targ = min (self.get_n_pages (), self._n_real_tabs () + targ_mag)
            add = targ - self._n_real_tabs ()
            for _ in xrange (add):
                l = Gtk.Label ("")
                l.set_size_request (self.tab_width, -1)
                self.label_widgets.append (l)
                self.right_idx = min (self.right_idx + 1, self.get_n_pages ())
                super (Tome, self).append_page (Gtk.Box (), l)
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
            self.right_idx = self.true_idx + last_real_tab
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
        self._update_tabs ()
        return True

    def append_page (self, label_text):
        self.labels.append (label_text)
        self.emit ("tome-page-added", self.get_n_pages () - 1)
        self.right_idx = self.get_n_pages ()
        self._update_tabs ()
        self.set_current_page (-1)

    def prepend_page (self, label_text):
        return self.insert_page (label_text, 0)

    def insert_page (self, label_text, position):
        if position == -1:
            return self.append_page (label_text)
        if position < 0:
            position += self.get_n_pages ()
        self.labels.insert (position, label_text)
        self.emit ("tome-page-added", position)
        self.right_idx = max (self._n_real_tabs (), position)
        self.set_current_page (position)

    def bulk_append_pages (self, label_texts):
        inserted_page = self.get_n_pages () - 1 + min (1, len (label_texts))
        self.labels += label_texts
        self._update_tabs ()
        self.set_current_page (inserted_page)

    def bulk_prepend_pages (self, label_texts):
        return self.bukl_insert_pages (label_texts, 0)

    def bulk_insert_pages (self, label_texts, position):
        if position == -1:
            return self.bulk_append_pages (label_text)
        if position < 0:
            position += self.get_n_pages ()
        self.labels = self.labels[:position] + label_texts + self.labels[position:]
        for i in xrange (position, len (label_texts)):
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
        if self.true_idx > page_num:
            self.true_idx -= 1
        if self.right_idx > page_num:
            self.right_idx = max (self._n_real_tabs (), self.right_idx - 1)
        self.labels.pop (page_num)
        self._update_tabs ()
        self.emit ("tome-page-removed", page_num)

    def set_tab_label_text (self, page_num, tab_text):
        if page_num < 0:
            page_num += self.get_n_pages ()
        assert page_num < self.get_n_pages ()
        self.labels[page_num] = tab_text
        self._update_labels ()

    def get_tab_label_text (self, page_num):
        if page_num < 0:
            page_num += self.get_n_pages ()
        assert page_num < self.get_n_pages ()
        return self.labels[page_num]
