# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 20:53:28 2017

@author: Alfred
"""
UNCLEAN_PATH = r'C:\Users\Alfred\Desktop\book'

CLEAN_PATH = r'C:\Users\Alfred\Desktop\clean'

REMOVE_PATH = r'C:\Users\Alfred\Desktop\remove'

DB = {
    'book': {
        'type': 'sqlite',
        'connection': {'database': 'C:/Users/Alfred/Documents/Python/My/book/book.db'},#'D:/Python/book/book.db'},
        'tbls': {
            'dirty': (
                [
                    ('path', 'varchar(256)'), 
                    ('ctime', 'date'), 
                    ('size', 'real'), 
                    ('isbn', 'varchar(13)'),
                    ('md5', 'varchar(32)'),
                    ('flag', 'int(1)')
                ],
                'path'
            ),
            'file': (
                [
                    ('path', 'varchar(256)'), 
                    ('ctime', 'date'), 
                    ('size', 'real'), 
                    ('isbn', 'varchar(13)'),
                    ('md5', 'varchar(32)'),
                    ('flag', 'int(1)')
                ],
                'path'
            ),
            'book': (
                [
                    ('isbn', 'varchar(13)'),
                    ('title', 'varchar(128)'),
                    ('isbn_10', 'varchar(10)'),
                    ('isbn_13', 'varchar(13)'),
                    ('authors', 'varchar(64)'),
                    ('edition', 'varchar(64)'),
                    ('publisher', 'varchar(32)'),
                    ('link', 'varchar(128)'),
                    ('other_info', 'text'),
                ],
                'isbn'
            ),
            'tag': (
                [('id', 'int(11)'), ('name', 'varchar(16)')],
                'id'
            ),
            'book_tag': (
                [
                    ('id', 'int(11)'),
                    ('book_id', 'varchar(13)'),
                    ('tag_id', 'int(11)')
                ],
                'id'
            ),
            'tag_parent': (
                [
                    ('id', 'int(11)'),
                    ('tag_id', 'int(11)'),
                    ('parent_id', 'int(11)')
                ],
                'id'
            ),
        },
    },
}