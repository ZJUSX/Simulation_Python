from PyQt5 import QtWidgets, QtGui, QtCore
import logging
import queue
import CenterWidget, ImportWidget, PropertyWidget, FormatConvertWidget, SampleWidget
from ProjectManager import projectManagerSingleton

class UIMainWindow():

    def setUI(self, window: QtWidgets.QMainWindow) -> None:
        """设置UI界面"""

        self.window = window

        self.window.setWindowIcon(QtGui.QIcon("icons/tool.png"))
        self.window.setWindowTitle("Combine Simulation")
        self.window.setGeometry(120, 120, 1700, 900)

        # 仿真软件栏，用于展示各类仿真软件
        simulationBar = QtWidgets.QToolBar("Simulation Software Bar")
        self.window.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, simulationBar)
        simulationBar.setMovable(False)
        simulationBar.setMinimumHeight(60)
        simulationBar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        self.hfssAction = QtWidgets.QAction(QtGui.QIcon("icons/ElectronicsDesktop.ico"), "HFSS", self.window)
        simulationBar.addAction(self.hfssAction)

        self.comsolAction = QtWidgets.QAction(QtGui.QIcon("icons/comsol_32.png"), "Comsol", self.window)
        simulationBar.addAction(self.comsolAction)

        self.interconnectAction = QtWidgets.QAction(QtGui.QIcon("icons/interconnect_project.ico"), "Interconnect", self.window)
        simulationBar.addAction(self.interconnectAction)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)  # 按钮添加到最右侧
        simulationBar.addWidget(spacer)

        # 显示仿真样例
        self.sampleAction = QtWidgets.QAction(QtGui.QIcon("icons/sample.png"), "Samples", self.window)
        simulationBar.addAction(self.sampleAction)

        '''
        # 用户注册信息
        self.userAction = QtWidgets.QAction(QtGui.QIcon("icons/user.png"), "User", self.window)
        simulationBar.addAction(self.userAction)

        # 显示版本信息
        self.versionAction = QtWidgets.QAction(QtGui.QIcon("icons/version.png"), "About version", self.window)
        simulationBar.addAction(self.versionAction)

        # 退出按钮
        self.exitAction = QtWidgets.QAction(QtGui.QIcon("icons/exit.png"), "Exit", self.window)
        simulationBar.addAction(self.exitAction)
        '''

        # 工具栏
        self.drawLineAction = QtWidgets.QAction(QtGui.QIcon("icons/line.png"), "draw line")
        self.drawLineAction.setStatusTip("Create line connect component")
        self.drawLineAction.setObjectName("connect_line")

        # 运行仿真栏
        self.runSimulationAction = QtWidgets.QAction(QtGui.QIcon("icons/run.png"), "run simulation")
        self.runSimulationAction.setStatusTip("Run Simulation")
        self.runSimulationAction.setObjectName("run_simulation")

        self.window.addToolBarBreak()  # 显示换行
        self.toolbar = self.window.addToolBar("Options")
        self.window.addToolBarBreak(QtCore.Qt.ToolBarArea.TopToolBarArea)
        self.toolbar.setMovable(False)

        self.toolbar.addAction(self.drawLineAction)
        self.toolbar.addAction(self.runSimulationAction)
        # 用于设置action样式
        self.toolbar.widgetForAction(self.drawLineAction).setObjectName(self.drawLineAction.objectName())

        # 中间位置窗口用于规划联合仿真
        self.centerWidget = CenterWidget.CenterWidget()
        self.centerWidget.project_clicked_notifier.connect(self.show_information)
        self.window.setCentralWidget(self.centerWidget)

        # 当鼠标点击空白区域时显示空的窗口
        self.emptyDockWin = QtWidgets.QDockWidget()
        self.emptyDockWin.setWindowTitle("EMPTY")
        self.emptyDockWin.setAcceptDrops(False)
        self.emptyDockWin.setMinimumWidth(500)
        self.emptyDockWin.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.emptyDockWin.setVisible(True)
        self.window.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.emptyDockWin)

        # 右侧用于展示仿真软件的参数列表
        self.propertyWin = QtWidgets.QDockWidget()
        self.propertyWin.setWindowTitle("PROPERTY")
        self.propertyWin.setAcceptDrops(False)
        self.propertyWin.setMinimumWidth(500)
        self.propertyWin.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.propertyWin.setVisible(False)
        self.window.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.propertyWin)

        # 右侧用于设置仿真结果格式
        self.formatSettingWin = QtWidgets.QDockWidget()
        self.formatSettingWin.setWindowTitle("FORMAT SETTING")
        self.formatSettingWin.setAcceptDrops(False)
        self.formatSettingWin.setMinimumWidth(500)
        self.formatSettingWin.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.formatSettingWin.setVisible(False)
        self.window.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.formatSettingWin)
        self.formatConvertWidget = FormatConvertWidget.FormatConvertWidget()
        self.formatSettingWin.setWidget(self.formatConvertWidget)

        self.triggered_clicked()

    def triggered_clicked(self):

        self.hfssAction.triggered.connect(lambda x: self.showImportWidget("HFSS"))
        self.comsolAction.triggered.connect(lambda x: self.showImportWidget("Comsol"))
        self.interconnectAction.triggered.connect(lambda x: self.showImportWidget("Interconnect"))

        self.sampleAction.triggered.connect(self.showSamplesWidget)
        # self.versionAction.triggered.connect(self.showVersionWidget)

        self.drawLineAction.triggered.connect(self.draw_connect_line)
        self.runSimulationAction.triggered.connect(self.run_simulation)

    def showImportWidget(self, type):

        importWidget = ImportWidget.ImportWidget(self, type)
        '''关闭弹窗才能操作主窗口'''
        importWidget.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        importWidget.show()

    def show_information(self, value):
        if len(value) == 0:
            self.display_empty_dock_win()
        else:
            item_info = value
            if item_info["type"] == "path":
                self.show_format(item_info)
            elif item_info["type"] == "project":
                self.show_property(item_info)

    def show_property(self, project_info):
        self.display_property()
        propertyWidget = PropertyWidget.PropertyWidget(self, project_info)
        propertyWidget.setMinimumHeight(600)
        propertyWidget.setMaximumHeight(600)
        # propertyWidget.property_changed_notifier.connect(self.set_project_property)
        self.propertyWin.setWidget(propertyWidget)

    def show_format(self, connect_info):
        self.display_format()
        # formatWidget = FormatConvertWidget.FormatWidget(self, connect_info)
        # self.formatSettingWin.setWidget(formatWidget)
        self.formatConvertWidget.setConvertWidget(connect_info)

    # def set_project_property(self, current_property):
    #     logging.info(current_property)
    #     self.centerWidget.setGraphicPDKProperty(current_property)

    def draw_connect_line(self):
        if self.centerWidget.draw_line_mode == True:
            logging.info("cancel draw component connect line")
            self.centerWidget.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            self.centerWidget.draw_line_mode = False
            self.toolbar.setStyleSheet("QToolButton#connect_line { background:white }")
        elif self.centerWidget.draw_line_mode == False:
            logging.info("enable draw component connect line")
            self.centerWidget.setCursor(QtCore.Qt.CursorShape.CrossCursor)
            self.centerWidget.draw_line_mode = True
            self.toolbar.setStyleSheet("QToolButton#connect_line { background:LightGray }")

    def run_simulation(self):
        logging.info("run simulation")
        run_item_order = self.centerWidget.get_run_item_order()
        if run_item_order is None:
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning', 'No project can be simulated !')
            msg_box.exec_()
            return

        task_q = queue.Queue()
        for item in run_item_order:
            if item["type"] == "project":
                prj_info = dict()
                prj_info["type"] = item["type"]
                prj_info["project name"] = item["project name"]
                task_q.put(prj_info)
            elif item["type"] == "path":
                path_uuid = item["path uuid"]
                path_info = self.formatConvertWidget.get_path_info(path_uuid)
                if path_info == None:
                    # path 未设置告警
                    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning', 'path not set !')
                    msg_box.exec_()
                    return
                elif len(path_info["start_setting"]) == 0:
                    # path 输入端未设置告警
                    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning', 'path input not set !')
                    msg_box.exec_()
                    return
                elif len(path_info["end_setting"]) == 0:
                    # path 输出端未设置告警
                    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning', 'path output not set !')
                    msg_box.exec_()
                    return

                path_setting = dict()
                path_setting["type"] = "path"
                path_setting["path uuid"] = path_uuid
                path_setting["start setting"] = path_info["start_setting"]
                path_setting["end setting"] = path_info["end_setting"]
                task_q.put(path_setting)

        projectManagerSingleton.run_simulation(task_q)


    def display_property(self):
        # 展示属性窗口
        self.propertyWin.setVisible(True)
        self.formatSettingWin.setVisible(False)
        self.emptyDockWin.setVisible(False)

    def display_format(self):
        # 展示格式转换窗口
        self.propertyWin.setVisible(False)
        self.formatSettingWin.setVisible(True)
        self.emptyDockWin.setVisible(False)

    def display_empty_dock_win(self):
        # 展示空白窗口
        self.propertyWin.setVisible(False)
        self.formatSettingWin.setVisible(False)
        self.emptyDockWin.setVisible(True)

    def showSamplesWidget(self):
        # 展示案例窗口
        sampleWidget = SampleWidget.SamplesWidget(self.window)
        # 关闭弹窗才能操作主窗口
        sampleWidget.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        sampleWidget.show()

    # def showVersionWidget(self):
    #     # 跳转到软件版本信息页面
    #     versionWidget = VersionWidget.VersionWidget(self.window)
    #     # 关闭弹窗才能操作主窗口
    #     versionWidget.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
    #     versionWidget.show()
