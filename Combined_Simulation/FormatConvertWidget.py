from __future__ import annotations

import sys
import traceback
import logging
from typing import Union
from PyQt5 import QtWidgets, QtCore, QtGui

from HFSS_ReportSettingWidget import Report_Widget
from ProjectManager import projectManagerSingleton

class Interconnect_InputTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setMinimumHeight(150)
        self.setMaximumHeight(150)
        self.setColumnCount(4)

        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 150)
        self.setColumnWidth(3, 130)

        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("Idx")
        self.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("element name")
        self.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("property")
        self.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("file name")
        self.setHorizontalHeaderItem(3, item)

        self.verticalHeader().setVisible(False)  # 索引栏不可见
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # 设置选择行为，按行选择
        self.setStyleSheet("selection-background-color:rgb(255,209,128)")  # 设置选中行背景颜色

class HFSS_ReportTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setMinimumHeight(150)
        self.setMaximumHeight(150)
        self.setColumnCount(5)

        self.setColumnWidth(0, 30)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 120)
        self.setColumnWidth(4, 100)

        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("Idx")
        self.setHorizontalHeaderItem(0, item)

        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("user define")
        self.setHorizontalHeaderItem(1, item)

        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("report name")
        self.setHorizontalHeaderItem(2, item)

        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("expression")
        self.setHorizontalHeaderItem(3, item)

        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("solution")
        self.setHorizontalHeaderItem(4, item)

        self.verticalHeader().setVisible(False)  # 索引栏不可见
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # 设置选择行为，按行选择
        self.setStyleSheet("selection-background-color:rgb(255,209,128)")  # 设置选中行背景颜色

class Comsol_ReportTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setMinimumHeight(150)
        self.setMaximumHeight(150)
        self.setColumnCount(3)

        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 200)
        self.setColumnWidth(2, 150)

        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("Idx")
        self.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("table name")
        self.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("file name")
        self.setHorizontalHeaderItem(2, item)

        self.verticalHeader().setVisible(False)  # 索引栏不可见
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # 设置选择行为，按行选择
        self.setStyleSheet("selection-background-color:rgb(255,209,128)")  # 设置选中行背景颜色

class CollapsibleWidget(QtWidgets.QWidget):
    def __init__(self, contextWidget: QtWidgets.QWidget, parent=None, title=""):
        super().__init__(parent)

        self.collapsibleButton = QtWidgets.QToolButton(self)
        self.collapsibleButton.setText(title)
        self.collapsibleButton.setCheckable(True)
        self.collapsibleButton.setChecked(True)
        self.collapsibleButton.setStyleSheet("QToolButton { border: none; }")
        self.collapsibleButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.collapsibleButton.setArrowType(QtCore.Qt.ArrowType.DownArrow)
        self.collapsibleButton.pressed.connect(self.onPressed)

        self.contentArea = contextWidget
        VBox = QtWidgets.QVBoxLayout(self)
        VBox.setSpacing(0)
        VBox.setContentsMargins(0, 0, 0, 0)
        VBox.addWidget(self.collapsibleButton)
        VBox.addWidget(self.contentArea)
        self.setLayout(VBox)

    def onPressed(self):
        checked = self.collapsibleButton.isChecked()
        # logging.info(checked)
        # self.collapsibleButton.setArrowType(QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow)
        if not checked:
            self.collapsibleButton.setArrowType(QtCore.Qt.ArrowType.DownArrow)
            self.contentArea.setVisible(True)
        else:
            self.collapsibleButton.setArrowType(QtCore.Qt.ArrowType.RightArrow)
            self.contentArea.setVisible(False)

