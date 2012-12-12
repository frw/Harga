'''
Created on Jul 24, 2012

@author: Frederick
'''
import os
import re
import string
import urllib2

WEBSITE = 'http://www.agromaret.com/page/comm.php'

ROW_PATTERN = '\\s*<tr id="post_([0-9]+)" onmouseout="this.style.background=\'white\';" onmouseover="this.style.background=\'#FDFF7B\';">'
NAME_PATTERN = '\\s*<td class="t_label_1 t_border_1 valign_lt"><a href=".+" class="t_link_20">([^<>\\r\\n]+)</a></td>'
PRICE_PATTERN = '\\s*<td class="t_label_1 t_border_1 valign_rt">([^<>\\r\\n]+)</td>'
UNIT_PATTERN = '\\s*<td class="t_label_1 t_border_1 valign_ct">([^<>\\r\\n]+)</td>'
CITY_PATTERN = '\\s*<td class="t_label_1 t_border_1 valign_lt tipsy" title="(.+)">([^<>\\r\\n]+)</td>'
DATE_PATTERN = '\\s*<td class="t_label_1 t_border_1 valign_lt">([^<>\\r\\n]+)</td>'

SPLIT = "\t"

AGROMARET_FILE = 'agromaret.txt'

items = []

class Item:
    def __init__(self, name, price, unit, city, date2):
        self.name = name
        self.price = price
        self.unit = unit
        self.city = city
        self.date = date2
        
    def save(self, f):
        f.write(self.name)
        f.write(SPLIT)
        f.write(self.price)
        f.write(SPLIT)
        f.write(self.unit)
        f.write(SPLIT)
        f.write(self.city)
        f.write(SPLIT)
        f.write(self.date)
        f.write('\n')
        
def load_prices():
    if os.path.isfile(AGROMARET_FILE):
        try:
            with open(AGROMARET_FILE, 'r') as f:
                for line in f:
                    s = string.rstrip(line).split(SPLIT)
                    items.append(Item(s[0], s[1], s[2], s[3], s[4]))
            return True
        except IOError as e:
            print e
    return False
    
def save_prices():
    try:
        with open(AGROMARET_FILE, 'w') as f:
            for item in items:
                item.save(f)
        return True
    except IOError as e:
        print e
        return False
    
def clean(s):
    s = re.sub("(&nbsp;|\\s)+", " ", s)
    s = re.sub("&(?![#0-9a-zA-Z]+;)", "&amp;", s, re.IGNORECASE)
    return string.strip(s)
    
def crawl():
    del items[:]
    for i in xrange(0, 3, 1):
        try:
            conn = urllib2.urlopen(WEBSITE, timeout=10)
            found_row = False
            for line in conn.readlines():
                if found_row:
                    m = re.match(NAME_PATTERN, line)
                    if m != None:
                        name = clean(m.group(1))
                        continue
                    
                    m = re.match(PRICE_PATTERN, line)
                    if m != None:
                        price = clean(m.group(1))
                        continue
                    
                    m = re.match(UNIT_PATTERN, line)
                    if m != None:
                        unit = clean(m.group(1))
                        continue
                    
                    m = re.match(CITY_PATTERN, line)
                    if m != None:
                        city = clean(m.group(2)) + ' (' + clean(m.group(1)) + ')'
                        continue
                    
                    m = re.match(DATE_PATTERN, line)
                    if m != None:
                        date2 = clean(m.group(1))
                        items.append(Item(name, price, unit, city, date2))
                        found_row = False
                        continue
                    
                else:
                    m = re.match(ROW_PATTERN, line)
                    if m != None:
                        found_row = True
            save_prices();
            return True
        except IOError, e:
            print e
    return False
    
