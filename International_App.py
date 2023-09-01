# -*- coding:utf-8 -*-

# Author:六非博
# 关注微信公众号：六非博
# CreatTime:2023/7/2
# FilesNmae:App
"""
官方key
"""

import os
import sys
import subprocess
import re
import time

import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QTextOption
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QDialog, QVBoxLayout, QPushButton, QLabel, \
    QListWidget, QHBoxLayout, QAbstractItemView, QDialogButtonBox, QTextEdit
from International_App_Window_ui import Ui_ChatGPT
from ChatGPT_conversation_3_international import ChatGPT_conversation_3
from ChatGPT_conversation_4_international import ChatGPT_conversation_4
from Token_check import TokenCounter  # 引入token计算
import datetime
from docx import Document
class International_App_Window(QWidget):
    def __init__(self):
        super().__init__()
        # 设置图标
        self.setWindowIcon(QIcon(r"./Icon/Icon.png"))
        # 设置窗口的大小为特定值，并阻止用户更改它
        self.setFixedSize(916, 456)

        self.setupUi()
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        # 用来存储数据的字典
        self.document_dict = {}
        # 用来存储GPT的配置信息
        self.gpt_dict = {}
        # 用来存储对话信息
        self.PROMPT_LIST = []
        # 文献综述模板
        self.PROMPT_model = """现在你是一名正在写学术论文的大学教授，你需要从5条文献数据的摘要中提取每篇文献的研究方法、内容、意义、价值等重要信息，并将每一篇文章摘要的研究对象、方法、内容以及价值等信息概括成逻辑连贯、简洁全面的一句话，例如张涛和李均超(2023)基于2010～2020年中国城市层面数据，研究了网络基础设施对城市包容性绿色增长的影响效应及内在机制，并进一步考察了网络基础设施的区域协调效应。除了5句话之外，禁止输出'以上是对这五篇文献的摘要信息的概括'、'综上所述'、'摘要概括'等无关内容,每句话都要换行后再输出下一句。下面是需要概括的5条文献数据："""
        self.Summary_PROMPT = """现在你是一名正在写学术论文的大学教授，你需要从下面的文献数据中从3-5个角度去梳理，分析和评价当前的研究现状。首先通过一句非常简短精炼的话对现有文献成果进行概括，然后再对已有文献成果进行分类，并给出详细的依据理由和对应的文献数据（作者+年份+观点）。最后总结现有文献的不足，给出当前领域可能的新研究方向，并说明理由。下面我将传给你具体的文献数据，请你进行总结。"""
        # 一键摘要模板
        self.Abstract_PROMPT = """你是一名大学教授，你需要对下面文字内容进行总结后，请分别从（1）研究背景、（2）研究方法，（3）主要结论，（4）研究价值四个方面总结并撰写一个中英文摘要。"""
        self.abstract_file = []

        # 这个用于存储多个prompt
        self.PROMPT_model_much = []
        # 判断GPT是否回答
        self.check = "running"

        # 这个是记录文件的路径的，以便于实时更新这个表格
        self.update_excel_filename = ""

    def setupUi(self):  # 调用ui类,并获取每一个元素
        self.ui = Ui_ChatGPT()
        self.ui.setupUi(self)
        # 获取界面所有的白框
        self.API_KEY = self.ui.API_KEY  # APIkey

        self.input_informa = self.ui.input_informa  # 输入框

        self.Chat_response = self.ui.Chat_response  # gpt回复框

        self.Token_use = self.ui.Token_use  # token使用框
        self.Token_use.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        self.verison_choose_box = self.ui.verison_choose_box  # 版本多选框
        self.request_port = self.ui.request_port  # 端口输入框

        # 获取所有按钮
        self.data_clean_btn = self.ui.data_clean_btn  # 数据处理按钮
        self.data_clean_btn.setIcon(
            QIcon(r"./Icon/data.png"))
        self.data_clean_btn.clicked.connect(self.show_data_process_dialog)
        self.Review_data_botton = self.ui.Review_data_botton  # 一键综述
        self.Review_data_botton.setIcon(
            QIcon(r"./Icon/robot.png"))
        self.Review_data_botton.clicked.connect(self.Gpt_connect_review)

        self.sum_review_btn = self.ui.sum_review_btn  # 一键总结
        self.sum_review_btn.setIcon(
            QIcon(r"./Icon/sum.png"))
        self.sum_review_btn.clicked.connect(self.Gpt_connect_sum)

        self.Submit_to_Gpt = self.ui.Submit_to_Gpt  # 提交给GPT
        self.Submit_to_Gpt.setIcon(
            QIcon(r"./Icon/send.png"))
        self.Submit_to_Gpt.clicked.connect(self.Gpt_connect)

        self.Save_resonse = self.ui.Save_resonse  # 保存结果
        self.Save_resonse.setIcon(
            QIcon(r"./Icon/save.png"))
        self.Save_resonse.clicked.connect(self.Sava_response_func)

        self.clear_botton = self.ui.Clear_botton  # 清除结果
        self.clear_botton.setIcon(
            QIcon(r"./Icon/clear.png"))
        self.clear_botton.clicked.connect(self.Clear_token)

        self.open_floder = self.ui.open_floder  # 打开文件夹
        self.open_floder.clicked.connect(self.open_project_folder)
        self.open_floder.setIcon(
            QIcon(r"./Icon/floder.png"))

        ##############################2023年8月8日功能更新###########################
        self.abstract_btn = self.ui.abstract_btn  # 一键摘要功能
        self.abstract_btn.setIcon(
            QIcon(r"./Icon/abstract.png"))
        self.abstract_btn.clicked.connect(self.handle_abstract_btn_clicked)

    # 显示数据处理的对话框
    def show_data_process_dialog(self):
        self.dialog_dataprocess = DataprocessDialog(self)
        self.dialog_dataprocess.show()

    #####################工具类槽函数编写#########################
    def Sava_response_func(self):
        savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)

        # 获取当前.exe文件的目录
        exe_folder_path = os.path.dirname(sys.executable)

        # 检查是否存在 "对话结果" 文件夹，如果不存在则创建它
        directory = os.path.join(exe_folder_path, "对话结果")
        if not os.path.exists(directory):
            os.makedirs(directory)

        if self.Chat_response.toPlainText() == "":
            savedataalrt("请对话后再保存！")
        else:
            # 将文件保存到 "对话结果" 文件夹中
            file_path = os.path.join(directory, '聊天记录.txt')
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(self.Chat_response.toPlainText())
            savedataalrt("保存成功，请返回文件夹查看！")

    # 打开项目文件夹
    def open_project_folder(self):
        import sys
        # 获取当前.exe文件的目录
        folder_path = os.path.dirname(sys.executable)
        # 根据操作系统打开文件夹
        if os.name == 'nt':  # Windows
            subprocess.Popen(['explorer', folder_path])
        elif os.name == 'posix':  # macOS
            subprocess.Popen(['open', folder_path])
        else:  # linux variants (though it's rare to have an .exe here)
            subprocess.Popen(['xdg-open', folder_path])

    # 这个槽函数用来清空self.PROMPT_LIST
    def Clear_token(self):
        self.PROMPT_LIST = []
        self.input_informa.setText("你好吗？")
        self.Chat_response.clear()
        self.Token_use.setText("当前Token已清空，对话将重新开始")

    def ZN_data_choose(self):
        try:
            # 弹窗警告
            savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)
            # 选择自我介绍文件，返回一个元组，第一个元素是txt文件路径
            data_choose_tuple = QFileDialog.getOpenFileName(self, "待处理数据的txt文件", self.cwd,
                                                            filter="txt文件(*.txt)")
            if data_choose_tuple[0] == "":
                pass
            else:
                dataprocessor = DataProcessor(data_choose_tuple[0])
                dataprocessor.CN_data_process()
                savedataalrt("成功！返回文件夹查看！")
        except Exception as e:
            QMessageBox.warning(self, "数据格式错误！", str(e))

    def EN_data_choose(self):
        try:
            savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)
            # 选择自我介绍文件，返回一个元组，第一个元素是txt文件路径
            data_choose_tuple = QFileDialog.getOpenFileName(self, "待处理数据的txt文件", self.cwd,
                                                            filter="Excel文件(*.xls)")
            if data_choose_tuple[0] == "":
                pass
            else:
                dataprocessor = DataProcessor(data_choose_tuple[0])
                dataprocessor.EN_data_process()
                savedataalrt("成功！返回文件夹查看！")
        except Exception as e:
            QMessageBox.warning(self, "数据格式错误！", str(e))

    ######################GPT槽函数##############################
    def Gpt_connect(self):
        try:
            savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)
            # 点击后其他按钮失效
            self.False_botton()

            # 判断版本:gpt-3.5-turbo-0613或者gpt-4-0613
            Gpt_version = self.verison_choose_box.currentText()

            # 端口信息
            if not self.request_port.text():
                savedataalrt("请输入请求端口")
                self.True_botton()
            elif self.API_KEY.text() == "":
                savedataalrt("请输入API_KEY")
                self.True_botton()
            elif self.input_informa.toPlainText() == "":
                savedataalrt("你没有输入任何信息")
                self.True_botton()
            else:
                self.gpt_dict["API_KEY"] = self.API_KEY.text()
                # 将提问框的内容转移到回复框中
                self.Chat_response.append(self.input_informa.toPlainText() + '\n')

                # 将提问框中的内容添加到PROMPT中
                self.PROMPT_LIST.append({"role": "user", "content": self.input_informa.toPlainText()})
                self.gpt_dict["PROMPT_LIST"] = self.PROMPT_LIST

                # 将提问框的内容清空
                self.input_informa.setText("你好吗？")

                # 创建一个线程来链接gpt
                self.gpt_talk = MyThread_gpt_chat(self.gpt_dict, Gpt_version, self.request_port.text())
                # 运行线程
                self.gpt_talk.start()

                # 线程运行后的动作
                self.gpt_talk.gpt_answer_signal.connect(self.gpt_answer_show)
                # 连接新的错误处理槽函数
                self.gpt_talk.gpt_error_signal.connect(self.handle_gpt_error)
                self.gpt_talk.gpt_prompt_update_signal.connect(self.Prompt_update)
                self.gpt_talk.gpt_token_consume_signal.connect(self.token_consume)
        except Exception as e:
            QMessageBox.warning(self, "网络异常！", str(e))

    #####################一键生成文献综述#######################################
    def Gpt_connect_review(self):
        try:
            savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)

            # 点击后其他按钮失效
            self.False_botton()

            # 清空Prompt,可能用户先测试了聊天功能，所以必须要先清空，避免前面使用过后数据累计
            self.PROMPT_LIST = []
            self.Chat_response.clear()

            data_choose_tuple = QFileDialog.getOpenFileName(self, "待处理数据的文献数据", self.cwd,
                                                            filter="csv文件(*.csv)")
            self.update_csv_filename = data_choose_tuple[0]

            if data_choose_tuple[0] == "":
                savedataalrt("请选择文献数据文件！")
                self.True_botton()
                return

            # 将csv文件中的数据每5个分割一次，便于gpt生成结果
            df = pd.read_csv(data_choose_tuple[0])

            # 提取"作者"、"年份"和"摘要"三列的数据
            selected_data = df[["作者", "年份", "摘要"]]

            # 每五行存储在一个子列表中，所有子列表存储在总列表中
            chunk = []
            chunks = []
            for i, row in selected_data.iterrows():
                formatted_row = "{}{}{}".format(row["作者"], row["年份"], row["摘要"])
                chunk.append(formatted_row)
                if (i + 1) % 5 == 0:  # 每5行分割一次
                    chunks.append(chunk)
                    chunk = []

            # 如果有余下的行数，添加到chunks中
            if chunk:
                chunks.append(chunk)

            # 生成n个prompt
            for chunk in chunks:
                # 将前5条数据转换成str格式
                str_lst = "".join(["{}\\n".format(sublist) for sublist in chunk])
                # 生成多个prompt的列表
                self.PROMPT_LIST.append({"role": "user", "content": self.PROMPT_model + str_lst})

            # 判断版本:gpt-3.5-turbo-0613或者gpt-4-0613
            Gpt_version = self.verison_choose_box.currentText()
            if not self.request_port.text():
                savedataalrt("请输入请求端口")
                self.True_botton()
                return
            if self.API_KEY.text() == "":
                savedataalrt("请输入API_KEY")
                self.True_botton()
                return

            self.gpt_dict["API_KEY"] = self.API_KEY.text()
            self.gpt_dict["PROMPT_LIST"] = self.PROMPT_LIST

            # 创建一个线程来链接gpt
            self.gpt_talk = MyThread_gpt_review(self.gpt_dict, Gpt_version, self.request_port.text())
            self.gpt_talk.start()
            self.gpt_talk.gpt_answer_signal.connect(self.gpt_answer_show_review)
            # 连接新的错误处理槽函数
            self.gpt_talk.gpt_error_signal.connect(self.handle_gpt_error)
            self.gpt_talk.gpt_status_signal.connect(self.gpt_status_show_requerst)
            self.gpt_talk.gpt_token_consume_signal.connect(self.token_consume)

            # 在连接新的信号之前，确保断开先前的连接
            try:
                self.gpt_talk.gpt_answer_over_signal.disconnect(self.over_check_review)
            except TypeError:  # Ignore if the signal was not connected before
                pass

            # Now, connect the signal
            self.gpt_talk.gpt_answer_over_signal.connect(self.over_check_review)

        except Exception as e:
            QMessageBox.warning(self, "网络异常！", str(e))

    #####################一键总结文献综述#######################################
    def Gpt_connect_sum(self):
        try:
            savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)

            # 点击后其他按钮失效
            self.False_botton()

            self.Chat_response.clear()
            # 判断版本: gpt-3.5-turbo-0613 或者 gpt-4-0613
            Gpt_version = self.verison_choose_box.currentText()
            if not self.request_port.text():
                savedataalrt("请输入请求端口")
                self.True_botton()
                return
            if self.API_KEY.text() == "":
                savedataalrt("请输入API_KEY")
                self.True_botton()
                return

            data_choose_tuple = QFileDialog.getOpenFileName(self, "待处理数据的txt文件", self.cwd, filter="txt文件(*.txt)")
            if data_choose_tuple[0] == "":
                savedataalrt("请选择文献数据文件！")
                self.True_botton()
                self.input_informa.setText("")
                return
            else:
                with open(data_choose_tuple[0], "r", encoding="utf-8") as file:
                    review_data = file.read().strip().replace("\n", "")
                self.PROMPT_LIST.append({"role": "user", "content": self.Summary_PROMPT + "{}".format(review_data)})
            self.gpt_dict["API_KEY"] = self.API_KEY.text()
            self.gpt_dict["PROMPT_LIST"] = self.PROMPT_LIST

            self.input_informa.setText("ChatGPT正在总结，请耐心等待！")
            # 创建一个线程来链接gpt
            self.gpt_talk = MyThread_gpt_sum(self.gpt_dict, Gpt_version, self.request_port.text())
            self.gpt_talk.start()
            self.gpt_talk.gpt_answer_signal.connect(self.gpt_answer_show)
            self.gpt_talk.gpt_error_signal.connect(self.handle_gpt_error)
            self.gpt_talk.gpt_token_consume_signal.connect(self.token_consume)
            self.gpt_talk.gpt_answer_over_signal.connect(self.over_check_sum)
        except Exception as e:
            QMessageBox.warning(self, "网络异常！", str(e))

    #####################一键摘要功能#######################################
    def handle_abstract_btn_clicked(self):
        try:
            savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)

            # 禁用所有按钮
            self.False_botton()

            # Open file dialog to let the user select a .docx file
            self.abstract_file, _ = QFileDialog.getOpenFileNames(self, "选择.docx文件", "",
                                                                 "Word Documents (*.docx);;All Files (*)")

            # Check if user cancelled the file dialog
            if not self.abstract_file:
                QMessageBox.warning(self, "提示", "请上传文件")
                self.True_botton()
                return

            # Check if user selected more than one file
            if len(self.abstract_file) > 1:
                QMessageBox.warning(self, "提示", "只能上传一个文件")
                self.True_botton()
                return

            # Process the selected file using DocxProcessor
            processor = DocxProcessor(self.abstract_file[0])
            processor.extract_titles_and_contents()

            # Check if any titles were extracted
            if not processor.get_titles():
                QMessageBox.warning(self, "提示", "该文档未创建任何标题，请创建后重新上传")
                self.True_botton()
                return

            # If titles were extracted, show the FilterDialog
            self.dialog_abstract = BtnFilterDialog(processor, self)

            result = self.dialog_abstract.exec_()
            # If user clicked "OK" in the FilterDialog
            if result != QDialog.Accepted:
                self.True_botton()
                return

            # 获取用户选择的标题和内容
            selected_data = self.dialog_abstract.get_selected_Abstract_content()
            self.input_informa.setText("ChatGPT正在生成摘要，请耐心等待！")

            # 判断版本:gpt-3.5-turbo-0613或者gpt-4-0613
            Gpt_version = self.verison_choose_box.currentText()
            if not self.request_port.text():
                savedataalrt("请输入请求端口")
                self.True_botton()
                return

            if self.API_KEY.text() == "":
                savedataalrt("请输入API_KEY")
                self.True_botton()
                return

            self.gpt_dict["API_KEY"] = self.API_KEY.text()
            self.PROMPT_LIST.append({"role": "user", "content": self.Abstract_PROMPT + "{}".format(selected_data)})
            self.gpt_dict["PROMPT_LIST"] = self.PROMPT_LIST

            # 创建一个线程来链接gpt
            self.gpt_talk = MyThread_gpt_sum(self.gpt_dict, Gpt_version, self.request_port.text())
            self.gpt_talk.start()
            self.gpt_talk.gpt_answer_signal.connect(self.gpt_answer_show)
            self.gpt_talk.gpt_token_consume_signal.connect(self.token_consume)
            self.gpt_talk.gpt_answer_over_signal.connect(self.over_check_abstract)
        except Exception as e:
            QMessageBox.warning(self, "网络异常！", str(e))

    ###########################状态检查的槽函数####################################
    #异常报错窗口
    def handle_gpt_error(self, error_msg):
        """处理GPT返回的错误"""
        QMessageBox.critical(self, "错误，正在重试，关闭本窗口即可", error_msg)
        self.True_botton()  # 恢复按钮的状态
    # 这个槽函数将一键综述的情况添加到提问框，比如说
    def gpt_status_show_requerst(self, str):
        self.input_informa.append(str + "\n")

    # 这个槽函数是接收返回消息的，如果出现错误
    def gpt_answer_show(self, answer):
        # 恢复按钮 at the end
        self.True_botton()
        self.Chat_response.append(answer + '\n')
        # 一键生成综述点击之后后面的三个再结束之前全部设置不可用
        # 清空Prompt,避免前面使用过后数据累计
        self.PROMPT_LIST = []

    def gpt_answer_show_review(self, answer):
        self.Chat_response.append(answer + "\n")

        # 清空Prompt,避免前面使用过后数据累计
        self.PROMPT_LIST = []

    # 这个槽函数用来更新对话的Prompt，以实现连续对话
    def Prompt_update(self, prompt_list_update):
        self.PROMPT_LIST = prompt_list_update

    # 这个槽函数用来输出每次的token消耗数据
    def token_consume(self, token):
        self.Token_use.setText(
            f"本次对话由 {token['model']}提供，对话共使用 ({token['usage']['total_tokens']}) Token,提问 ({token['usage']['prompt_tokens']}) Token,回答 ({token['usage']['completion_tokens']}) Token。")

    # 全部任务结束后执行检查
    def over_check_sum(self, sum_docx):
        savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)

        # 获取当前.exe文件的目录
        exe_folder_path = os.path.dirname(sys.executable)

        # 检查是否存在 "一键总结结果" 文件夹，如果不存在则创建它
        directory = os.path.join(exe_folder_path, "一键总结结果")
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 将文件保存到 "一键总结结果" 文件夹中
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        file_path_timestamped = os.path.join(directory, f'{timestamp}_一键总结.txt')
        with open(file_path_timestamped, 'w', encoding='utf-8') as f:
            f.write(sum_docx)

        savedataalrt("总结完毕，返回文件夹查看！")

    def over_check_abstract(self, sum_docx):
        savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")

        # 获取当前.exe文件的目录
        exe_folder_path = os.path.dirname(sys.executable)
        # 定义"一键摘要结果"文件夹的路径
        output_folder_path = os.path.join(exe_folder_path, "一键摘要结果")
        # 如果文件夹不存在，则创建它
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        # 定义输出.txt文件的路径
        output_file_path = os.path.join(output_folder_path, f'{timestamp}_摘要.txt')

        # 将摘要写入到.txt文件中
        with open(output_file_path, "w", encoding='utf-8') as f:
            f.write(sum_docx)

        savedataalrt("摘要已生成并保存，返回文件夹查看！")

    def over_check_review(self, check):
        savedataalrt = lambda message: QMessageBox.warning(self, "注意", message)

        # 恢复按钮 at the end
        self.True_botton()

        self.check = check
        if self.check == "over":
            # 文件命名
            self.update_excel_filename = ""
            self.input_informa.clear()
            self.input_informa.append("文献综述数据自动生成完毕！请保存数据或返回查看")
            savedataalrt("文献综述数据自动生成完毕！请保存数据或返回查看")

            # 获取当前.exe文件的目录
            exe_folder_path = os.path.dirname(sys.executable)

            # 检查是否存在 "一键综述结果" 文件夹，如果不存在则创建它
            directory = os.path.join(exe_folder_path, "一键综述结果")
            if not os.path.exists(directory):
                os.makedirs(directory)

            # 将文件保存到 "一键综述结果" 文件夹中
            file_path = os.path.join(directory, 'AI回答记录.txt')
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(self.Chat_response.toPlainText())

            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d%H%M%S")
            file_path_timestamped = os.path.join(directory, f'{timestamp}_本次回答结果.txt')
            with open(file_path_timestamped, 'w', encoding='utf-8') as f:
                f.write(self.Chat_response.toPlainText())

    # 让所有按钮失效
    def False_botton(self):
        self.Submit_to_Gpt.clicked.disconnect(self.Gpt_connect)
        self.clear_botton.clicked.disconnect(self.Clear_token)
        self.Save_resonse.clicked.disconnect(self.Sava_response_func)
        self.Review_data_botton.clicked.disconnect(self.Gpt_connect_review)
        self.sum_review_btn.clicked.disconnect(self.Gpt_connect_sum)
        self.abstract_btn.clicked.disconnect(self.handle_abstract_btn_clicked)
        self.input_informa.setReadOnly(True)

    # 让所有按钮恢复功能
    def True_botton(self):
        self.Submit_to_Gpt.clicked.connect(self.Gpt_connect)
        self.clear_botton.clicked.connect(self.Clear_token)
        self.Save_resonse.clicked.connect(self.Sava_response_func)
        self.Review_data_botton.clicked.connect(self.Gpt_connect_review)
        self.sum_review_btn.clicked.connect(self.Gpt_connect_sum)
        self.abstract_btn.clicked.connect(self.handle_abstract_btn_clicked)
        self.input_informa.setReadOnly(False)


