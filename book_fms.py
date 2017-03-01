# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 13:25:44 2017

@author: Alfred
"""
from fms.main_window import MainWindow

from book.book_constants import DB

class BookFms(MainWindow):
    
    def __init__(self):
        flds = []
        for i in ['book', 'file']:
            flds += ['%s.%s' %(i,i2) for i2 in DB['book']['tbls'][i][0]]
        flds.append('tag')
        super(BookFms, self).__init__(flds)
        self.show()
        
