# -*- coding: utf-8 -*-
import os
import hashlib
import sys
import pickle
import uuid
from PyQt5.QtWidgets import (QApplication, QWidget, QMessageBox, QVBoxLayout, QLabel, QPushButton,
                             QTextEdit, QDialog, QHBoxLayout)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon, QFont
from PyQt5.QtCore import Qt
from Initial_ui import Ui_Form
from Domestic_App import Domestic_App_Window
from International_App import International_App_Window

def get_mac_address():
    """获取MAC地址"""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                    for elements in range(0,8*6,8)][::-1])
    return mac

def get_machine_code():
    return get_mac_address()

class ActivationDialog(QDialog):
    def __init__(self, machine_code):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.machine_code = machine_code
        self.setWindowTitle('一键毕业软件激活')
        self.setWindowIcon(QIcon(r"./Icon/Icon.png"))
        layout = QVBoxLayout()

        # 显示机器码
        machine_code_layout = QHBoxLayout()
        self.machine_code_label = QLabel(f"您的机器码是：{self.machine_code}")
        self.copy_button = QPushButton("复制")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        machine_code_layout.addWidget(self.machine_code_label)
        machine_code_layout.addWidget(self.copy_button)
        layout.addLayout(machine_code_layout)

        # 输入激活码
        self.activation_input = QTextEdit()
        layout.addWidget(self.activation_input)

        # 验证按钮
        self.verify_button = QPushButton("验证")
        self.verify_button.clicked.connect(self.verify_activation)
        layout.addWidget(self.verify_button)

        # 免责声明
        text_res = '''
        <center><h2><b>【软件免责声明】</b></h2></center>

        在您决定使用此软件之前，请严格遵守国家互联网信息办公室 中华人民共和国国家发展和改革委员会 中华人民共和国教育部 中华人民共和国科学技术部 中华人民共和国工业和信息化部 中华人民共和国公安部 国家广播电视总局令第15号《生成式人工智能服务管理暂行办法》及阅读以下免责声明。

         <center><h3><b>1.版权声明</b></h3></center>

        本软件仅作学习交流使用，相关源码和图标在转发给用户的同时进行了非商业性共享。用户在使用或二次传播此软件时，需确保自己已获得PyQt和其他相关图标的适当使用许可，尤其在进行商业活动时,如发生任何侵权行为，软件开发者不承担任何责任。软件使用者不得二次开发、打包、出售本软件原创代码和相关功能代码。
         <center><h3><b>2.免责声明</b></h3></center>

        本软件按“原样”提供，不提供任何明示或暗示的保证，包括但不限于对适销性、特定用途的适用性和非侵权的明示或暗示保证。在任何情况下，软件作者或版权持有人不对任何形式的损害负责，包括但不限于直接、间接、偶然、特殊、示范或后果性的损害，即使在已被告知此类损害的可能性下。

         <center><h3><b>3.使用风险</b></h3></center>

        用户明确同意其使用软件的风险完全由其自己承担。软件开发者不向用户提供任何非法的网络服务与连接活动，同时不对此软件的适用性、安全性或功能提供任何保证。用户需自行判断并承担所有使用风险。软件开发者不保证软件功能的长期有效性。

         <center><h3><b>4.第三方内容</b></h3></center>

        本软件及其相关视频教程可能包含第三方内容或链接。这些内容的准确性、安全性、合法性、相关性、版权等均由相关第三方负责。软件作者对此不承担任何责任。用户应遵循第三方的使用条款和条件，以及中华人民共和国相关法律法规。

         <center><h3><b>5.用户数据与隐私</b></h3></center>

        本软件尊重并保护用户的隐私，不会从用户电脑采集和获取任何信息及数据。除非获得用户明确同意或法律明文规定，我们不会向第三方提供、公开或分享用户的任何个人信息。

         <center><h3><b>6.适用法律</b></h3></center>

        此免责声明及与之相关的任何纠纷均应根据中华人民共和国的法律进行解释和裁决。

        <b>通过下载、安装或使用此软件，您表示您已经阅读、理解并同意接受本免责声明中的所有条款。如果您不同意本免责声明的任何部分，请不要下载、安装或使用此软件。</b>
        '''
        text_font = QFont()
        text_font.setPointSize(12)
        self.disclaimer_box = QTextEdit(text_res)
        self.disclaimer_box.setFont(text_font)
        self.disclaimer_box.setReadOnly(True)  # 设置为只读
        layout.addWidget(self.disclaimer_box)

        # 微信公众号提示
        wechat_label = QLabel('在阅读并同意免责声明后，将机器码复制给"六非博"客服')
        font = QFont()
        font.setFamily("猫啃珠圆体")
        font.setBold(True)
        font.setPointSize(16)
        wechat_label.setFont(font)
        wechat_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(wechat_label)
        self.setLayout(layout)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.machine_code)

    def verify_activation(self):
        mac_address = get_machine_code()
        combined_code = mac_address
        activation_code = self.activation_input.toPlainText()
        correct_activation_code = hashlib.sha256(combined_code.encode()).hexdigest()[:10]

        if activation_code == correct_activation_code:
            with open('activation.dat', 'wb') as f:
                pickle.dump(activation_code, f)
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "激活码不正确，请重试！")

