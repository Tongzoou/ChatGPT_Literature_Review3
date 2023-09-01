# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon
from Initial_ui import Ui_Form
from Domestic_App import Domestic_App_Window
from International_App import International_App_Window

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setupUi()

        # 设置背景图片
        pixmap = QPixmap("Icon/六非博 主LOGO 2400x1800.jpg")
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(pixmap))
        self.setPalette(palette)

        # 设置窗口图标
        self.setWindowIcon(QIcon("Icon/Icon.ico"))


    def setupUi(self):
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.btn_international = self.ui.btn_international
        self.btn_international.clicked.connect(self.show_international_version)
        self.btn_domestic = self.ui.btn_domestic
        self.btn_domestic.clicked.connect(self.show_domestic_version)

    def show_international_version(self):
        self.international_app_window = International_App_Window()
        self.international_app_window.show()
        self.close()

    def show_domestic_version(self):
        self.domestic_app_window = Domestic_App_Window()
        self.domestic_app_window.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