#################################线程类################################
# 聊天功能的线程
class MyThread_gpt_chat(QThread):
    # GPT返回结果的信号
    gpt_answer_signal = pyqtSignal(str)
    # GPT返回的新的PROMPT
    gpt_prompt_update_signal = pyqtSignal(list)
    # GPT消耗的token情况
    gpt_token_consume_signal = pyqtSignal(dict)
    # GPT回答结束信号
    gpt_answer_over_signal = pyqtSignal(str)
    # 定义一个新的信号用于错误处理
    gpt_error_signal = pyqtSignal(str)

    def __init__(self, gpt_dict, gpt_version, request_port):
        super(MyThread_gpt_chat, self).__init__()
        self.gpt_dict = gpt_dict
        self.gpt_version = gpt_version
        self.request_port = request_port

    def run(self):
        tc = TokenCounter(self.gpt_version)
        token_count = tc.num_tokens_from_messages(self.gpt_dict["PROMPT_LIST"])
        if self.gpt_version == 'gpt-3.5-turbo-16k' and token_count < 16384:
            gpt = ChatGPT_conversation_3(self.gpt_dict["API_KEY"], self.gpt_dict["PROMPT_LIST"], self.request_port)
        elif self.gpt_version == 'gpt-4-0613' and token_count < 8192:
            gpt = ChatGPT_conversation_4(self.gpt_dict["API_KEY"], self.gpt_dict["PROMPT_LIST"], self.request_port)
        else:
            self.gpt_answer_signal.emit("输入信息过长，请检查！")
            return

        # 分别接收答案数据、更新后的对话数据、token消耗数据
        answer, PROMPT_LIST_UPDATE, usage, model, error = gpt.creat_conversation(self.gpt_version)
        if error:
            self.gpt_error_signal.emit(error)  # 发送错误信号
            return  # 立即结束线程的执行
        else:
            if answer is not None:
                self.gpt_answer_signal.emit(answer)
                self.gpt_prompt_update_signal.emit(PROMPT_LIST_UPDATE)
                self.gpt_token_consume_signal.emit({'usage': usage, 'model': model})
            else:
                self.gpt_answer_signal.emit("未知错误")

        self.gpt_answer_over_signal.emit("over")


