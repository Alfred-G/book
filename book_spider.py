# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 10:59:32 2017

@author: Alfred
"""
from datetime import datetime as dt

from utils.spider import Spider
from utils.db_connector import DB, DBconnector

"""
'create table book (
    isbn varchar(13) primary key,
    title varchar(128),
    isbn_10 varchar(10),
    isbn_13 varchar(13),
    authors varchar(64),
    edition varchar(32),
    publisher varchar(64),
    link varchar(64),
    other_info text
)'
"""
KEYS={
    'Book Title':'title',
    'BookSubtitle':'subtitle',
    'Editors':'authors',
    'SeriesTitle':'series_title',
    'SeriesVolume':'series_volume',
    'Copyright':'copy_right',
    'Publisher':'publisher',
    'Copyright Holder':'copyright_holder',
    'eBook ISBN':'ebook_isbn',
    'DOI':'doi',
    'Hardcover ISBN':'hardcover_isbn',
    'Softcover ISBN':'softcover_isbn',
    'SeriesISSN':'series_issn',
    'EditionNumber':'edition_number',
    'NumberofPages':'page_num',
    'NumberofIllustrationsandTables':'illu_table_num',
    'Topics':'topics',
    'Authors':'authors',
}


class BookSpider():

    def __init__(self):
        header = {
            #'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
            #'Accept-Language':'en-us',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64;'\
                ' Trident/7.0; Touch; rv:11.0) like Gecko',
            #'Accept-Encoding': 'gzip, deflate',
            #'Connection': 'Keep-Alive',
            #'Pragma': 'no-cache',
        }
        self.spider = Spider(header=header, timeout = 15)
        self.db = DBconnector(DB['book'])
        
    def isbndb(self, isbn):
        url = 'https://isbndb.com/search/all?query=%s'
        book = {'other_info': '{}'}
        response = self.spider.request(url % isbn)
        if not response:
            return
        
        info = self.extract(response.xpath('//div[@class="bookSnippetBasic"]'))
        if not info:
            return
        
        book['isbn'] = isbn
        book['title'] = self.extract(info.xpath(
            './/h1/text()')
        ).replace('\n','').replace('\r','').strip('\t')
        book['isbn_10'], book['isbn_13'] = info.xpath(
                './/span[@itemprop="isbn"]/text()'
        )
        book['authors'] = self.extract(info.xpath(
                './/a[@itemprop="author"]/text()'
        ))
        book['edition'] = self.extract(info.xpath(
            './/span[@itemprop="bookEdition"]/text()'
        ))
        book['publisher'] = self.extract(info.xpath(
                './/a[@itemprop="publisher"]/text()'
        ))
        book['link'] = response.url
        
        image_urls = response.xpath('//div[@id="image"]/a/img/@src')
        print(image_urls)
        self.spider.get_imgs('d:/Python/fms/book/pic', image_urls, 
                             prefix='isbndb')
        
        return book

    def springer(self, isbn):
        response = self.spider.request(
            'http://www.springer.com/cn/book/%s' % isbn
        )
        if not response:
            return
        
        book = {'isbn': isbn, 'title': '', 'isbn_10': '', 'isbn_13': '',
                'authors': '', 'edition': '', 'publisher': '', 'link': '',
                'other_info': {}
        }
        for i in range(1, 4):
            for i2 in range(1, 10):
                key = response.xpath(
                    '//div[@class="product-bibliographic"]/dl/dd/'\
                    'div/div/dl[%s]/dt[%s]/text()' % (i, i2)
                )
                if key:
                    key = key[0]
                else:
                    continue
                info=response.xpath(
                    '//div[@class="product-bibliographic"]/dl/dd/'\
                    'div/div/dl[%s]/dd[%s]/text()' % (i, i2)
                )
                if key == 'Editors' or key == 'Authors':
                    info=';'.join(response.xpath(
                        '//div[@class="product-bibliographic"]/dl/'\
                        'dd/div/div/dl[%s]/dd[%s]/ul//span/text()' % (i, i2)
                    ))
                elif key == 'Publisher':
                    info=response.xpath(
                        '//div[@class="product-bibliographic"]/dl/'\
                        'dd/div/div/dl[%s]/dd[%s]/span/text()' % (i, i2)
                    )[0]
                elif key == 'Topics':
                    info=';'.join(response.xpath(
                        '//div[@class="product-bibliographic"]/dl/'\
                        'dd/div/div/dl[%s]/dd[%s]/ul/li/a/text()' % (i, i2)
                    ))
                elif info:
                    info = info[0]
                if key in KEYS.keys():
                    book['other_info'][KEYS[key]] = \
                        str(info).strip('\n').strip(' ')
                book['other_info']['link'] = response.url
                book['other_info']['create_date'] = \
                    dt.today().strftime('%Y-%m-%d')
                
            image_urls=response.xpath(
                '//meta[@property="og:image:secure_url"]/@content'
            )
            self.spider.get_imgs('d:/Python/fms/book/pic', image_urls,
                                 prefix='springer')
            
        book['other_info'] = str(book['other_info'])
        return book
    
    def get_books(self, parse):
        for i in self.db.execute(
                'select A.isbn from file as A '\
                    'left join book as B on A.isbn=B.isbn '\
                    'where A.isbn!="" and B.isbn is null'
                ):
            yield getattr(self, parse)(i[0])
    
    @staticmethod
    def extract(data, idx=0):
        if data and len(data) > idx:
            return data[idx]
        return ''