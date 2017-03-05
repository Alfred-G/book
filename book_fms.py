# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 13:25:44 2017

@author: Alfred
"""
import os
import math
import traceback

from PyQt5.QtWidgets import QGridLayout, QPushButton, QLineEdit, QAction, QMenu,\
    QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from utils.tag import Tag
from fms.main_window import MainWindow
from book.book_constants import DB
from book.book_file import BookFile
from book.book_spider import BookSpider
from utils.db_connector import DBcon


class BookFms(MainWindow):
    
    def __init__(self):
        try:
            self.tag = Tag('book')
            self.db = DBcon(DB['book'])
            self.book_file = BookFile()
            self.book_spider = BookSpider()
            
            super(BookFms, self).__init__(self.get_flds())
            self.set_button_zone()
            self.set_edit_zone()
            self.set_list_zone()
    
            self.selected = [set(),None]
    
            self.show()
        except:
            traceback.print_exc()

    @staticmethod
    def get_flds():
        flds = []
        for i in ['book', 'file']:
            flds += ['%s.%s' %(i,i2) for i2 in DB['book']['tbls'][i][0]]
        #flds.append('tag.name')
        return flds
        
    def set_button_zone(self):
        try:
            scan = QPushButton('Scan')
            crawl = QPushButton('Crawl')
            move = QPushButton('Move')
            delete = QPushButton('Delete')
            self.lineEdit = QLineEdit()

            self.lineEdit.returnPressed.connect(self.search)
            scan.clicked.connect(self.scan)
            crawl.clicked.connect(self.crawl)
            move.clicked.connect(self.rename)
            delete.clicked.connect(self.remove)
            
            grid = QGridLayout()
            grid.addWidget(self.lineEdit, 0, 0, 3, 4)
            grid.addWidget(scan, 4, 0)
            grid.addWidget(crawl, 4, 1)
            grid.addWidget(move, 4, 2)
            grid.addWidget(delete, 4, 3)
            self.button_zone.setLayout(grid)
        except:
            traceback.print_exc()

    def search(self):
        try:
            stmt = \
                'SELECT book.title, file.path, file.isbn '\
                    'FROM file LEFT JOIN book ON file.isbn = book.isbn '
            where = self.lineEdit.text()
            self.list_zone.info_list = [
                (i[0], i[1], i[2]) if i[0] \
                    else (os.path.basename(i[1]), i[1], i[2]) \
                    for i in self.db.execute(stmt + where)
            ]
            
            max_page = max(math.ceil(len(self.list_zone.info_list) / 42) - 1, 0)
            self.list_zone.slider.setMaximum(max_page)
            self.list_zone.slider.setValue(0)
            self.list_zone.slider.setFocus()
            
            self.list_zone.print_screen(self.list_zone.info_list[:42])
            #self.statusBar().showMessage(str(len(self.list_zone.info_list)))
        except:
            traceback.print_exc()
    
    def scan(self):
        path = 'E:/Documents'
        try:
            self.statusBar().showMessage('scan start')
            self.db.execute('update file set flag=0')
            self.db.sqlite_insert('file', self.book_file.add_isbn(path))
            self.db.execute('delete from file where flag=0')
            self.statusBar().showMessage('scan complete')
        except:
            traceback.print_exc()
        
    def crawl(self):
        try:
            stmt = 'select file.isbn from file left join book on file.isbn=book.isbn '\
                'where book.isbn is null and file.isbn!=""'
            self.statusBar().showMessage('crawl start')
            self.db.sqlite_insert(
                'book', self.book_spider.crawl([i[0] for i in self.db.execute(stmt)])
            )
            self.statusBar().showMessage('crawl complete')
        except:
            traceback.print_exc()
        
    def clean(self):
        pass
    
    def rename(self):
        try:
            dialog = QFileDialog()
            if len(self.selected[0]) > 1:
                dst = dialog.getExistingDirectory()
                if not dst:
                    return
                for i in self.selected[0]:
                    src = self.list_zone.info_list[i][1]
                    dst = os.path.join(dst, os.path.basename(src))
                    if self.book_file.rename(src, dst):
                        self.db.update('file', ['path'], [{'path': dst, '_pk': src}])
            elif self.selected[0]:
                for i in self.selected[0]:
                    src = self.list_zone.info_list[i][1]
                dst = dialog.getSaveFileName(
                        directory=src, filter='*.%s' % src.split('.')[-1]
                )
                if not dst[0]:
                    return
                dst = dst[0] + dst[1][1:]
                if self.book_file.rename(src, dst):
                    self.db.update('file', ['path'], [{'path': dst, '_pk': src}])
            else:
                return
        except:
            traceback.print_exc()

    def remove(self):
        try:
            for i in self.selected[0]:
                src = self.list_zone.info_list[i][1]
                dst = os.path.join('E:/remove', os.path.basename(src))
                if self.book_file.rename(src, dst):
                    self.db.execute('delete from file where path="%s"' % src)
        except:
            traceback.print_exc()
            
    def set_edit_zone(self):
        self.edit_zone.widget_dict['file.isbn'].returnPressed.connect(
            self.file_isbn_modify)
        
    def file_isbn_modify(self):
        try:
            self.db.update(
                'file', ['isbn'] ,
                [{'_pk': self.edit_zone.widget_dict['file.path'].text(),
                 'isbn': self.sender().text().replace('-','')}]
            )
            self.statusBar().showMessage('file.isbn modified')
        except:
            traceback.print_exc()
    ##########################################################################
    def set_list_zone(self):
        try:
            for i in self.list_zone.widget_list:
                i[1].OnClicked.connect(self.select)
                i[1].OnClickedCtrl.connect(self.select_ctrl)
                i[1].OnClickedShift.connect(self.select_shift)
                i[1].OnDblClicked.connect(self.open_file)
                i[1].OnDblClickedCtrl.connect(self.open_folder)
        except:
            traceback.print_exc()
            
    def basic_select(self, single = True):
        try:
            idx = self.get_idx()
            self.list_zone.set_label_color(idx, 'blue', single)
            
            idx += self.list_zone.slider.value() * 42
            self.show_info(idx)
            return idx
        except:
            traceback.print_exc()
    
    def select(self, event):
        idx = self.basic_select()
        self.selected = [set([idx]),idx]
        
    def select_ctrl(self):
        idx = self.basic_select(False)
        if idx in self.selected[0]:
            self.selected[0].remove(idx)
            if idx == self.selected[1]:
                self.selected[1] = max(self.selected[0])
            self.list_zone.set_label_color(idx % 42, 'black', False)
        else:
            self.selected[0].add(idx)
            self.selected[1] = idx

    def select_shift(self):
        idx = self.basic_select(False)
        if not self.selected[1]:
            return
        
        start = min(self.selected[1] % 42, idx % 42) + 1
        end = max(self.selected[1] % 42, idx % 42) + 1
        if start == end:
            return
        for i in range(start, end):
            self.list_zone.set_label_color(i, 'blue', False)
            
        start = min(self.selected[1], idx) + 1
        end = max(self.selected[1], idx) + 1
        self.selected[0] = self.selected[0].union(range(start, end))
        self.selected[1] = idx

    def get_idx(self):
        idx = self.list_zone.layout().indexOf(self.sender())
        r, c, w, h = self.list_zone.layout().getItemPosition(idx)
        return int(r / 2 * 7) + c
    
    def open_file(self):
        try:
            self.basic_select()
            for i in self.selected[0]:
                self.book_file.open_file(self.list_zone.info_list[i][1])
                break
        except:
            traceback.print_exc()

    def open_folder(self):
        try:
            self.basic_select()
            for i in self.selected[0]:
                self.book_file.open_file(
                    os.path.dirname(self.list_zone.info_list[i][1])
                )
                break
        except:
            traceback.print_exc()
            
    def show_info(self, idx):
        try:
            flds = self.get_flds()
            for i in self.db.execute(
                    'select %s from file left join book on file.isbn = book.isbn '\
                        # 'left join book_tag on book.id = book_tag.book_id '\
                        'where file.path = "%s" limit 1' \
                        % (','.join(flds), self.list_zone.info_list[idx][1])
                    ):
                for i2 in enumerate(i):
                    edit = self.edit_zone.widget_dict[flds[i2[0]]]
                    edit.setText(str(i2[1]))
                    edit.setCursorPosition(0)
        except:
            traceback.print_exc()
    
    ###########################################################################
    def modify(self):
        return
        path = self.edit_zone.widget_dict['file.path']
        isbn = self.edit_zone.widget_dict['file.isbn']
        for i in self.edit_zone.widget_dict.items():
            tbl, fld = i[0].split('.')
            if tbl =='file':
                self.db.update(tbl, [fld], {fld: i[1], 'path': path})
            elif tbl == 'book':
                self.db.update(tbl, [fld], {fld: i[1], 'isbn': isbn})

    def tag_modify(self):
        self.tag.modify()


if __name__=='__main__':
    bf = BookFms()
    
    """
        rename=QAction()
        remove
        scan
        crawl
        modify
        delete
        tag
        select
        search

    def item_menu(self):
        try:
            menu = QMenu()
            rename = QAction('Move', item)
            rename.triggered.connect(self.rename)
            remove = QAction('Delete', item)
            menu.addAction(rename)
            menu.addAction(remove)
            menu.exec_(QCursor.pos())
        except:
            traceback.print_exc()

    
                                #i[1].setContextMenuPolicy(Qt.CustomContextMenu)
                #i[1].customContextMenuRequested.connect(
                #        lambda x: self.menu()
                #)
                #.connect(open)
                #.addAction(menu)
    """