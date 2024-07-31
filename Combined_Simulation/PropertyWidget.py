from __future__ import annotations

import sys
import traceback
import logging
from typing import Union

from PyQt5 import QtWidgets, QtCore, QtGui

class BasicInfoWidget(QtWidgets.QWidget):
    def __init__(self, basicInfo: Union[dict, None] = None, parent=None):
        super().__init__(parent)

        grid = QtWidgets.QGridLayout()
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

        grid.addWidget(projectNameLabel, 1, 0, 1, 1)
        grid.addWidget(projectNameEdit, 1, 1, 1, 1)
        grid.addWidget(projectTypeLabel, 2, 0, 1, 1)
        grid.addWidget(projectTypeEdit, 2, 1, 1, 1)
        grid.addWidget(position_x_label, 3, 0, 1, 1)
        grid.addWidget(position_x_edit, 3, 1, 1, 1)
        grid.addWidget(position_y_label, 4, 0, 1, 1)
        grid.addWidget(position_y_edit, 4, 1, 1, 1)

        # spacer = QtWidgets.QWidget()
        # spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # grid.addWidget(spacer)
        self.setLayout(grid)

class VariablesTableWidget(QtWidgets.QTableWidget):
    def __init__(self, variables_info: dict, parent=None):
        super().__init__(parent)
        self.variables = variables_info

        self.initUI()

    def initUI(self):
        self.setMinimumHeight(500)
        self.setMaximumHeight(500)
        self.setColumnCount(3)

        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 150)
        self.setColumnWidth(2, 300)

        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("Idx")
        self.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("variable")
        self.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("expression")
        self.setHorizontalHeaderItem(2, item)

        self.verticalHeader().setVisible(False)  # 索引栏不可见
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # 设置选择行为，按行选择
        self.setStyleSheet("selection-background-color:rgb(255,209,128)")  # 设置选中行背景颜色

        num = len(self.variables)
        self.setRowCount(num + 1)
        Idx = 0
        for key, value in self.variables.items():
            item = QtWidgets.QTableWidgetItem(str(Idx + 1))
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.setItem(Idx, 0, item)

            item = QtWidgets.QTableWidgetItem(key)
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.setItem(Idx, 1, item)

            item = QtWidgets.QTableWidgetItem(value)
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.setItem(Idx, 2, item)

            Idx += 1


# class ParametersWidget(QtWidgets.QWidget):
#     parametersChangedSignal = QtCore.pyqtSignal(dict)
#
#     def __init__(self, parametersInfo: Union[dict, None], parent=None):
#         super().__init__(parent)
#
#         grid = QtWidgets.QGridLayout()
#
#         if isinstance(parametersInfo, dict):
#             lineNum = 1
#             for key, value in parametersInfo.items():
#                 keyLabel = QtWidgets.QLabel(key)
#                 keyLabel.setObjectName(key + '_label')
#
#                 valueEdit = QtWidgets.QLineEdit(self)
#                 valueEdit.setText(str(value))
#                 valueEdit.textChanged.connect(self.textChanged)
#                 valueEdit.setObjectName(key)
#
#                 grid.addWidget(keyLabel, lineNum, 0)
#                 grid.addWidget(valueEdit, lineNum, 1)
#                 lineNum += 1
#
#         self.setLayout(grid)

    def textChanged(self, newValue):
        editObj = self.sender()
        parameter = dict()
        parameter[editObj.objectName()] = newValue
        data = dict()
        data['parameters'] = parameter
        logging.info(data)
        self.parametersChangedSignal.emit(data)

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

class ElementCollapsibleWidget(QtWidgets.QWidget):
    element_clicked_notifier = QtCore.pyqtSignal(str)
    def __init__(self, contextWidget: QtWidgets.QWidget, parent=None, element_name=""):
        super().__init__(parent)

        self.element_name = element_name
        self.collapsibleButton = QtWidgets.QToolButton(self)
        self.collapsibleButton.setText(element_name)
        self.collapsibleButton.setCheckable(True)
        self.collapsibleButton.setChecked(True)
        self.collapsibleButton.setStyleSheet("QToolButton { border: none; }")
        self.collapsibleButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.collapsibleButton.setArrowType(QtCore.Qt.ArrowType.RightArrow)
        self.collapsibleButton.pressed.connect(self.onPressed)

        self.contentArea = contextWidget
        self.contentArea.setVisible(False)
        VBox = QtWidgets.QVBoxLayout(self)
        VBox.setSpacing(0)
        VBox.setContentsMargins(0, 0, 0, 0)
        VBox.addWidget(self.collapsibleButton)
        VBox.addWidget(self.contentArea)
        self.setLayout(VBox)

    def onPressed(self):
        checked = self.collapsibleButton.isChecked()
        logging.info(checked)
        logging.info(self.collapsibleButton.arrowType())
        # self.collapsibleButton.setArrowType(QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow)
        if checked:
            self.collapsibleButton.setArrowType(QtCore.Qt.ArrowType.DownArrow)
            self.element_clicked_notifier.emit(self.element_name)
            self.contentArea.setVisible(True)
        else:
            self.collapsibleButton.setArrowType(QtCore.Qt.ArrowType.RightArrow)
            self.contentArea.setVisible(False)

