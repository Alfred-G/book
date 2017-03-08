# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 15:04:53 2017

@author: Alfred
"""
import threading
import traceback


from fms.local_file import LocalFile
from utils.functions import get_md5
from utils.db_connector import DBcon
from book.book_constants import DB

INFO = {
    'path': r'C:\Users\Alfred\Desktop\1',
}


class BookFile(LocalFile):
    """
    1
    """

    def __init__(self):
        super(BookFile,self).__init__()
        self.db = DBcon(DB['book'])

    @staticmethod
    def create_table():
        stmt = \
            'create table file (' \
                'path varchar(128) primary key,'\
                'ctime date,'\
                'size real,'\
                'isbn varchar(13)'\
            ')'
        # db.execute(stmt)
        return stmt
        
    def add_isbn(self, path):
        try:
            for i in self.scan(path):
                if i['path'][-4:] == '.pdf':
                    i = FileIO(i)
                    i.start()
                    yield i.result
        except:
            traceback.print_exc()

class FileIO(threading.Thread):
    def __init__(self, result):
        super(FileIO, self).__init__()
        self.result = result
        self.setDaemon(True)

    def run(self):
        fobj = open(self.result['path'], 'rb')
        self.result['md5'] = get_md5(fobj.read())
        if self.result['path'].split()[-1][:5] == 'isbn_':
            isbn = self.result['path'].split()[-1][5:]\
                .split('.')[0].strip('isbn')
        else:
            isbn = self.get_isbn(fobj)
        fobj.close()
        
        self.result['isbn'] = self.convert(isbn)
        self.result['flag'] = 1

    @staticmethod
    def get_isbn(file_object):
        import PyPDF2
        try:
            reader=PyPDF2.PdfFileReader(file_object)
            for i in range(min(10,reader.numPages)):
                page=reader.getPage(i)
                text=page.extractText()
                start=text.find('ISBN-13')
                if start!=-1:
                    text=text[start+7:]
                    for i in [':','-',' ']:
                        text=text.replace(i,'')
                    file_object.close()
                    return text[:13]
                            
                start=text.find('ISBN')
                if start!=-1:
                    text=text[start+4:]
                    for i in [':','-',' ']:
                        text=text.replace(i,'')
                    file_object.close()
                    if text[:13].isdigit():
                        return text[:13]
                    else:
                        return text[:10]
        except:
            file_object.close()
            # traceback.print_exc()
        return ''

    @staticmethod
    def convert(isbn):
        for i in ['-',' ']:
            isbn = isbn.replace(i, '')
        if isbn.isdigit():
            if len(isbn) == 13:
                return isbn
            elif len(isbn) == 10:
                isbn = '978' + isbn[:-1]
                last = 0
                for i in enumerate(isbn):
                    if i[0]%2 ==0:
                        last+=int(i[1])
                    else:
                        last+=3*int(i[1])
                return isbn+str((10-last)%10)
        return ''
