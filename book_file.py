# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 15:04:53 2017

@author: Alfred
"""
import os
import traceback



from fms.local_file import LocalFile
from utils.db_connector import DBconnector, DB

INFO = {
    'path': r'C:\Users\Alfred\Desktop\1',
}


class BookFile(LocalFile):
    """
    1
    """
    
    def __init__(self):
        super(BookFile,self).__init__()
        self.db = DBconnector(DB['book'])
        
    @staticmethod
    def create_table():
        stmt = \
            'create table file (' \
                'path varchar(128) primary key,'\
                'ctime date,'\
                'size real,'\
                'isbn varchar(13)'\
            ')'
        #db.execute(stmt)
        return stmt
        
    def add_isbn(self, path):
        for i in self.scan(path):
            if i['path'][-4:] == '.pdf':
                i['isbn'] = self.convert(self.get_isbn(i['path']))
                yield i

    @staticmethod
    def get_isbn(file_path):
        import PyPDF2
        if file_path.split()[-1][:5] == 'isbn_':
            isbn = file_path.split()[-1][5:].split('.')[0].strip('isbn')
            return isbn
        file_object=open(file_path,'rb')
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
            #traceback.print_exc()
        return ''

    def book_rename(self, dirname=None):
        for i in self.db.execute(
                'select A.path, A.isbn, B.title from file as A '\
                    'join book as B on A.isbn=B.isbn '\
                    'where A.isbn!="" and title!=""'
                ):
            src, isbn, title = i
            title = '_'.join([i.replace(':','') for i in title.split()])
            dst = '{title} isbn_{isbn}.pdf'.format(title=title, isbn=isbn)
            if dirname:
                dst = os.path.join(dirname, dst)
            else:
                dst = os.path.join(os.path.dirname(src), dst)
            if os.path.isfile(src) and not os.path.isfile(dst):
                try:
                    os.rename(src, dst)
                    yield {'src': src, 'dst': dst}
                except:
                    traceback.print_exc()
            else:
                print(src)
                print(dst)
    
    def book_move(self, stmt, dirname):
        for i in self.db.execute(stmt):
            src = i[0]
            dst = os.path.join(dirname, os.path.basename(src))
            if os.path.isfile(src) and not os.path.isfile(dst):
                os.rename(src, dst)
                yield {'src': src, 'dst': dst}
            else:
                print(src, dst)
                
    def book_rename_md5(self):
        for i in self.db.execute(
                'select path, md5 from file'
                ):
            src, md5 = i
            dst = os.path.join(os.path.dirname(src),
                               md5 + ' ' + os.path.basename(src))
            if os.path.isfile(src) and not os.path.isfile(dst):
                try:
                    os.rename(src, dst)
                    yield {'src': src, 'dst': dst}
                except:
                    traceback.print_exc()
            else:
                print(src, dst)
                
    def book_rename_isbn(self):
        for i in self.db.execute(
                'select path, isbn from file'
                ):
            src, isbn = i
            name, ext = os.path.splitext(os.path.basename(src))
            dst = os.path.join(
                os.path.dirname(src),
                '{name} isbn_{isbn}{ext}'.format(name=name, isbn=isbn, ext=ext)
            )
            if os.path.isfile(src) and not os.path.isfile(dst):
                try:
                    os.rename(src, dst)
                    yield {'src': src, 'dst': dst}
                except:
                    traceback.print_exc()
            else:
                pass
                #print(src, dst)
    
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
    