class Window(QWidget):
    def __init__(self):
        super().__init__()

        # 检查激活
        if not self.check_activation():
            sys.exit()
        self.setupUi()

        # 设置背景图片
        pixmap = QPixmap(r"./Icon/六非博 主LOGO 2400x1800.jpg")
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(pixmap))
        self.setPalette(palette)

        # 设置窗口图标
        self.setWindowIcon(QIcon(r"./Icon/Icon.ico"))

    def setupUi(self):
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.btn_international = self.ui.btn_international
        self.btn_international.clicked.connect(self.show_international_version)
        self.btn_domestic = self.ui.btn_domestic
        self.btn_domestic.clicked.connect(self.show_domestic_version)

    def show_international_version(self):
        disclaimer_dialog = DisclaimerDialog()
        result = disclaimer_dialog.exec_()
        if result == QDialog.Accepted:
            self.international_app_window = International_App_Window()
            self.international_app_window.show()
            self.close()

    def show_domestic_version(self):
        disclaimer_dialog = DisclaimerDialog()
        result = disclaimer_dialog.exec_()
        if result == QDialog.Accepted:
            self.domestic_app_window = Domestic_App_Window()
            self.domestic_app_window.show()
            self.close()

    def check_activation(self):
        """检查是否已经激活。"""
        if os.path.exists('activation.dat'):
            with open('activation.dat', 'rb') as f:
                saved_activation_code = pickle.load(f)

            mac_address = get_machine_code()
            combined_code = mac_address + "tongzoulovemuxuan"
            correct_activation_code = hashlib.sha256(combined_code.encode()).hexdigest()[:10]

            if saved_activation_code == correct_activation_code:
                return True
            else:
                os.remove('activation.dat')
                QMessageBox.warning(self, "错误", "激活文件不匹配或已损坏！")
                return False

        activation_dialog = ActivationDialog(get_machine_code())
        result = activation_dialog.exec_()

        return result == QDialog.Accepted


class DisclaimerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('免责声明')
        self.resize(500, 400)

        # Layouts
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Disclaimer text
        self.text_edit = QTextEdit()
        self.text_edit.setHtml(text_res)
        self.text_edit.setReadOnly(True)

        # Buttons
        self.agree_button = QPushButton('同意')
        self.disagree_button = QPushButton('不同意')

        # Connect buttons
        self.agree_button.clicked.connect(self.accept)
        self.disagree_button.clicked.connect(self.reject)

        # Add widgets to layouts
        button_layout.addWidget(self.agree_button)
        button_layout.addWidget(self.disagree_button)

        main_layout.addWidget(self.text_edit)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
text_res='''
<center><h2><b>【软件免责声明】</b></h2></center>

在您决定使用此软件之前，请严格遵守国家互联网信息办公室 中华人民共和国国家发展和改革委员会 中华人民共和国教育部 中华人民共和国科学技术部 中华人民共和国工业和信息化部 中华人民共和国公安部 国家广播电视总局令第15号《生成式人工智能服务管理暂行办法》及阅读以下免责声明。

 <center><h3><b>1.版权声明</b></h3></center>

本软件仅作学习交流使用，相关源码和图标在转发给用户的同时进行了非商业性共享。用户在使用或二次传播此软件时，需确保自己已获得PyQt和其他相关图标的适当使用许可，尤其在进行商业活动时,如发生任何侵权行为，软件开发者不承担任何责任。软件使用者不得二次开发、打包、出售本软件原创代码和相关功能代码。
 <center><h3><b>2.免责声明</b></h3></center>

本软件按“原样”提供，不提供任何明示或暗示的保证，包括但不限于对适销性、特定用途的适用性和非侵权的明示或暗示保证。在任何情况下，软件作者或版权持有人不对任何形式的损害负责，包括但不限于直接、间接、偶然、特殊、示范或后果性的损害，即使在已被告知此类损害的可能性下。

 <center><h3><b>3.使用风险</b></h3></center>

用户明确同意其使用软件的风险完全由其自己承担。软件开发者不向用户提供任何非法的网络服务与连接活动，同时不对此软件的适用性、安全性或功能提供任何保证。用户需自行判断并承担所有使用风险。软件开发者不保证软件功能的长期有效性。

 <center><h3><b>4.第三方内容</b></h3></center>

本软件及其相关视频教程可能包含第三方内容或链接。这些内容的准确性、安全性、合法性、相关性、版权等均由相关第三方负责。软件作者对此不承担任何责任。用户应遵循第三方的使用条款和条件，以及中华人民共和国相关法律法规。

 <center><h3><b>5.用户数据与隐私</b></h3></center>

本软件尊重并保护用户的隐私，不会从用户电脑采集和获取任何信息及数据。除非获得用户明确同意或法律明文规定，我们不会向第三方提供、公开或分享用户的任何个人信息。

 <center><h3><b>6.适用法律</b></h3></center>

此免责声明及与之相关的任何纠纷均应根据中华人民共和国的法律进行解释和裁决。

<b>通过下载、安装或使用此软件，您表示您已经阅读、理解并同意接受本免责声明中的所有条款。如果您不同意本免责声明的任何部分，请不要下载、安装或使用此软件。</b>
'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
