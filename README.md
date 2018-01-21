# GtkTome
The GtkNotebook widget that really scales!

The Tome widget acts broadly similar to a GtkNotebook widget, but it's built to
scale up to many thousands of tabs without losing any responsiveness. If your
application isn't going to use thousands of tabs, you will not get any benefit
from using this instead of GtkNotebook, and you should use GtkNotebook instead.

Whereas GtkNotebook actually creates a tab widget for each tab, and frequently
tries to iterate through all of them, GtkTome creates only as many tab widgets
as are visible at the current time. Compared to an application using
GtkNotebook, an application using GtkTome will be able to start much more
quickly, because the overhead of creating all those tab widgets is saved. An
application using GtkTome will also be less computationally intensive during
rendering and will be able to maintain the same level of responsiveness
regardless of how many tabs it is using.

However, GtkTome has some limitations that GtkNotebook doesn't have.
 * Unlike GtkNotebook, it will not keep track of tab *contents* for you, only
   tab labels. You are responsible for listening to the switch-tome-page event
   and displaying whatever contents are appropriate below the GtkTome widget.
   Also, if your tab labels aren't unique, you are responsible for keeping
   track of what each tab number means as tabs are added, removed, and
   reordered.
 * Currently, tab labels may only be text.
 * While GtkNotebook allows you to choose whether each individual tab is
   reorderable, GtkTome requires you to choose whether or not every tab is
   reorderable.
 * The menu functionality is not implemented, and won't work.

Some of the signals from GtkNotebook will work with GtkTome, but for any signal
that calls its callbacks with "page_num" and "child" arguments, there should be
a "tome" version of that signal which provides only a "page_num" argument, and
you should use that version instead. So far, there is:
 * switch-tome-page: corresponds to switch-page. Callback will be called with
   the GtkTome object followed by the page number and any user data.
 * tome-page-added: corresponds to page-added. Callback will be called with the
   GtkTome object followed by the page number and any user data.
 * tome-page-removed: corresponds to page-removed. Callback will be called with
   the GtkTome object followed by the page number and any user data.
 * tome-page-reordered: corresponds to page-reordered. Callback will be called
   with the GtkTome object, followed by the old page number of the tab being
   moved, followed by the new page number of the tab being moved, followed by
   any user data.