# 一键综述功能的线程
class MyThread_gpt_review(QThread):
    # GPT返回结果的信号
    gpt_answer_signal = pyqtSignal(str)
    # 这个信号给输入框添加综述的条数清空
    gpt_status_signal = pyqtSignal(str)
    # GPT消耗的token情况
    gpt_token_consume_signal = pyqtSignal(dict)
    # GPT回答结束信号
    gpt_answer_over_signal = pyqtSignal(str)

    # 定义一个新的信号用于错误处理
    gpt_error_signal = pyqtSignal(str)

    def __init__(self, gpt_dict, gpt_version, request_port):
        super(MyThread_gpt_review, self).__init__()
        self.gpt_dict = gpt_dict
        self.gpt_version = gpt_version
        self.request_port = request_port

    def run(self):
        num = 0
        answer_list = []  # 创建一个新列表用于存储所有的答案部分

        # 遍历每一个提示
        for each_prompt in self.gpt_dict["PROMPT_LIST"]:
            retry_count = 0  # 初始化重试计数器
            success = False  # 标志，用于检查请求是否成功

            # 重试机制：最多尝试3次
            while not success and retry_count < 3:
                try:
                    # 令牌计数逻辑
                    tc = TokenCounter(self.gpt_version)
                    token_count = tc.num_tokens_from_messages([each_prompt])

                    # 根据GPT版本和令牌计数来决定使用哪个GPT对象
                    if self.gpt_version == 'gpt-3.5-turbo-16k' and token_count < 16384:
                        gpt = ChatGPT_conversation_3(self.gpt_dict["API_KEY"], [each_prompt], self.request_port)
                    elif self.gpt_version == 'gpt-4-0613' and token_count < 8192:
                        gpt = ChatGPT_conversation_4(self.gpt_dict["API_KEY"], [each_prompt], self.request_port)
                    else:
                        self.gpt_answer_signal.emit("输入信息过长，请检查！")
                        return

                    # 发送状态信号以通知进度
                    self.gpt_status_signal.emit(f"Chat_GPT正在生成第{num}-{num + 5}条综述数据，请等待！")

                    # 获取GPT对话结果
                    answer, PROMPT_LIST_UPDATE, usage, model, error = gpt.creat_conversation(self.gpt_version)

                    # 检查是否有错误，并引发异常以触发重试机制
                    if error:
                        self.gpt_error_signal.emit(error)
                        raise Exception("GPT请求错误")

                    # 如果答案可用，则发送相应的信号
                    elif answer is not None:
                        self.gpt_answer_signal.emit(answer)
                        self.gpt_token_consume_signal.emit({'usage': usage, 'model': model})

                    num += 5
                    success = True  # 将此请求标记为成功

                # 处理异常并实现重试逻辑
                except Exception as e:
                    self.gpt_error_signal.emit(f"连接出错，60秒后进行第{retry_count}次重试，关闭错误弹窗即可\n"+str(e))
                    retry_count += 1
                    if retry_count < 3:  # 只有在最后一次重试之前才休眠
                        time.sleep(60)  # 等待60秒再重试

        self.gpt_answer_over_signal.emit("over")