class Comsol_Result_Table_Widget(QtWidgets.QWidget):
    comsol_result_table_config_notifier = QtCore.pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_row_id = 0
        self.current_row_info = None

        self.setObjectName("comsol result table")
        self.resize(600, 150)
        self.setWindowTitle("comsol result table setting")
        self.setStyleSheet("background-color:white")
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)

        grid_layout = QtWidgets.QGridLayout()
        num_name_label = QtWidgets.QLabel("name")
        self.num_name_edit = QtWidgets.QLineEdit()
        type_label = QtWidgets.QLabel("type")
        self.type_edit = QtWidgets.QLineEdit()
        data_label = QtWidgets.QLabel("data")
        self.data_edit = QtWidgets.QLineEdit()
        table_name_label = QtWidgets.QLabel("table name")
        self.table_name_edit = QtWidgets.QLineEdit()
        table_comments_label = QtWidgets.QLabel("table comments")
        self.table_comments_edit = QtWidgets.QLineEdit()
        add_button = QtWidgets.QPushButton("add")
        add_button.clicked.connect(self.add_result_table)
        delete_button = QtWidgets.QPushButton("delete")
        delete_button.clicked.connect(self.delete_result_table)
        save_button = QtWidgets.QPushButton("save")
        save_button.clicked.connect(self.save_result_table)
        export_file_label = QtWidgets.QLabel("export file")
        self.export_file_edit = QtWidgets.QLineEdit()

        grid_layout.addWidget(num_name_label, 1, 0, 1, 1)
        grid_layout.addWidget(self.num_name_edit, 1, 1, 1, 1)
        grid_layout.addWidget(type_label, 2, 0, 1, 1)
        grid_layout.addWidget(self.type_edit, 2, 1, 1, 1)
        grid_layout.addWidget(data_label, 3, 0, 1, 1)
        grid_layout.addWidget(self.data_edit, 3, 1, 1, 1)
        grid_layout.addWidget(table_name_label, 4, 0, 1, 1)
        grid_layout.addWidget(self.table_name_edit, 4, 1, 1, 1)
        grid_layout.addWidget(table_comments_label, 5, 0, 1, 1)
        grid_layout.addWidget(self.table_comments_edit, 5, 1, 1, 1)
        grid_layout.addWidget(add_button, 6, 0, 1, 1)
        grid_layout.addWidget(delete_button, 6, 1, 1, 1)
        grid_layout.addWidget(save_button, 7, 0, 1, 2)
        grid_layout.addWidget(export_file_label, 8, 0, 1, 1)
        grid_layout.addWidget(self.export_file_edit, 8, 1, 1, 1)

        rowSize = 25
        colSize = 100
        for row in range(grid_layout.rowCount()):
            grid_layout.setRowStretch(row, 1)
            grid_layout.setRowMinimumHeight(row, rowSize)
        for col in range(grid_layout.columnCount()):
            grid_layout.setColumnStretch(col, 1)
            grid_layout.setColumnMinimumWidth(col, colSize)

        sub_widget = QtWidgets.QWidget()
        sub_widget.setLayout(grid_layout)

        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 200)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("Idx")
        self.table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("expression")
        self.table_widget.setHorizontalHeaderItem(1, item)
        self.table_widget.verticalHeader().setVisible(False)  # 索引栏不可见

        HBox = QtWidgets.QHBoxLayout()
        HBox.addWidget(sub_widget)
        HBox.addWidget(self.table_widget)

        self.setLayout(HBox)

        # 添加一些默认参数
        self.set_default_parameters()

    def set_current_item(self, row_id):
        self.current_row_id = row_id

    def set_current_item_info(self, info):
        logging.info(info)
        self.current_row_info = info

    def set_default_parameters(self):
        # 设置一些默认参数
        self.num_name_edit.setText("gev1")
        self.type_edit.setText("EvalGlobal")
        self.data_edit.setText("dset3")
        self.table_name_edit.setText("tbl1")
        self.table_comments_edit.setText("Global Evaluation 1")
        self.export_file_edit.setText("modulator_ret.txt")

        self.table_widget.setRowCount(2)

        item = QtWidgets.QTableWidgetItem(0)
        item.setText(str(0))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(0, 0, item)

        item = QtWidgets.QTableWidgetItem("expr_1")
        item.setText("imag(ewfd.neff)")
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(0, 1, item)

        item = QtWidgets.QTableWidgetItem(1)
        item.setText(str(1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(1, 0, item)

        item = QtWidgets.QTableWidgetItem("expr_2")
        item.setText("real(ewfd.neff)")
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(1, 1, item)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        # 每次打开的时候将参数设置成默认值
        if self.current_row_info is None:
            self.set_default_parameters()
        else:
            self.num_name_edit.setText(self.current_row_info["numerical name"])
            self.type_edit.setText(self.current_row_info["numerical type"])
            self.data_edit.setText(self.current_row_info["data type"])
            self.table_name_edit.setText(self.current_row_info["table name"])
            self.table_comments_edit.setText(self.current_row_info["table comment"])
            self.export_file_edit.setText(self.current_row_info["export file"])

            num_item = len(self.current_row_info["expression list"])
            self.table_widget.setRowCount(2)
            for index in range(num_item):
                item = QtWidgets.QTableWidgetItem(index)
                item.setText(str(index))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(index, 0, item)

                item = QtWidgets.QTableWidgetItem("expr_" + str(index))
                item.setText(self.current_row_info["expression list"][index])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(index, 1, item)

            # 使用后将属性置为空，避免被另一行数据使用
            self.current_row_info = None


    def save_result_table(self):
        info = dict()
        info["current row id"] = self.current_row_id
        info["numerical name"] = self.num_name_edit.text()
        info["numerical type"] = self.type_edit.text()
        info["data type"] = self.data_edit.text()
        info["table name"] = self.table_name_edit.text()
        info["table comment"] = self.table_comments_edit.text()
        info["export file"] = self.export_file_edit.text()

        expression_list = list()
        num_item = self.table_widget.rowCount()
        for index in range(num_item):
            item = self.table_widget.item(index, 1)
            expression_list.append(item.text())

        info["expression list"] = expression_list
        self.comsol_result_table_config_notifier.emit(info)

    def add_result_table(self):
        pass

    def delete_result_table(self):
        pass

class Comsol_Input_FormatInfoWidget(QtWidgets.QWidget):
    format_info_notifier = QtCore.pyqtSignal(dict)

    def __init__(self, basicInfo: Union[dict, None] = None, settingInfo: Union[dict, None] = None, parent=None):
        super().__init__(parent)

        logging.info(basicInfo)
        logging.info(settingInfo)

        self.comsol_config = dict()
        if settingInfo is not None and "item dict" in settingInfo.keys():
            self.comsol_config = settingInfo["item dict"]
        self.comsol_result_config_table_widget = Comsol_Result_Table_Widget()
        self.comsol_result_config_table_widget.comsol_result_table_config_notifier.connect(self.update_table_config)

        # 基本信息窗口
        basicInfoWidgetGrid = QtWidgets.QGridLayout()
        projectNameLabel = QtWidgets.QLabel("project name")
        projectNameEdit = QtWidgets.QLineEdit()
        projectNameEdit.setEnabled(False)
        projectTypeLabel = QtWidgets.QLabel("project type")
        projectTypeEdit = QtWidgets.QLineEdit()
        projectTypeEdit.setEnabled(False)
        position_x_label = QtWidgets.QLabel("position x")
        position_x_edit = QtWidgets.QLineEdit()
        position_x_edit.setEnabled(False)
        position_y_label = QtWidgets.QLabel("position y")
        position_y_edit = QtWidgets.QLineEdit()
        position_y_edit.setEnabled(False)

        if isinstance(basicInfo, dict):
            projectNameEdit.setText(basicInfo['project_name'])
            projectTypeEdit.setText(basicInfo['project_type'])
            position_x_edit.setText(str(basicInfo['position_x']))
            position_y_edit.setText(str(basicInfo['position_y']))

        basicInfoWidgetGrid.addWidget(projectNameLabel, 1, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(projectNameEdit, 1, 1, 1, 1)
        basicInfoWidgetGrid.addWidget(projectTypeLabel, 2, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(projectTypeEdit, 2, 1, 1, 1)
        basicInfoWidgetGrid.addWidget(position_x_label, 3, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(position_x_edit, 3, 1, 1, 1)
        basicInfoWidgetGrid.addWidget(position_y_label, 4, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(position_y_edit, 4, 1, 1, 1)

        basicInfoWidget = QtWidgets.QWidget()
        basicInfoWidget.setLayout(basicInfoWidgetGrid)

        VBox = QtWidgets.QVBoxLayout()
        VBox.addWidget(basicInfoWidget)

        # 设置数据输出窗口
        Comsol_VBox = QtWidgets.QVBoxLayout()

        buttonWidget = QtWidgets.QWidget()
        button_HBox = QtWidgets.QHBoxLayout()
        addButton = QtWidgets.QPushButton("add")
        addButton.clicked.connect(self.add_table)
        deleteButton = QtWidgets.QPushButton("delete")
        deleteButton.clicked.connect(self.delete_table)
        saveButton = QtWidgets.QPushButton("save")
        saveButton.clicked.connect(self.save_table)
        button_HBox.addWidget(addButton)
        button_HBox.addWidget(deleteButton)
        button_HBox.addWidget(saveButton)
        buttonWidget.setLayout(button_HBox)

        Comsol_VBox.addWidget(buttonWidget)

        self.report_table_widget = Comsol_ReportTableWidget(self)
        self.report_table_widget.cellDoubleClicked.connect(self.show_comsol_result_config_table)  # 双击后出现弹窗可以编辑
        self.report_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 设置表格不可编辑
        Comsol_VBox.addWidget(self.report_table_widget)

        exportWidget = QtWidgets.QWidget()
        export_HBox = QtWidgets.QHBoxLayout()
        exportDirNameLabel = QtWidgets.QLabel("export directory")
        self.exportDirNameEdit = QtWidgets.QLineEdit()
        export_HBox.addWidget(exportDirNameLabel)
        export_HBox.addWidget(self.exportDirNameEdit)
        exportWidget.setLayout(export_HBox)

        Comsol_VBox.addWidget(exportWidget)

        exportDirBrowserButton = QtWidgets.QPushButton("Browse")
        exportDirBrowserButton.clicked.connect(self.set_export_dirctory)

        Comsol_VBox.addWidget(exportDirBrowserButton)

        HFSS_OutputWidget = QtWidgets.QWidget()
        HFSS_OutputWidget.setLayout(Comsol_VBox)
        VBox.addWidget(HFSS_OutputWidget)

        if "export dirction" in settingInfo.keys():
            self.exportDirNameEdit.setText(settingInfo["export dirction"])

        if "item dict" in settingInfo.keys():
            num_item = len(settingInfo['item dict'])
            self.report_table_widget.setRowCount(num_item)

            for index in range(num_item):
                item = QtWidgets.QTableWidgetItem(str(index + 1))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.report_table_widget.setItem(index, 0, item)

                item = QtWidgets.QTableWidgetItem(settingInfo['item dict'][index]['table name'])
                item.setText(settingInfo['item dict'][index]['table name'])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.report_table_widget.setItem(index, 1, item)

                item = QtWidgets.QTableWidgetItem(settingInfo['item dict'][index]['export file'])
                item.setText(settingInfo['item dict'][index]['export file'])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.report_table_widget.setItem(index, 2, item)

        self.setLayout(VBox)

    def __del__(self):
        print("FormatInfoWidget delete")

    def add_table(self):
        # 设置需要导出的报告名称
        num_item = self.report_table_widget.rowCount()
        self.report_table_widget.setRowCount(num_item + 1)

        Idx = num_item
        item = QtWidgets.QTableWidgetItem(str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 0, item)

        item = QtWidgets.QTableWidgetItem("table_" + str(Idx + 1))
        item.setText("table_" + str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 1, item)

        item = QtWidgets.QTableWidgetItem("file_" + str(Idx + 1) + ".txt")
        item.setText("file_" + str(Idx + 1) + ".txt")
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 2, item)

    def delete_table(self):
        print("delete report")

    def save_table(self):
        # 添加完需要导出的报告之后要点击保存
        info = dict()
        info["start_setting"] = dict()
        info["start_setting"]["item dict"] = self.comsol_config
        self.format_info_notifier.emit(info)

    def set_export_dirctory(self):
        export_dirctory = QtWidgets.QFileDialog.getExistingDirectory(self, "选取文件夹", "./")
        self.exportDirNameEdit.setText(export_dirctory)
        info = dict()
        info["start_setting"] = dict()
        info["start_setting"]["export dirction"] = export_dirctory
        self.format_info_notifier.emit(info)

    def show_comsol_result_config_table(self, row, column):
        # 双击显示弹窗
        item = self.report_table_widget.item(row, column)
        if item is not None:
            self.comsol_result_config_table_widget.set_current_item(row)
            if row in self.comsol_config.keys():
                self.comsol_result_config_table_widget.set_current_item_info(self.comsol_config[row])
            self.comsol_result_config_table_widget.show()

    def update_table_config(self, info):
        logging.info(info)
        self.comsol_config[info["current row id"]] = info

        # 更新table中的数据
        num_item = self.report_table_widget.rowCount()
        for index in range(num_item):
            if index == info["current row id"]:
                item = self.report_table_widget.item(index, 1)
                item.setText(info["table name"])
                item = self.report_table_widget.item(index, 2)
                item.setText(info["export file"])


class Interconnect_Input_FormatInfoWidget(QtWidgets.QWidget):
    format_info_notifier = QtCore.pyqtSignal(dict)

    def __init__(self, basicInfo: Union[dict, None] = None, settingInfo: Union[dict, None] = None, parent=None):
        super().__init__(parent)

        logging.info(basicInfo)
        logging.info(settingInfo)

        # 基本信息窗口
        basicInfoWidgetGrid = QtWidgets.QGridLayout()
        projectNameLabel = QtWidgets.QLabel("project name")
        projectNameEdit = QtWidgets.QLineEdit()
        projectNameEdit.setEnabled(False)
        projectTypeLabel = QtWidgets.QLabel("project type")
        projectTypeEdit = QtWidgets.QLineEdit()
        projectTypeEdit.setEnabled(False)
        position_x_label = QtWidgets.QLabel("position x")
        position_x_edit = QtWidgets.QLineEdit()
        position_x_edit.setEnabled(False)
        position_y_label = QtWidgets.QLabel("position y")
        position_y_edit = QtWidgets.QLineEdit()
        position_y_edit.setEnabled(False)

        if isinstance(basicInfo, dict):
            projectNameEdit.setText(basicInfo['project_name'])
            projectTypeEdit.setText(basicInfo['project_type'])
            position_x_edit.setText(str(basicInfo['position_x']))
            position_y_edit.setText(str(basicInfo['position_y']))

        basicInfoWidgetGrid.addWidget(projectNameLabel, 1, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(projectNameEdit, 1, 1, 1, 1)
        basicInfoWidgetGrid.addWidget(projectTypeLabel, 2, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(projectTypeEdit, 2, 1, 1, 1)
        basicInfoWidgetGrid.addWidget(position_x_label, 3, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(position_x_edit, 3, 1, 1, 1)
        basicInfoWidgetGrid.addWidget(position_y_label, 4, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(position_y_edit, 4, 1, 1, 1)

        basicInfoWidget = QtWidgets.QWidget()
        basicInfoWidget.setLayout(basicInfoWidgetGrid)

        VBox = QtWidgets.QVBoxLayout()
        VBox.addWidget(basicInfoWidget)

        # 设置数据输入窗口
        Interconnect_VBox = QtWidgets.QVBoxLayout()

        self.interconnect_input_info = None
        buttonWidget = QtWidgets.QWidget()
        button_HBox = QtWidgets.QHBoxLayout()
        addButton = QtWidgets.QPushButton("add")
        addButton.clicked.connect(self.add_import)
        deleteButton = QtWidgets.QPushButton("delete")
        deleteButton.clicked.connect(self.delete_import)
        saveButton = QtWidgets.QPushButton("save")
        saveButton.clicked.connect(self.save_import)
        button_HBox.addWidget(addButton)
        button_HBox.addWidget(deleteButton)
        button_HBox.addWidget(saveButton)
        buttonWidget.setLayout(button_HBox)

        Interconnect_VBox.addWidget(buttonWidget)

        self.import_table_widget = Interconnect_InputTableWidget(self)
        Interconnect_VBox.addWidget(self.import_table_widget)

        importWidget = QtWidgets.QWidget()
        import_HBox = QtWidgets.QHBoxLayout()
        importDirNameLabel = QtWidgets.QLabel("import directory")
        self.importDirNameEdit = QtWidgets.QLineEdit()
        import_HBox.addWidget(importDirNameLabel)
        import_HBox.addWidget(self.importDirNameEdit)
        importWidget.setLayout(import_HBox)

        Interconnect_VBox.addWidget(importWidget)

        importDirBrowserButton = QtWidgets.QPushButton("Browse")
        importDirBrowserButton.clicked.connect(self.set_import_dirctory)

        Interconnect_VBox.addWidget(importDirBrowserButton)

        Interconnect_OutputWidget = QtWidgets.QWidget()
        Interconnect_OutputWidget.setLayout(Interconnect_VBox)
        VBox.addWidget(Interconnect_OutputWidget)

        if "import dirction" in settingInfo.keys():
            self.importDirNameEdit.setText(settingInfo["import dirction"])

        if "import list" in settingInfo.keys():
            num_item = len(settingInfo['import list'])
            self.import_table_widget.setRowCount(num_item)

            for index in range(num_item):
                item = QtWidgets.QTableWidgetItem(str(index + 1))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.import_table_widget.setItem(index, 0, item)

                item = QtWidgets.QTableWidgetItem(settingInfo['import list'][index])
                item.setText(settingInfo['import list'][index])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.import_table_widget.setItem(index, 1, item)

                item = QtWidgets.QTableWidgetItem(settingInfo['property list'][index])
                item.setText(settingInfo['property list'][index])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.import_table_widget.setItem(index, 2, item)

                item = QtWidgets.QTableWidgetItem(settingInfo['file list'][index])
                item.setText(settingInfo['file list'][index])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.import_table_widget.setItem(index, 3, item)

        self.setLayout(VBox)

    def __del__(self):
        print("FormatInfoWidget delete")

    def add_import(self):
        # 设置需要导入数据的模块
        num_item = self.import_table_widget.rowCount()
        self.import_table_widget.setRowCount(num_item + 1)

        Idx = num_item
        item = QtWidgets.QTableWidgetItem(str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.import_table_widget.setItem(Idx, 0, item)

        item = QtWidgets.QTableWidgetItem("element_" + str(Idx + 1))
        item.setText("element_" + str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.import_table_widget.setItem(Idx, 1, item)

        item = QtWidgets.QTableWidgetItem("property_" + str(Idx + 1))
        item.setText("property_" + str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.import_table_widget.setItem(Idx, 2, item)

        item = QtWidgets.QTableWidgetItem("file_" + str(Idx + 1) + ".txt")
        item.setText("file_" + str(Idx + 1) + ".txt")
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.import_table_widget.setItem(Idx, 3, item)

    def delete_import(self):
        print("delete import")

    def save_import(self):
        # 添加完需要导入的数据之后要点击保存
        import_list = list()
        property_list = list()
        file_list = list()
        num_item = self.import_table_widget.rowCount()
        for index in range(num_item):
            item = self.import_table_widget.item(index, 1)
            import_list.append(item.text())

            item = self.import_table_widget.item(index, 2)
            property_list.append(item.text())

            item = self.import_table_widget.item(index, 3)
            file_list.append(item.text())

        info = dict()
        info["end_setting"] = dict()
        info["end_setting"]["import list"] = import_list
        info["end_setting"]["property list"] = property_list
        info["end_setting"]["file list"] = file_list

        self.format_info_notifier.emit(info)

    def set_import_dirctory(self):
        import_dirctory = QtWidgets.QFileDialog.getExistingDirectory(self, "选取文件夹", "./")
        self.importDirNameEdit.setText(import_dirctory)
        info = dict()
        info["end_setting"] = dict()
        info["end_setting"]["import dirction"] = import_dirctory
        self.format_info_notifier.emit(info)

class HFSS_Output_FormatInfoWidget(QtWidgets.QWidget):
    format_info_notifier = QtCore.pyqtSignal(dict)

    def __init__(self, basicInfo: Union[dict, None] = None, settingInfo: Union[dict, None]=None, parent=None):
        super().__init__(parent)

        logging.info(basicInfo)
        logging.info(settingInfo)

        self.project_name = basicInfo['project_name']

        # 基本信息窗口
        basicInfoWidgetGrid = QtWidgets.QGridLayout()
        projectNameLabel = QtWidgets.QLabel("project name")
        projectNameEdit = QtWidgets.QLineEdit()
        projectNameEdit.setEnabled(False)
        projectTypeLabel = QtWidgets.QLabel("project type")
        projectTypeEdit = QtWidgets.QLineEdit()
        projectTypeEdit.setEnabled(False)
        position_x_label = QtWidgets.QLabel("position x")
        position_x_edit = QtWidgets.QLineEdit()
        position_x_edit.setEnabled(False)
        position_y_label = QtWidgets.QLabel("position y")
        position_y_edit = QtWidgets.QLineEdit()
        position_y_edit.setEnabled(False)

        if isinstance(basicInfo, dict):
            projectNameEdit.setText(basicInfo['project_name'])
            projectTypeEdit.setText(basicInfo['project_type'])
            position_x_edit.setText(str(basicInfo['position_x']))
            position_y_edit.setText(str(basicInfo['position_y']))

        basicInfoWidgetGrid.addWidget(projectNameLabel, 1, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(projectNameEdit, 1, 1, 1, 1)
        basicInfoWidgetGrid.addWidget(projectTypeLabel, 2, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(projectTypeEdit, 2, 1, 1, 1)
        basicInfoWidgetGrid.addWidget(position_x_label, 3, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(position_x_edit, 3, 1, 1, 1)
        basicInfoWidgetGrid.addWidget(position_y_label, 4, 0, 1, 1)
        basicInfoWidgetGrid.addWidget(position_y_edit, 4, 1, 1, 1)

        basicInfoWidget = QtWidgets.QWidget()
        basicInfoWidget.setLayout(basicInfoWidgetGrid)

        VBox = QtWidgets.QVBoxLayout()
        VBox.addWidget(basicInfoWidget)

        HFSS_VBox = QtWidgets.QVBoxLayout()

        buttonWidget = QtWidgets.QWidget()
        button_HBox = QtWidgets.QHBoxLayout()
        addButton = QtWidgets.QPushButton("add")
        addButton.clicked.connect(self.add_report)
        deleteButton = QtWidgets.QPushButton("delete")
        deleteButton.clicked.connect(self.delete_report)
        saveButton = QtWidgets.QPushButton("save")
        saveButton.clicked.connect(self.save_report)
        button_HBox.addWidget(addButton)
        button_HBox.addWidget(deleteButton)
        button_HBox.addWidget(saveButton)
        buttonWidget.setLayout(button_HBox)

        HFSS_VBox.addWidget(buttonWidget)

        self.report_table_widget = HFSS_ReportTableWidget(self)
        HFSS_VBox.addWidget(self.report_table_widget)

        exportWidget = QtWidgets.QWidget()
        export_HBox = QtWidgets.QHBoxLayout()
        exportDirNameLabel = QtWidgets.QLabel("export directory")
        self.exportDirNameEdit = QtWidgets.QLineEdit()
        export_HBox.addWidget(exportDirNameLabel)
        export_HBox.addWidget(self.exportDirNameEdit)
        exportWidget.setLayout(export_HBox)

        HFSS_VBox.addWidget(exportWidget)

        exportDirBrowserButton = QtWidgets.QPushButton("Browse")
        exportDirBrowserButton.clicked.connect(self.set_export_dirctory)

        HFSS_VBox.addWidget(exportDirBrowserButton)

        HFSS_OutputWidget = QtWidgets.QWidget()
        HFSS_OutputWidget.setLayout(HFSS_VBox)
        VBox.addWidget(HFSS_OutputWidget)

        if "export dirction" in settingInfo.keys():
            self.exportDirNameEdit.setText(settingInfo["export dirction"])

        if 'report info list' in settingInfo.keys():
            num_item = len(settingInfo["report info list"])
            self.report_table_widget.setRowCount(num_item)

            for index in range(num_item):
                # 1. 索引号
                item = QtWidgets.QTableWidgetItem()
                item.setText(settingInfo["report info list"][index]["id"])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.report_table_widget.setItem(index, 0, item)

                # 2. 复选框
                checkBox = QtWidgets.QCheckBox()  # 1.实例复选框
                if settingInfo["report info list"][index]["user define"] == True:
                    checkBox.setCheckState(QtCore.Qt.CheckState.Checked)
                else:
                    checkBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
                hLayout = QtWidgets.QHBoxLayout()  # 2.实例一个水平布局
                hLayout.addWidget(checkBox)  # 在布局里添加checkBox
                hLayout.setAlignment(checkBox, QtCore.Qt.AlignmentFlag.AlignCenter)  # 3.在布局里居中设置
                widget = QtWidgets.QWidget()  # 4.实例化一个QWidget
                widget.setLayout(hLayout)  # 5.在QWidget放置布局
                self.report_table_widget.setCellWidget(index, 1, widget)

                # 3. 报告的名称
                item = QtWidgets.QTableWidgetItem()
                item.setText(settingInfo["report info list"][index]["report name"])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.report_table_widget.setItem(index, 2, item)

                # 4. 表达式
                item = QtWidgets.QTableWidgetItem()
                item.setText(settingInfo["report info list"][index]["expression"])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.report_table_widget.setItem(index, 3, item)

                # 5. 解释器
                item = QtWidgets.QTableWidgetItem()
                item.setText(settingInfo["report info list"][index]["solution"])
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.report_table_widget.setItem(index, 4, item)

        self.setLayout(VBox)

    def __del__(self):
        print("FormatInfoWidget delete")

    def add_report(self):
        hfss_adapter = projectManagerSingleton.get_adapter(project_name=self.project_name)
        hfss_report_widget = Report_Widget(adapter=hfss_adapter)
        hfss_report_widget.new_report_notifier.connect(self.set_report_information)
        hfss_report_widget.show()

    def set_report_information(self, report_information):
        print(report_information)

        num_item = self.report_table_widget.rowCount()
        self.report_table_widget.setRowCount(num_item + 1)

        Idx = num_item
        # 1. 索引号
        item = QtWidgets.QTableWidgetItem(str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 0, item)

        # 2. 复选框
        checkBox = QtWidgets.QCheckBox()  # 1.实例复选框
        if report_information['category'] == 'Output Variables':
            checkBox.setCheckState(QtCore.Qt.CheckState.Checked)  # 复选框默认选择
        else:
            checkBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        hLayout = QtWidgets.QHBoxLayout()  # 2.实例一个水平布局
        hLayout.addWidget(checkBox)  # 在布局里添加checkBox
        hLayout.setAlignment(checkBox, QtCore.Qt.AlignmentFlag.AlignCenter)  # 3.在布局里居中设置
        widget = QtWidgets.QWidget()  # 4.实例化一个QWidget
        widget.setLayout(hLayout)  # 5.在QWidget放置布局
        self.report_table_widget.setCellWidget(Idx, 1, widget)

        # 3. 报告的名称
        item = QtWidgets.QTableWidgetItem(report_information['expression'])
        item.setText(report_information['expression'])
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 2, item)

        # 4. 表达式
        item = QtWidgets.QTableWidgetItem(report_information['expression'])
        item.setText(report_information['expression'])
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 3, item)

        # 5. 解释器
        item = QtWidgets.QTableWidgetItem(report_information['solution'])
        item.setText(report_information['solution'])
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 4, item)

    def add_report_test(self):
        # 设置需要导出的报告名称
        num_item = self.report_table_widget.rowCount()
        self.report_table_widget.setRowCount(num_item + 1)

        Idx = num_item
        # 1. 索引号
        item = QtWidgets.QTableWidgetItem(str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 0, item)

        # 2. 复选框
        checkBox = QtWidgets.QCheckBox()  # 1.实例复选框
        checkBox.setCheckState(QtCore.Qt.CheckState.Checked)  # 复选框默认选择
        hLayout = QtWidgets.QHBoxLayout()  # 2.实例一个水平布局
        hLayout.addWidget(checkBox)  # 在布局里添加checkBox
        hLayout.setAlignment(checkBox, QtCore.Qt.AlignmentFlag.AlignCenter)  # 3.在布局里居中设置
        widget = QtWidgets.QWidget()  # 4.实例化一个QWidget
        widget.setLayout(hLayout)  # 5.在QWidget放置布局
        self.report_table_widget.setCellWidget(Idx, 1, widget)

        # 3. 报告的名称
        item = QtWidgets.QTableWidgetItem("report_" + str(Idx + 1))
        item.setText("report_" + str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 2, item)

        # 4. 表达式
        item = QtWidgets.QTableWidgetItem("expression_" + str(Idx + 1))
        item.setText("expression_" + str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 3, item)

        # 5. 解释器
        item = QtWidgets.QTableWidgetItem("solution_" + str(Idx + 1))
        item.setText("solution_" + str(Idx + 1))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.report_table_widget.setItem(Idx, 4, item)

    def delete_report(self):
        print("delete report")

    def save_report(self):
        # 添加完需要导出的报告之后要点击保存
        report_info_list = list()
        num_item = self.report_table_widget.rowCount()
        for index in range(num_item):
            item_info = dict()

            item = self.report_table_widget.item(index, 0)
            item_info["id"] = item.text()

            cellWidget = self.report_table_widget.cellWidget(index, 1)
            for i in range(cellWidget.layout().count()):
                widget = cellWidget.layout().itemAt(i).widget()
                if isinstance(widget, QtWidgets.QCheckBox):
                    item_info["user define"] = True if widget.checkState() == QtCore.Qt.CheckState.Checked else False

            item = self.report_table_widget.item(index, 2)
            item_info["report name"] = item.text()

            item = self.report_table_widget.item(index, 3)
            item_info["expression"] = item.text()

            item = self.report_table_widget.item(index, 4)
            item_info["solution"] = item.text()

            report_info_list.append(item_info)

        info = dict()
        info["start_setting"] = dict()
        info["start_setting"]["report info list"] = report_info_list
        self.format_info_notifier.emit(info)

    def set_export_dirctory(self):
        export_dirctory = QtWidgets.QFileDialog.getExistingDirectory(self, "选取文件夹", "./")
        self.exportDirNameEdit.setText(export_dirctory)
        info = dict()
        info["start_setting"] = dict()
        info["start_setting"]["export dirction"] = export_dirctory
        self.format_info_notifier.emit(info)

class HFFS2InterconectConvertWidget(QtWidgets.QWidget):
    format_setting_notifier = QtCore.pyqtSignal(dict)
    def __init__(self, parent=None, connect_info=None):
        super().__init__(parent)

        self.connect_info = connect_info
        self.path_uuid = self.connect_info["uuid"]

        VBox = QtWidgets.QVBoxLayout()
        if 'start_item' in self.connect_info.keys():
            contentWidget = HFSS_Output_FormatInfoWidget(basicInfo=self.connect_info['start_item'],
                                                         settingInfo=self.connect_info['start_setting'],
                                                         parent=self)
            contentWidget.format_info_notifier.connect(self.update_format_setting)
            basicInfoWidget = CollapsibleWidget(contextWidget=contentWidget,
                                                parent=self,
                                                title="start item")
            VBox.addWidget(basicInfoWidget)
        if 'end_item' in self.connect_info.keys():
            contentWidget = Interconnect_Input_FormatInfoWidget(basicInfo=self.connect_info['end_item'],
                                                                settingInfo=self.connect_info['end_setting'],
                                                                parent=self)
            contentWidget.format_info_notifier.connect(self.update_format_setting)
            basicInfoWidget = CollapsibleWidget(contextWidget=contentWidget,
                                                parent=self,
                                                title="end item")
            VBox.addWidget(basicInfoWidget)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        VBox.addWidget(spacer)
        self.setLayout(VBox)

    def update_format_setting(self, info):
        info["uuid"] = self.path_uuid
        self.format_setting_notifier.emit(info)

class Comsol2InterconectConvertWidget(QtWidgets.QWidget):
    format_setting_notifier = QtCore.pyqtSignal(dict)
    def __init__(self, parent=None, connect_info=None):
        super().__init__(parent)

        self.connect_info = connect_info
        self.path_uuid = self.connect_info["uuid"]

        VBox = QtWidgets.QVBoxLayout()
        if 'start_item' in self.connect_info.keys():
            contentWidget = Comsol_Input_FormatInfoWidget(basicInfo=self.connect_info['start_item'],
                                                          settingInfo=self.connect_info['start_setting'],
                                                          parent=self)
            contentWidget.format_info_notifier.connect(self.update_format_setting)
            basicInfoWidget = CollapsibleWidget(contextWidget=contentWidget,
                                                parent=self,
                                                title="start item")
            VBox.addWidget(basicInfoWidget)
        if 'end_item' in self.connect_info.keys():
            contentWidget = Interconnect_Input_FormatInfoWidget(basicInfo=self.connect_info['end_item'],
                                                                settingInfo=self.connect_info['end_setting'],
                                                                parent=self)
            contentWidget.format_info_notifier.connect(self.update_format_setting)
            basicInfoWidget = CollapsibleWidget(contextWidget=contentWidget,
                                                parent=self,
                                                title="end item")
            VBox.addWidget(basicInfoWidget)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        VBox.addWidget(spacer)
        self.setLayout(VBox)

    def update_format_setting(self, info):
        info["uuid"] = self.path_uuid
        self.format_setting_notifier.emit(info)

class FormatConvertWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vbox_layout = QtWidgets.QVBoxLayout()
        self.vbox_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox_layout)

        # 用于保存路径的信息
        self.path_info = dict()

    def setConvertWidget(self, connect_info):

        path_uuid = connect_info["uuid"]
        # 更新数据
        if path_uuid in self.path_info.keys():
            connect_info = self.path_info[path_uuid]
        else:
            connect_info["start_setting"] = dict()
            connect_info["start_setting"]["project type"] = connect_info["start_item"]["project_type"]
            connect_info["start_setting"]["project name"] = connect_info["start_item"]["project_name"]
            connect_info["end_setting"] = dict()
            connect_info["end_setting"]["project_type"] = connect_info["end_item"]["project_type"]
            connect_info["end_setting"]["project name"] = connect_info["end_item"]["project_name"]
            self.path_info[path_uuid] = connect_info

        widget_count = self.vbox_layout.count()
        if widget_count != 0:
            for index in range(widget_count - 1, -1, -1):
                widget_item = self.vbox_layout.itemAt(index)
                self.vbox_layout.removeItem(widget_item)
                widget_item.widget().deleteLater()

        if connect_info["start_item"]["project_type"] == "HFSS" and connect_info["end_item"]["project_type"] == "Interconnect":
            hfss2Interconect = HFFS2InterconectConvertWidget(self, connect_info)
            hfss2Interconect.format_setting_notifier.connect(self.update_path_info)
            self.vbox_layout.addWidget(hfss2Interconect)
        elif connect_info["start_item"]["project_type"] == "Comsol" and connect_info["end_item"]["project_type"] == "Interconnect":
            comsol2Interconect = Comsol2InterconectConvertWidget(self, connect_info)
            comsol2Interconect.format_setting_notifier.connect(self.update_path_info)
            self.vbox_layout.addWidget(comsol2Interconect)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.vbox_layout.addWidget(spacer)

    def update_path_info(self, info):
        logging.info(info)
        path_uuid = info["uuid"]
        for key, value in info.items():
            if "uuid" == key:
                continue
            if "start_setting" == key:
                for sub_key, sub_value in value.items():
                    self.path_info[path_uuid]["start_setting"][sub_key] = sub_value
            if "end_setting" == key:
                for sub_key, sub_value in value.items():
                    self.path_info[path_uuid]["end_setting"][sub_key] = sub_value

    def get_path_info(self, uuid):
        if uuid in self.path_info.keys():
            return self.path_info[uuid]
        else:
            logging.warning("uuid: %s can not find in path info" % uuid)