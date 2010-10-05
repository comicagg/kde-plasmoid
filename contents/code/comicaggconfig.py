# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from configform import Ui_Form

class ComicaggConfig(QWidget, Ui_Form):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setupUi(self)
        self.parent = parent
