# -*- coding:utf-8 -*-

# Author:六非博
# 关注微信公众号：六非博
# CreatTime:2023/8/15
# FilesNmae:英文数据单独处理，单独打包

import sys
import os
import pandas as pd
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QVBoxLayout


class DataProcessingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.folder_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('数据合并软件')
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        self.btn_merge = QPushButton('数据合并', self)
        self.btn_merge.clicked.connect(self.on_merge_click)
        layout.addWidget(self.btn_merge)

        self.btn_open_folder = QPushButton('项目文件夹', self)
        self.btn_open_folder.clicked.connect(self.on_open_folder_click)
        layout.addWidget(self.btn_open_folder)

        self.setLayout(layout)

    def on_merge_click(self):
        try:
            self.folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
            if self.folder_path:
                all_dataframes = []
                for file_name in os.listdir(self.folder_path):
                    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                        self.input_file = os.path.join(self.folder_path, file_name)
                        processed_data = self.EN_data_process()
                        all_dataframes.append(processed_data)

                if all_dataframes:
                    combined_df = pd.concat(all_dataframes, ignore_index=True)

                    # Remove duplicate rows
                    combined_df.drop_duplicates(inplace=True)

                    now = datetime.datetime.now()
                    timestamp = now.strftime("%Y%m%d%H%M%S")
                    combined_df.to_csv(os.path.join(self.folder_path, f'{timestamp}_合并数据.csv'), index=False)

                    # Show success message
                    QMessageBox.information(self, '成功', '数据合并成功!')

        except Exception as e:
            QMessageBox.critical(self, '错误', f'发生错误: {str(e)}')

    def on_open_folder_click(self):
        if self.folder_path:
            os.startfile(self.folder_path)
        else:
            QMessageBox.warning(self, '提示', '请先选择一个项目文件夹')

    def EN_data_process(self):
        # Load the Excel file
        df = pd.read_excel(self.input_file)

        # Select the desired columns
        desired_columns = ['Article Title', 'Authors', 'Publication Year', 'Abstract', 'Source Title']
        new_df = df[desired_columns]

        # 去掉空白字符
        for col in new_df.columns:
            if new_df[col].dtype == 'object':
                new_df.loc[:, col] = new_df[col].str.replace('\s+', ' ', regex=True)

        # 删掉有缺失值的文献
        new_df = new_df.dropna()

        # 修改列名
        columns_map = {
            'Article Title': '标题',
            'Authors': '作者',
            'Publication Year': '年份',
            'Abstract': '摘要',
            'Source Title': '期刊',
        }
        # 使用 rename 方法批量修改列名
        new_df.rename(columns=columns_map, inplace=True)

        return new_df


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DataProcessingApp()
    ex.show()
    sys.exit(app.exec_())