# 一键总结功能的线程
class MyThread_gpt_sum(QThread):
    # GPT返回结果的信号
    gpt_answer_signal = pyqtSignal(str)
    # GPT返回的新的PROMPT
    gpt_prompt_update_signal = pyqtSignal(list)
    # GPT消耗的token情况
    gpt_token_consume_signal = pyqtSignal(dict)
    # GPT回答结束信号
    gpt_answer_over_signal = pyqtSignal(str)
    # 定义一个新的信号用于错误处理
    gpt_error_signal = pyqtSignal(str)
    def __init__(self, gpt_dict, gpt_version, request_port):
        super(MyThread_gpt_sum, self).__init__()
        self.gpt_dict = gpt_dict
        self.gpt_version = gpt_version
        self.request_port = request_port

    def run(self):
        tc = TokenCounter(self.gpt_version)
        token_count = tc.num_tokens_from_messages(self.gpt_dict["PROMPT_LIST"])
        if self.gpt_version == 'gpt-3.5-turbo-16k' and token_count < 16384:
            gpt = ChatGPT_conversation_3(self.gpt_dict["API_KEY"], self.gpt_dict["PROMPT_LIST"], self.request_port)
        elif self.gpt_version == 'gpt-4-0613' and token_count < 8192:
            gpt = ChatGPT_conversation_4(self.gpt_dict["API_KEY"], self.gpt_dict["PROMPT_LIST"], self.request_port)
        else:
            self.gpt_answer_signal.emit("输入信息过长，请检查！")
            return
        # 分别接收答案数据、更新后的对话数据、token消耗数据
        answer, PROMPT_LIST_UPDATE, usage, model, error = gpt.creat_conversation(self.gpt_version)
        if error:
            self.gpt_error_signal.emit(error)  # 发送错误信号
            return  # 立即结束线程的执行
        elif answer is not None:
            self.gpt_answer_signal.emit(answer)
            self.gpt_token_consume_signal.emit({'usage': usage, 'model': model})
        self.gpt_answer_over_signal.emit(answer)

