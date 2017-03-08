# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 09:27:46 2017

@author: Alfred
"""

from PyQt5.QtWidgets import QGridLayout,QWidget,QLabel
a=QWidget()
b=QGridLayout()
a.setLayout(b)
c=QLabel('1')
d=QLabel('2')
b.addWidget(c)
b.addWidget(d)
a.show()
b.removeWidget(c)
a.update()