class PropertyListWidget(QtWidgets.QListWidget):
    def __init__(self):
        super().__init__()

class PropertyWidget(QtWidgets.QWidget):

    property_changed_notifier = QtCore.pyqtSignal(dict)
    # element_clicked_notifier = QtCore.pyqtSignal(dict) # 这两个信号槽用于修改属性参数，暂时用不到

    def __init__(self, parent=None, project_info=None):
        super().__init__(parent)

        """
        componentInfo 字段信息，先用dict以后用yaml或json替换
        {
            'project_name': 'Interconnect_Project_1', 
            'project_type': 'Interconnect', 
            'position_x': 0, 
            'position_y': 0, 
            'uuid': '06504550030e425588afcf64939e0ece', 
            'pic_path': 'F:\\tmp\\CombinedProject\\CombinedSimulation\\icons\\Interconnect.png'
        }
        """

        self.project_info = self.transInfo(project_info)
        logging.info(self.project_info)
        self.setupUI()

    def setupUI(self):
        VBox = QtWidgets.QVBoxLayout()

        saveButton = QtWidgets.QPushButton("save")
        saveButton.clicked.connect(self.saveFile)
        VBox.addWidget(saveButton)

        if 'basic_info' in self.project_info.keys():
            contentWidget = BasicInfoWidget(basicInfo=self.project_info['basic_info'], parent=self)
            basicInfoWidget = CollapsibleWidget(contextWidget=contentWidget, parent=self, title="basic info")
            VBox.addWidget(basicInfoWidget)
        if 'parameters' in self.project_info.keys():
            contentWidget = VariablesTableWidget(variables_info=self.project_info['parameters'], parent=self)
            variablesWidget = CollapsibleWidget(contextWidget=contentWidget, parent=self, title="variables")
            VBox.addWidget(variablesWidget)
        if 'elements' in self.project_info.keys():
            for ele_name, property_list in self.project_info['elements'].items():
                # emptyWidget = QtWidgets.QWidget()
                property_list_widget = PropertyListWidget()
                for property_name in  property_list:
                    property_list_widget.addItem(property_name)
                elementWidget = ElementCollapsibleWidget(contextWidget=property_list_widget, parent=self, element_name=ele_name)
                VBox.addWidget(elementWidget)

            # contentWidget = ParametersWidget(parametersInfo=self.componentInfo['parameters'], parent=self)
            # contentWidget.parametersChangedSignal.connect(self.propertyChanged)
            # parametersWidget = CollapsibleWidget(contextWidget=contentWidget, parent=self, title="Parameters")
            # VBox.addWidget(parametersWidget)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        VBox.addWidget(spacer)
        self.setLayout(VBox)

    def saveFile(self):
        pass

    def propertyChanged(self, currentProperty: dict):
        currentProperty['uuid'] = self.componentInfo['auxiliaryInfo']['uuid']
        self.propertyChangedSignal.emit(currentProperty)

    def transInfo(self, project_info: dict):
        '''项目信息格式转换'''
        basic_info = dict()
        basic_info['project_name'] = project_info['project_name']
        basic_info['project_type'] = project_info['project_type']
        basic_info['position_x'] = project_info['position_x']
        basic_info['position_y'] = project_info['position_y']

        reform_project_info = dict()
        reform_project_info['basic_info'] = basic_info
        if basic_info["project_type"] == "HFSS" or basic_info["project_type"] == "Comsol":
            reform_project_info['parameters'] = project_info['parameters']
        elif basic_info["project_type"] == "Interconnect":
            reform_project_info['elements'] = project_info['elements']

        return reform_project_info


