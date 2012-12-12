'''
Created on Jul 24, 2012

@author: Frederick
'''

import os
import re
import string
import urllib2

WEBSITE = 'http://www.bulog.co.id'

DATE1_PATTERN = '\\s*<th>(\\([\\d/]+\\))</th>'
DATE2_PATTERN = '\\s*<th nowrap="nowrap" >(\\([\\d/]+\\))</th>'
NAME_PATTERN = '\\s*<td width="37%">([^<>\\r\\n]+)</td>'
PRICE1_PATTERN = '\\s*([^<>\\r\\n]+)</td>'
PRICE2_PATTERN = '\\s*<td width="31%" align="right">([^<>\\r\\n]+)</td>'

SPLIT = "\t"

BULOG_FILE = 'bulog.txt'

date1 = None
date2 = None
items = []

class Item:
    def __init__(self, name, price1, price2):
        self.name = name
        self.price1 = price1
        self.price2 = price2
        
    def save(self, f):
        f.write(self.name)
        f.write(SPLIT)
        f.write(self.price1)
        f.write(SPLIT)
        f.write(self.price2)
        f.write('\n')
        
def load_prices():
    global date1, date2
    
    if os.path.isfile(BULOG_FILE):
        try:
            with open(BULOG_FILE, 'r') as f:
                for line in f:
                    if date1 == None:
                        date1 = string.rstrip(line)
                    elif date2 == None:
                        date2 = string.rstrip(line)
                    else:
                        s = string.rstrip(line).split(SPLIT)
                        items.append(Item(s[0], s[1], s[2]))
            return True
        except IOError as e:
            print e
    return False
    
def save_prices():
    try:
        with open(BULOG_FILE, 'w') as f:
            f.write(date1 + '\n')
            f.write(date2 + '\n')
            for item in items:
                item.save(f)
        return True
    except IOError as e:
        print e
        return False
    
def crawl():
    global date1, date2
    
    del items[:]
    for i in xrange(0, 3, 1):
        try:
            conn = urllib2.urlopen(WEBSITE, timeout=10)
            for line in conn.readlines():
                m = re.match(DATE1_PATTERN, line)
                if m != None:
                    date1 = m.group(1)
                    continue
                
                m = re.match(DATE2_PATTERN, line)
                if m != None:
                    date2 = m.group(1)
                    continue
                
                m = re.match(NAME_PATTERN, line)
                if m != None:
                    name = m.group(1)
                    continue
                
                m = re.match(PRICE1_PATTERN, line)
                if m != None:
                    price1 = m.group(1)
                    continue
                    
                m = re.match(PRICE2_PATTERN, line)
                if m != None:
                    price2 = m.group(1)
                    items.append(Item(name, price1, price2))
                    continue
            save_prices();
            return True
        except IOError, e:
            print e
    return False
    