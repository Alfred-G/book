# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 13:17:55 2017

@author: Alfred
"""
import os
import traceback

from book_file import BookFile
from book_spider import BookSpider
from utils.db_connector import DBconnector
from book_constants import DB


class BookFunc():
    
    def __init__(self):
        self.db=DBconnector(DB['book'])

    
    def get_books(self, data, parse):
        """
        1
        """

        spider=BookSpider()
        for i in data:
            yield getattr(spider, parse)(i[0])

    def standard_rename(self):
        """
        1
        """

        stmt = 'select A.path, A.isbn, B.title from file as A '\
            'join book as B on A.isbn=B.isbn '\
            'where A.isbn!="" and title!=""'

        for i in self.db.execute(stmt):
            src, isbn, title = i
            title = '_'.join([i.replace(':','') for i in title.split()])
            dst = '{title} isbn_{isbn}.pdf'.format(title=title, isbn=isbn)
            yield {'src': src, 'dst': dst}

    def rename(self, data):
        self.db.update(self.rename_list(self.standard_name))

    def rename_list(self, data):
        for i in data:
            if self.move(i):
                yield i

    @staticmethod
    def move_file(src, dst):
        if os.path.isfile(src) and not os.path.isfile(dst):
            try:
                os.rename(src, dst)
                return True
            except:
                traceback.print_exc()
        else:
            print(src)
            print(dst)
        return False
