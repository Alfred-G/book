# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 13:25:44 2017

@author: Alfred
"""
import os
import math
import traceback

from PyQt5.QtWidgets import QGridLayout, QPushButton, QLineEdit,\
    QFileDialog
#from PyQt5.QtCore import Qt
#from PyQt5.QtGui import QCursor

from utils.tag import Tag
from fms.main_window import MainWindow, ListZone
from book.book_constants import DB, UNCLEAN_PATH, CLEAN_PATH, REMOVE_PATH
from book.book_file import BookFile
from book.book_spider import BookSpider
from utils.db_connector import DBcon


class BookFms(MainWindow):
    """
    fms
    """
    def __init__(self):
        try:
            # Gui Parts
            self.unclean_zone = ListZone('dirty')
            self.clean_zone = ListZone('file')
            
            # Functional Parts
            self.tag = Tag('book')
            self.db = DBcon(DB['book'])
            self.book_file = BookFile()
            self.book_spider = BookSpider()

            # Initial
            super(BookFms, self).__init__()
            self.set_button_zone()
            self.set_edit_zone('dirty')
            self.set_tab_zone()

            #self.show()
        except:
            traceback.print_exc()

    def create_table(self):
        try:
            tbls = DB['book']['tbls']
            for i in tbls.keys():
                flds, pk = tbls[i]
                stmt = \
                    'CREATE TABLE {tbl} ({flds}, PRIMARY KEY({pk}))'
                self.db.execute(stmt.format(
                    tbl=i, flds=','.join([' '.join(i) for i in flds]), pk=pk
                    )
                )
        except:
            traceback.print_exc()

    def set_button_zone(self):
        """
        1
        """
        try:
            scan = QPushButton('Scan')
            crawl = QPushButton('Crawl')
            move = QPushButton('Move')
            delete = QPushButton('Delete')
            self.lineEdit = QLineEdit()

            self.lineEdit.returnPressed.connect(self.search)
            scan.clicked.connect(self.scan)
            crawl.clicked.connect(self.crawl)
            move.clicked.connect(self.click_move)
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
            list_zone = self.tab_zone.currentWidget()
            stmt = \
                'SELECT {tbl}.path,'\
                       'book.isbn,'\
                       'book.isbn,'\
                    '   book.title,'\
                    '   {tbl}.path '\
                  'FROM {tbl} '\
             'LEFT JOIN book '\
                    'ON {tbl}.isbn = book.isbn '\
                .format(tbl=list_zone.name)
            if '#' in self.lineEdit.text():
                where, tag = self.lineEdit.text().split('#')
                tags = set()
                for i in self.tag.interpret(tag):
                    tags.update(set(self.tag.tag_to_item(i)))
                list_zone.info_list = [
                    (i[0], i[1], i[0]) if i[1] and i[0] in tags \
                        else (i[0], os.path.basename(i[2]), i[0]) \
                        for i in self.db.select(stmt + where)
                ]
            else:
                where = self.lineEdit.text()
                list_zone.info_list = []
                for i in self.db.select(stmt + where):
                    if i[3]:
                        list_zone.info_list.append(i)
                    elif i[0]:
                        list_zone.info_list.append(
                            (i[0], i[1], i[2], os.path.basename(i[0]), i[0])
                        )

            max_page = max(
                math.ceil(len(list_zone.info_list) / 42) - 1, 0
            )
            list_zone.slider.setMaximum(max_page)
            list_zone.slider.setValue(0)
            list_zone.slider.setFocus()
            
            list_zone.print_screen(list_zone.info_list[:42])
            self.statusBar().showMessage(str(len(list_zone.info_list)))
        except:
            traceback.print_exc()
    
    def scan(self):
        path = UNCLEAN_PATH
        try:
            self.statusBar().showMessage('scan start')
            self.db.execute('UPDATE dirty SET flag=0')
            self.db.sqlite_insert('dirty', self.book_file.add_isbn(path))
            self.db.execute('DELETE FROM dirty WHERE flag=0')
            self.statusBar().showMessage('scan complete')
        except:
            traceback.print_exc()
        
    def crawl(self):#
        try:
            stmt = 'SELECT dirty.isbn '\
                     'FROM dirty '\
                'LEFT JOIN book '\
                       'ON dirty.isbn = book.isbn '\
                    'WHERE book.isbn IS null AND dirty.isbn != ""'
            self.statusBar().showMessage('crawl start')
            self.db.sqlite_insert(
                'book', self.book_spider.crawl([i[0] for i in self.db.execute(stmt)])
            )
            self.statusBar().showMessage('crawl complete')
        except:
            traceback.print_exc()
        
    def name_format(self):#
        try:
            stmt = 'SELECT dirty.isbn, book.title FROM dirty JOIN book '\
                'ON dirty.isbn = book.isbn '\
                'WHERE dirty.isbn != "" AND book.title != ""'
            for i in self.db.execute(stmt):
                path = CLEAN_PATH
                isbn, title = i
                src = path
                dst = os.path.join(
                    os.path.dirname(path),
                    '%s isbn_%s.pdf' % ('_'.join(title.split(' ')), isbn)
                )
                self.rename(src, dst)
        except:
            traceback.print_exc()

    def move(self):
        try:
            list_zone = self.tab_zone.currentWidget()
            dialog = QFileDialog()
            if len(list_zone.selected[0]) > 1:
                dst = dialog.getExistingDirectory()
                if not dst:
                    return
                for i in list_zone[0]:
                    src = list_zone.info_list[i][1]
                    dst = os.path.join(dst, os.path.basename(src))
                    self.rename(src, dst)
            elif list_zone.selected[0]:
                for i in list_zone.selected[0]:
                    src = list_zone.info_list[i][0]
                dst = dialog.getSaveFileName(
                        directory=src, filter='*.%s' % src.split('.')[-1]
                )
                if not dst[0]:
                    return
                dst = dst[0] + dst[1][1:]
                self.rename(src, dst)
            else:
                return
        except:
            traceback.print_exc()
    
    def click_move(self):
        self.tab_zone.currentWidget().select()
        self.move()
            
    def rename(self, src, dst):
        try:
            list_zone = self.tab_zone.currentWidget()
            if self.book_file.rename(src, dst):
                self.db.update(list_zone.name, ['path'],
                               [{'path': dst, '_pk': src}])
        except:
            traceback.print_exc()
    
    def remove(self):
        try:
            list_zone = self.tab_zone.currentWidget()
            for i in list_zone[0]:
                src = list_zone.info_list[i][1]
                dst = os.path.join(REMOVE_PATH, os.path.basename(src))
                if self.book_file.rename(src, dst):
                    self.db.execute(
                        'delete from {tbl} where path="{path}"'\
                        .format(tbl=list_zone.name, path=src)
                    )
        except:
            traceback.print_exc()
    
    ####################################################################
    def set_edit_zone(self, name):
        try:
            for i in self.get_flds(name):
                self.edit_zone.add_widget(i)
            self.edit_zone.widget_dict['%s.isbn' % name]\
                .editingFinished.connect(self.file_isbn_modify)
            
            self.edit_zone.add_widget('tag')
            tag = self.edit_zone.widget_dict['tag']
            tag.editingFinished.connect(self.tag.modify)
        except:
            traceback.print_exc()

    @staticmethod
    def get_flds(tbl):
        try:
            tbls = DB['book']['tbls']
            flds = []
            for i in ['book', tbl]:
                flds += ['%s.%s' %(i,i2) for i2 in [i[0] for i in tbls[i][0]]]
            return flds
        except:
            traceback.print_exc()
    
    def file_isbn_modify(self):
        try:
            list_zone = self.tab_zone.currentWidget()
            self.db.update(
                list_zone.name, ['isbn'] ,
                [{'_pk': self.edit_zone.widget_dict['%s.path' \
                    % list_zone.name].text(),
                 'isbn': self.sender().text().replace('-','')}]
            )
            self.statusBar().showMessage('%s.isbn modified' % list_zone.name)
        except:
            traceback.print_exc()
            
    ####################################################################
    def set_tab_zone(self):
        try:
            self.tab_zone.addTab(self.unclean_zone, 'unclean')
            self.tab_zone.addTab(self.clean_zone, 'clean')
            self.tab_zone.currentChanged.connect(self.change_tab)
            
            self.set_list_zone(self.unclean_zone)
            self.set_list_zone(self.clean_zone)
        except:
            traceback.print_exc()

    def change_tab(self):
        try:
            keys = list(self.edit_zone.widget_dict.keys())
            for i in keys.copy():
                self.edit_zone.remove_widget(i)
    
            self.set_edit_zone(self.tab_zone.currentWidget().name)
        except:
            traceback.print_exc()

    def set_list_zone(self, list_zone):
        #info_list = [('a','b','c'),('d','e','f')]
        #list_zone.print_screen(info_list)
        try:
            for i in list_zone.widget_list:
                i[1].onSelected.connect(self.show_info)
                i[1].onClicked.connect(list_zone.select)
                i[1].onClickedCtrl.connect(list_zone.select_ctrl)
                i[1].onClickedShift.connect(list_zone.select_shift)
                i[1].onDblClicked.connect(self.open_file)
                i[1].onDblClickedCtrl.connect(self.open_folder)
                i[1].onDblClickedCtrl.connect(list_zone.select)
                i[1].onDblClicked[int,str].connect(self.click_move)
        except:
            traceback.print_exc()
    
    def get_file_path(self, idx, list_zone):
        try:
            rst = self.db.execute(
                'select path from {tbl} where isbn={isbn} limit 1'\
                .format(tbl=list_zone.name, isbn=list_zone.info_list[idx][1])
            )
            for i in rst:
                return i[0]
        except:
            traceback.print_exc()
        
    def open_file(self):
        try:
            list_zone = self.sender().parent()
            idx = list_zone.basic_select(True)
            self.book_file.open_file(list_zone.info_list[idx][0])
        except:
            traceback.print_exc()

    def open_folder(self):
        try:
            list_zone = self.sender().parent()
            idx = list_zone.basic_select(True)
            path = list_zone.info_list[idx][0]
            self.book_file.open_file(os.path.dirname(path))
        except:
            traceback.print_exc()
            
    def show_info(self, idx):
        list_zone = self.sender().parent()
        try:
            flds = self.get_flds(list_zone.name)
            values = self.db.select(
                'select {flds} from {tbl} left join book '\
                'on {tbl}.isbn = book.isbn '\
                'where {tbl}.path = "{path}" limit 1' \
                .format(flds=','.join(flds),
                        tbl=list_zone.name,
                        path=list_zone.info_list[idx][1])
            )
            for i in values:
                self.edit.widget.print_text(zip(flds, i))
                for i2 in enumerate(i):
                    edit = self.edit_zone.widget_dict[flds[i2[0]]]
                    edit.setText(str(i2[1]))
                    edit.setCursorPosition(0)
            if list_zone.info_list[idx][1]:
                stmt = self.tag.item_to_tag(list_zone.info_list[idx][1])
                tags = [i[0] for i in self.db.select(stmt)]
                self.edit_zone.widget_dict['tag'].setText(';'.join(tags))
                self.edit_zone.widget_dict['tag'].setCursorPosition(0)
        except:
            traceback.print_exc()


if __name__=='__main__':
    bf = BookFms()