#一键翻译线程



##################################数据处理类#############################
# 处理数据弹出按钮框
class DataprocessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('数据预处理')
        # 改变对话框的大小
        self.resize(150, 150)

        # 去掉问号按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.btn_zn = QPushButton('中文数据', self)
        self.btn_en = QPushButton('英文数据', self)
        # 设置按钮的宽度
        self.btn_zn.setMinimumHeight(45)
        self.btn_en.setMinimumHeight(45)

        self.btn_zn.clicked.connect(self.parent().ZN_data_choose)
        self.btn_en.clicked.connect(self.parent().EN_data_choose)

        layout.addWidget(self.btn_zn)
        layout.addWidget(self.btn_en)  #


#######################################一键摘要功能的类（整合到一个py文件中）##########################
# 一键摘要功能对话框
class BtnFilterDialog(QDialog):
    def __init__(self, titles, parent=None):
        super(BtnFilterDialog, self).__init__(parent)
        self.setWindowTitle("数据筛选")
        self.processor = titles
        self.selected_contents = []

        def create_buttons(list_widget):
            button_layout = QVBoxLayout()
            select_all_button = QPushButton("全选")
            select_all_button.clicked.connect(lambda: self.select_all(list_widget))
            button_layout.addWidget(select_all_button)
            clear_button = QPushButton("清除")
            clear_button.clicked.connect(lambda: self.clear_selection(list_widget))
            button_layout.addWidget(clear_button)
            return button_layout

        self.title_list = QListWidget()
        self.title_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.title_list.addItems(self.processor.get_titles())
        self.title_list.itemSelectionChanged.connect(self.display_selected_titles_content)

        self.title_buttons = create_buttons(self.title_list)

        # 使用QTextEdit替换原先的QTextBrowser
        self.text_editor = QTextEdit()
        self.text_editor.setMinimumSize(600, 400)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        title_layout = QVBoxLayout()
        title_layout.addWidget(QLabel("标题筛选"))
        title_layout.addWidget(self.title_list)
        title_layout.addLayout(self.title_buttons)

        list_layout = QHBoxLayout()
        list_layout.addLayout(title_layout)
        list_layout.addWidget(self.text_editor)  # 修改这里为text_editor

        button_layout = QHBoxLayout()
        button_layout.addWidget(buttonBox)

        layout = QVBoxLayout()
        layout.addLayout(list_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def display_selected_titles_content(self):
        selected_titles_set = set(item.text() for item in self.title_list.selectedItems())
        content_pieces = []

        for title_text, level in self.processor.titles:
            if title_text in selected_titles_set:
                content = self.processor.get_content_for_title(title_text)
                lang = "zh" if any(c.isalpha() and ord(c) > 127 for c in content) else "en"
                formatted_content = f'<div style="background-color: #FFFFB3;"><h{level} lang="{lang}">{title_text}</h{level}></div><p lang="{lang}">{content}</p>'
                content_pieces.append(formatted_content)

        style = """
        <style>
            h1, h2, h3, h4, h5, h6, p {
                text-align: justify;
                text-indent: 2ch;
            }
            [lang='zh'] {
                font-family: 宋体;
            }
            [lang='en'] {
                font-family: 'Times New Roman';
            }
        </style>
        """
        formatted_output = style + "<br>".join(content_pieces)
        self.text_editor.setHtml(formatted_output)  # 修改这里为text_editor

    def select_all(self, list_widget):
        list_widget.selectAll()

    def clear_selection(self, list_widget):
        list_widget.clearSelection()

    def get_selected_Abstract_content(self):
        selected_titles = [item.text() for item in self.title_list.selectedItems()]
        selected_content = [self.processor.get_content_for_title(title) for title in selected_titles]
        return selected_content
    def accept(self):
        if len(self.title_list.selectedItems()) == 0:
            QMessageBox.warning(self, "提示", "您未选择任何内容")
            return
        super().accept()



# 一键功能的文档处理类
class DocxProcessor:
    def __init__(self, file_path):
        self.doc = Document(file_path)
        self.titles = []  # This will now store tuples (title_text, heading_level)
        self.contents = []
        self.file_path = file_path

    def extract_titles_and_contents(self):
        current_title = None
        current_content = []
        current_level = None

        for para in self.doc.paragraphs:
            if para.style.name.startswith('Heading'):
                if current_title:
                    self.titles.append((current_title, current_level))
                    self.contents.append("\n".join(current_content))
                current_title = para.text
                current_level = int(para.style.name.split(' ')[-1])  # Extracting the level number from style name
                current_content = []
            else:
                current_content.append(para.text)

        if current_title:
            self.titles.append((current_title, current_level))
            self.contents.append("\n".join(current_content))

    def get_titles(self):
        return [title[0] for title in self.titles]  # Only return the title texts, not the levels

    def get_content_for_title(self, title_text):
        try:
            index = next(index for index, (title, level) in enumerate(self.titles) if title == title_text)
            return self.contents[index]
        except StopIteration:
            return "Title not found."

    def get_level_for_title(self, title_text):
        try:
            return next(level for title, level in self.titles if title == title_text)
        except StopIteration:
            return None


#中英文文献数据处理
class DataProcessor:
    def __init__(self, input_file):
        self.input_file = input_file

    def _ensure_output_directory(self):
        # 获取当前.py文件的目录
        script_folder_path = os.path.dirname((sys.executable))
        # 定义"数据处理结果"文件夹的路径
        output_folder_path = os.path.join(script_folder_path, "数据处理结果")
        # 如果文件夹不存在，则创建它
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
        return output_folder_path

    def CN_data_process(self):
        data_list = []
        data_dict = {}

        with open(self.input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('T1'):
                    data_dict['Title'] = re.sub('T1 ', '', line.strip())
                elif line.startswith('A1'):
                    data_dict['Author'] = re.sub('A1 ', '', line.strip())
                elif line.startswith('YR'):
                    data_dict['Year'] = re.sub('YR ', '', line.strip())
                elif line.startswith('AB'):
                    data_dict['Abstract'] = re.sub('AB ', '', line.strip())
                elif line.startswith('vo'):
                    data_dict['Volume'] = re.sub('vo ', '', line.strip())
                elif line.startswith('IS'):
                    data_dict['Issue'] = re.sub('IS ', '', line.strip())
                elif line.startswith('JF'):
                    data_dict['Journal'] = re.sub('JF ', '', line.strip())
                elif line.startswith('RT'):
                    if data_dict:
                        data_list.append(data_dict)
                        data_dict = {}

        if data_dict:
            data_list.append(data_dict)

        columns_order = ['Title', 'Author', 'Year', 'Abstract', 'Volume', 'Issue', 'Journal']
        df = pd.DataFrame(data_list, columns=columns_order)
        columns_map = {'Title': '标题', 'Author': '作者', 'Year': '年份', 'Abstract': '摘要', 'Volume': '卷号',
                       'Issue': '期号', 'Journal': '期刊'}
        df.rename(columns=columns_map, inplace=True)

        # 使用新方法确保输出目录存在并获取其路径
        output_folder_path = self._ensure_output_directory()
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        output_filename = os.path.join(output_folder_path, f'{timestamp}_中文文献数据.csv')
        df.to_csv(output_filename, index=False)

    def EN_data_process(self):
        df = pd.read_excel(self.input_file)
        desired_columns = ['Article Title', 'Authors', 'Publication Year', 'Abstract', 'Source Title']
        new_df = df[desired_columns]
        for col in new_df.columns:
            if new_df[col].dtype == 'object':
                new_df.loc[:, col] = new_df[col].str.replace('\\s+', ' ', regex=True)
        new_df = new_df.dropna()
        columns_map = {'Article Title': '标题', 'Authors': '作者', 'Publication Year': '年份', 'Abstract': '摘要',
                       'Source Title': '期刊'}
        new_df.rename(columns=columns_map, inplace=True)

        # 使用新方法确保输出目录存在并获取其路径
        output_folder_path = self._ensure_output_directory()
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        output_filename = os.path.join(output_folder_path, f'{timestamp}_英文文献数据.csv')
        new_df.to_csv(output_filename, index=False)


if __name__ == "__main__":
    import sys

    # 1. 创建一个应用程序对象
    app = QApplication(sys.argv)

    # 2.1 创建控件
    window = International_App_Window()

    # 2.4 展示控件
    window.show()

    # 3. 应用程序的执行, 进入到消息循环
    # 让整个程序开始执行,并且进入到消息循环(无限循环)
    # 检测整个程序所接收到的用户的交互信息
    sys.exit(app.exec_())
