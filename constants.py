# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 20:53:28 2017

@author: Alfred
"""

DB={
    'path':'d:/Python/fms/book/book.db',
    'tbs':{
        'f':(['path', 'isbn', 'size', 'ctime'], 'path'),
        'b':(['isbn', 'title', 'isbn_10', 'isbn_13', 'authors', 'edition', 
              'publisher', 'link', 'other_info'], 'isbn'),
    },
}
DB = {
    'book': {
        'type': 'sqlite',
        'connection': {'database': 'D:/Python/fms/book/book.db'},
        'tbls': {
            'file': (['path', 'ctime', 'size', 'isbn', 'md5'], 'path'),
            'book': (['isbn', 'title', 'isbn_10', 'isbn_13', 'authors',
                      'edition', 'publisher', 'link', 'other_info'], 'isbn'),
        },
    },
}