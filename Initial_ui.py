# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Initial_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(411, 151)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(70, 80, 261, 41))
        font = QtGui.QFont()
        font.setFamily("猫啃珠圆体")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(110, 120, 181, 16))
        font = QtGui.QFont()
        font.setFamily("猫啃珠圆体")
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setGeometry(QtCore.QRect(20, 30, 361, 36))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.btn_international = QtWidgets.QPushButton(self.splitter)
        font = QtGui.QFont()
        font.setFamily("猫啃珠圆体")
        font.setPointSize(16)
        self.btn_international.setFont(font)
        self.btn_international.setObjectName("btn_international")
        self.btn_domestic = QtWidgets.QPushButton(self.splitter)
        font = QtGui.QFont()
        font.setFamily("猫啃珠圆体")
        font.setPointSize(16)
        self.btn_domestic.setFont(font)
        self.btn_domestic.setObjectName("btn_domestic")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "一键毕业3.0"))
        self.label.setText(_translate("Form", "六非博科研服务团队出品"))
        self.label_2.setText(_translate("Form", "关注微信公众号：六非博"))
        self.btn_international.setText(_translate("Form", "官方Api"))
        self.btn_domestic.setText(_translate("Form", "中转Api"))
