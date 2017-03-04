# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 13:25:44 2017

@author: Alfred
"""
from PyQt5.QtWidgets import QGridLayout, QPushButton, QLineEdit

from utils.tag import Tag
from fms.main_window import MainWindow
from book.book_constants import DB

class BookFms(MainWindow):
    
    def __init__(self):
        self.tag = Tag('book')
        self.actions = {}

        self.start_gui()

        self.show()

    def start_gui(self):
        flds = []
        for i in ['book', 'file']:
            flds += ['%s.%s' %(i,i2) for i2 in DB['book']['tbls'][i][0]]
        flds.append('tag')
        super(BookFms, self).__init__(flds)
        self.set_button_zone()
        self.set_list_zone()
        
    def set_button_zone(self):
        self.sButton = QPushButton('Search')
        self.oButton = QPushButton('Order')
        self.rButton = QPushButton('Random')
        self.lineEdit = QLineEdit()

        grid = QGridLayout()
        grid.addWidget(self.sButton, 4, 0)
        grid.addWidget(self.oButton, 4, 1)
        grid.addWidget(self.rButton, 4, 2)
        grid.addWidget(self.lineEdit, 0, 0, 3, 3)
        self.button_zone.setLayout(grid)

    def set_list_zone(self):
        self.list_zone
        self.list_zone.print_screen([('1','1')])
        for i in self.list_zone.widget_list:
            i[1].OnDblClicked.connect(self.select)
        
        
        for i in self.list_zone.widgt_list():
            #.connect(select)
            #.connect(open)
            #.addAction(menu)
            pass

    def generator_action():
        rename=QAction()
        remove
        scan
        crawl
        modify
        delete
        tag
        select
        search
    
    #select
    def basic_select():
        self.list_zone.widget_list.set_label_color(idx,'blue')
    
    def select(self, event):
        
        self.list_zone.widget_list.set_label_color(idx,'blue')
        selected=set([index])
        
    def select_ctrl():
        selected.add
        pass
    
    def select_shift():
        selected.union()
        pass
    
    def get_index(self):
        idx = self.layout().indexOf(self.sender())
        r, c, w, h = self.layout().getItemPosition(idx)
        return (r-1)*10+c
    
    def remove():
        db.execute('delete')
        opr.remove()
    
    def rename():
        db.update()
        opr.rename()
        
    def scan():
        db.insert(opr.scan)
    
    def f_open():
        opr.open_file()
        
    def crawl():
        db.insert(spd.crawl)
        
    def modify():
        db.update()
        
    def delete():
        db.execute('delte')
        
    def tag():
        tag.modify()


if __name__=='__main__':
    bf = BookFms()