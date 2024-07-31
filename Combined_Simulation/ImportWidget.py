from __future__ import annotations

import sys
import os
import logging
import traceback

from PyQt5 import QtWidgets, QtCore, QtGui

from ProjectManager import projectManagerSingleton

class ImportWidget(QtWidgets.QDialog):

    def __init__(self, parent = None, type=None):
        super().__init__(parent)

        self.project_path = None
        self.project_type = type
        self.loading_message = QtWidgets.QMessageBox()
        self.loading_message.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Close)
        self.initUI()

    def initUI(self):

        layout = QtWidgets.QGridLayout()

        self.pathLineEdit = QtWidgets.QLineEdit()
        self.openButton = QtWidgets.QPushButton('打开')
        self.importButton = QtWidgets.QPushButton('导入')
        self.cancelButton = QtWidgets.QPushButton('取消')

        layout.addWidget(self.pathLineEdit, 1, 0, 1, 3)
        layout.addWidget(self.openButton, 1, 3, 1, 1)
        layout.addWidget(self.importButton, 2, 0, 1, 2)
        layout.addWidget(self.cancelButton, 2, 2, 1, 2)

        # layout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.setLayout(layout)

        self.setWindowTitle("Import Project")
        # self.setGeometry(300, 300, 400, 200)
        self.setFixedSize(400, 150)
        '''隐藏问号'''
        # self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        # self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WA_SetWindowIcon)

        # self.setWindowFlags(QtCore.Qt.Drawer) # 去掉标题栏图标
        self.setWindowIcon(QtGui.QIcon(""))

        self.setStyleSheet("background-color:white")

        self.openButton.clicked.connect(self.openFile)
        self.importButton.clicked.connect(self.importProject)
        self.cancelButton.clicked.connect(self.cancelOperation)

        projectManagerSingleton.project_manager_notifier.connect(self.load_project_finished)

    def openFile(self):
        file_path, file_type = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', '', '')
        logging.info("open file %s, file type: %s" % (file_path, file_type))

        if 0 == len(file_path):
            reply = QtWidgets.QMessageBox.about(self, "路径为空", "文件路径不能为空")
            return

        if self.project_type == "HFSS" and file_path.endswith(".aedt") is not True:
            reply = QtWidgets.QMessageBox.about(self, "文件格式错误", "请打开aedt格式文件")
            return

        if self.project_type == "Comsol" and file_path.endswith(".mph") is not True:
            reply = QtWidgets.QMessageBox.about(self, "文件格式错误", "请打开mph格式文件")
            return

        if self.project_type == "Interconnect" and file_path.endswith(".icp") is not True:
            reply = QtWidgets.QMessageBox.about(self, "文件格式错误", "请打开icp格式文件")
            return


        if len(file_path) != 0:
            self.pathLineEdit.setText(file_path)
            self.project_path = file_path
        else:
            self.pathLineEdit.setText("file path is empty!")

    def importProject(self):
        self.loading_message.setText("loading project, do not operate")
        self.loading_message.show()
        projectManagerSingleton.load_project(self.project_path, self.project_type)

    def load_project_finished(self):
        self.loading_message.close()
        self.close()

    def cancelOperation(self):
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    importWidget = ImportWidget()
    importWidget.show()
    sys.exit(app.exec_())