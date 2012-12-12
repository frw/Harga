'''
Created on Jun 5, 2012

@author: Frederick
'''

from sugar.activity import activity
import agromaret
import bulog
import datetime
import gtk
import os
import pygtk
import string
import thread
import threading
import time

pygtk.require('2.0')

COLOR_BLUE = gtk.gdk.color_parse('#87CEEB')
COLOR_PINK = gtk.gdk.color_parse('#FFC0CB')
COLOR_WHITE = gtk.gdk.color_parse('#FFFFFF')
COLOR_GREEN = gtk.gdk.color_parse('#00FF00')
COLOR_RED = gtk.gdk.color_parse('#FF0000')
COLOR_BLACK = gtk.gdk.color_parse('#000000')
HARGA_FILE = 'harga.txt'

class Harga(activity.Activity):
    last_crawled = None
    bulog_labels = [[gtk.Label() for c in xrange(0, 4, 1)] for r in xrange(0, 11, 1)]
    agromaret_labels = [[gtk.Label() for c in xrange(0, 4, 1)] for r in xrange(0, 10, 1)]
    crawl_lock = threading.Lock()
        
    def show_prices(self):
        self.set_canvas(self.prices)
        
    def show_loading(self):
        self.set_canvas(self.loading)
    
    def show_error(self):
        self.set_canvas(self.error)
        
    def set_loading_message(self, message):
        self.label_wait.set_markup('<span size="xx-large">' + message + '</span>')
          
    def update_bulog_table(self):
        self.bulog_label_price1.set_markup('<span weight="bold" size="x-large">Harga' + bulog.date1 + '</span>')
        self.bulog_label_price2.set_markup('<span weight="bold" size="x-large">Harga' + bulog.date2 + '</span>')
        for i in xrange(0, 11, 1):
            row = self.bulog_labels[i]
            item = bulog.items[i]
            row[0].set_markup('<span size="large">' + item.name + '</span>')
            row[1].set_markup('<span size="large">' + item.price1 + 'Rp/Kg</span>')
            row[2].set_markup('<span size="large">' + item.price2 + 'Rp/Kg</span>')
            change = row[3]
            p1 = int(string.replace(item.price1, '.', ''))
            p2 = int(string.replace(item.price2, '.', ''))
            d = p2 - p1
            if d > 0:
                change.modify_fg(gtk.STATE_NORMAL, COLOR_GREEN)
                change.set_markup('<span size="large">+' + str(d) + '</span>')
            else:
                change.modify_fg(gtk.STATE_NORMAL, COLOR_RED if d < 0 else COLOR_BLACK)
                change.set_markup('<span size="large">' + str(d) + '</span>')
                
    def update_agromaret_table(self, page):
        off = (page - 1) * 10
        for i in xrange(0, 10, 1):
            row = self.agromaret_labels[i]
            item = agromaret.items[off + i]
            row[0].set_markup('<span size="large">' + item.name + '</span>')
            row[1].set_markup('<span size="large">' + item.price + 'Rp/' + item.unit + '</span>')
            row[2].set_markup('<span size="large">' + item.city + '</span>')
            row[3].set_markup('<span size="large">' + item.date + '</span>')
    
    def mark_last_crawled(self): 
        try:
            with open(HARGA_FILE, 'w') as f:
                f.write(str(self.last_crawled.toordinal()))
            return True
        except IOError as e:
            print e
        return False
    
    def load_last_crawled(self):
        if os.path.isfile(HARGA_FILE):
            try:
                with open(HARGA_FILE, 'r') as f:
                    self.last_crawled = datetime.date.fromordinal(int(f.read()))
                return True
            except IOError as e:
                print e
        return False

    def crawl_periodically(self):
        while self.get_visible():
            self.crawl(False)
            time.sleep(300)

    def crawl(self, force):
        with self.crawl_lock:
            current_time = datetime.date.today()
            if force or self.last_crawled == None or current_time.day > self.last_crawled.day:
                self.set_loading_message('Mohon Tunggu Sebentar')
                self.show_loading()
                self.set_loading_message('Sedang Ambil Data Dari Agromaret')
                if agromaret.crawl():
                    self.set_loading_message('Sedang Ambil Data Dari Bulog')
                    if bulog.crawl():
                        self.last_crawled = current_time
                        self.mark_last_crawled()
                        self.update_bulog_table()
                        if self.agromaret_combo_page.get_active() == 1:
                            self.update_agromaret_table(1)
                        else:
                            self.agromaret_combo_page.set_active(1)
                        self.set_loading_message('Sudah Selesai!')
                        self.show_prices()
                        return
                self.show_error()
    
    def update_prices(self, button):
        thread.start_new_thread(self.crawl, (True,))      
    
    def agromaret_page_changed(self, combobox):
        active = combobox.get_active()
        if active > 0:
            self.update_agromaret_table(active)
    
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        self.toolbox = activity.ActivityToolbox(self)
        self.activity_toolbar = self.toolbox.get_activity_toolbar()
        self.activity_toolbar.keep.props.visible = False
        self.activity_toolbar.share.props.visible = False
        self.set_toolbox(self.toolbox)
        self.toolbox.show()
        
        self.prices = gtk.VBox(False, 10)
        
        self.button_update = gtk.Button('Perbarui Sekarang')
        self.button_update.connect('clicked', self.update_prices)
        align = gtk.Alignment(1, 0, 0, 0)
        align.add(self.button_update)
        self.button_update.show()
        self.prices.pack_start(align, False, False)
        align.show()
        
        self.tables = gtk.Notebook()
        
        self.bulog = gtk.VBox(False, 10)
        
        self.bulog_scrolled_window = gtk.ScrolledWindow()
        self.bulog_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.bulog_viewport = gtk.Viewport()
        self.bulog_viewport.modify_bg(gtk.STATE_NORMAL, COLOR_WHITE)
        
        self.bulog_table = gtk.Table(13, 7)
        
        self.bulog_label_name = gtk.Label()
        self.bulog_label_name.set_markup('<span weight="bold" size="x-large">Nama</span>')
        self.bulog_table.attach(self.bulog_label_name, 0, 1, 0, 1)
        self.bulog_label_name.show()
        
        self.bulog_label_price1 = gtk.Label()
        self.bulog_table.attach(self.bulog_label_price1, 2, 3, 0, 1)
        self.bulog_label_price1.show()
        
        self.bulog_label_price2 = gtk.Label()
        self.bulog_table.attach(self.bulog_label_price2, 4, 5, 0, 1)
        self.bulog_label_price2.show()
        
        self.bulog_label_change = gtk.Label()
        self.bulog_label_change.set_markup('<span weight="bold" size="x-large">Perubahan</span>')
        self.bulog_table.attach(self.bulog_label_change, 6, 7, 0, 1)
        self.bulog_label_change.show()
        
        for c in xrange(1, 7, 2):
            separator = gtk.VSeparator()
            self.bulog_table.attach(separator, c, c + 1, 0, 13, gtk.SHRINK, gtk.SHRINK)
            separator.show()
        
        separator = gtk.HSeparator()
        self.bulog_table.attach(separator, 0, 7, 1, 2, gtk.SHRINK, gtk.SHRINK)
        separator.show()
        
        for r in xrange(2, 13, 1):
            for c in xrange(0, 7, 2):
                label = self.bulog_labels[r - 2][c / 2]
                viewport = gtk.Viewport()
                viewport.set_shadow_type(gtk.SHADOW_NONE)
                viewport.modify_bg(gtk.STATE_NORMAL, COLOR_BLUE if r % 2 == 0 else COLOR_PINK)
                viewport.add(label)
                label.show()
                self.bulog_table.attach(viewport, c, c + 1, r, r + 1)
                viewport.show()
        
        self.bulog_viewport.add(self.bulog_table)
        self.bulog_table.show()
        
        self.bulog_scrolled_window.add(self.bulog_viewport)
        self.bulog_viewport.show()
        
        self.bulog.pack_start(self.bulog_scrolled_window, True, True)
        self.bulog_scrolled_window.show();
        
        self.bulog_tab_label = gtk.Label()
        self.bulog_tab_label.set_markup('<span size="xx-large">Beras</span>')
        
        self.tables.append_page(self.bulog, self.bulog_tab_label);
        self.bulog.show()
        self.bulog_tab_label.show()
        
        self.agromaret = gtk.VBox(False, 10)
        
        self.agromaret_scrolled_window = gtk.ScrolledWindow()
        self.agromaret_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.agromaret_viewport = gtk.Viewport()
        self.agromaret_viewport.modify_bg(gtk.STATE_NORMAL, COLOR_WHITE)
        
        self.agromaret_table = gtk.Table(12, 7)
        
        self.agromaret_label_name = gtk.Label()
        self.agromaret_label_name.set_markup('<span weight="bold" size="x-large">Nama</span>')
        self.agromaret_table.attach(self.agromaret_label_name, 0, 1, 0, 1)
        self.agromaret_label_name.show()
        
        self.agromaret_label_price = gtk.Label()
        self.agromaret_label_price.set_markup('<span weight="bold" size="x-large">Harga</span>')
        self.agromaret_table.attach(self.agromaret_label_price, 2, 3, 0, 1)
        self.agromaret_label_price.show()
        
        self.agromaret_label_city = gtk.Label()
        self.agromaret_label_city.set_markup('<span weight="bold" size="x-large">Kota</span>')
        self.agromaret_table.attach(self.agromaret_label_city, 4, 5, 0, 1)
        self.agromaret_label_city.show()
        
        self.agromaret_label_date = gtk.Label()
        self.agromaret_label_date.set_markup('<span weight="bold" size="x-large">Tanggal</span>')
        self.agromaret_table.attach(self.agromaret_label_date, 6, 7, 0, 1)
        self.agromaret_label_date.show()
        
        for c in xrange(1, 7, 2):
            separator = gtk.VSeparator()
            self.agromaret_table.attach(separator, c, c + 1, 0, 12, gtk.SHRINK, gtk.SHRINK)
            separator.show()
        
        separator = gtk.HSeparator()
        self.agromaret_table.attach(separator, 0, 7, 1, 2, gtk.SHRINK, gtk.SHRINK)
        separator.show()
            
        for r in xrange(2, 12, 1):
            for c in xrange(0, 7, 2):
                label = self.agromaret_labels[r - 2][c / 2]
                viewport = gtk.Viewport()
                viewport.set_shadow_type(gtk.SHADOW_NONE)
                viewport.modify_bg(gtk.STATE_NORMAL, COLOR_BLUE if r % 2 == 0 else COLOR_PINK)
                viewport.add(label)
                label.show()
                self.agromaret_table.attach(viewport, c, c + 1, r, r + 1)
                viewport.show()
        
        self.agromaret_viewport.add(self.agromaret_table)
        self.agromaret_table.show()
        
        self.agromaret_scrolled_window.add(self.agromaret_viewport)
        self.agromaret_viewport.show()
        
        self.agromaret.pack_start(self.agromaret_scrolled_window, True, True)
        self.agromaret_scrolled_window.show()
        
        self.agromaret_page = gtk.HBox(False, 5)
        
        self.agromaret_label_page = gtk.Label()
        self.agromaret_label_page.set_markup('<span size="x-large">Halaman</span>')
        self.agromaret_page.pack_start(self.agromaret_label_page, False, False)
        self.agromaret_label_page.show()
        
        self.agromaret_combo_page = gtk.combo_box_new_text()
        self.agromaret_combo_page.append_text('')
        for i in xrange(1, 11, 1):
            self.agromaret_combo_page.append_text(str(i))
        self.agromaret_combo_page.set_active(1)
        self.agromaret_combo_page.connect('changed', self.agromaret_page_changed)
        self.agromaret_page.pack_start(self.agromaret_combo_page, False, False)
        self.agromaret_combo_page.show()
        
        align = gtk.Alignment(0.5, 0, 0, 0)
        align.add(self.agromaret_page)
        self.agromaret_page.show()
        self.agromaret.pack_start(align, False, False)
        align.show()
        
        self.agromaret_tab_label = gtk.Label()
        self.agromaret_tab_label.set_markup('<span size="xx-large">Lainnya</span>')
        
        self.tables.append_page(self.agromaret, self.agromaret_tab_label);
        self.agromaret.show()
        self.agromaret_tab_label.show()
        
        self.prices.pack_start(self.tables, True, True)
        self.tables.show()
        
        self.prices.show()
        
        self.loading = gtk.VBox(False, 10)
        
        self.spinner = gtk.Spinner()
        self.spinner.start()
        self.loading.pack_start(self.spinner, True, True)
        self.spinner.show()
        
        self.label_wait = gtk.Label()
        self.loading.pack_start(self.label_wait, False, False)
        self.label_wait.show()
        
        self.loading.show()
        
        self.error = gtk.VBox(False, 10)
        
        self.label_error_message = gtk.Label()
        self.label_error_message.set_markup('<span size="xx-large">Tidak bisa akses situs web</span>')
        align = gtk.Alignment(0.5, 1.0, 0, 0)
        align.add(self.label_error_message)
        self.label_error_message.show()
        self.error.pack_start(align, True, True)
        align.show()
        
        self.button_try_again = gtk.Button('Coba lagi')
        self.button_try_again.connect('clicked', self.update_prices)
        align = gtk.Alignment(0.5, 0, 0, 0)
        align.add(self.button_try_again)
        self.button_try_again.show()
        self.error.pack_start(align, True, True)
        align.show()
        
        self.error.show()
        
        if self.load_last_crawled() and datetime.date.today().day <= self.last_crawled.day and agromaret.load_prices() and bulog.load_prices():
            self.update_bulog_table()
            self.update_agromaret_table(1)
            self.show_prices()
        else:
            thread.start_new_thread(self.crawl, (True,))
        thread.start_new_thread(self.crawl_periodically, ())