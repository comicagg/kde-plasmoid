# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/configform.ui'
#
# Created: Tue May  4 17:02:03 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(409, 148)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.formLayout = QtGui.QFormLayout(Form)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.user = QtGui.QLineEdit(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.user.sizePolicy().hasHeightForWidth())
        self.user.setSizePolicy(sizePolicy)
        self.user.setMinimumSize(QtCore.QSize(170, 0))
        self.user.setMaximumSize(QtCore.QSize(170, 16777215))
        self.user.setObjectName("user")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.user)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setStyleSheet("font-weight:bold;")
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "User", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Account", None, QtGui.QApplication.UnicodeUTF8))

