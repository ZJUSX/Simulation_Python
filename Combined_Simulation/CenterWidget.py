from __future__ import annotations

import os
import sys
import uuid
import logging
from PyQt5 import QtWidgets, QtCore, QtGui

import SchemeGraphics
from ProjectManager import projectManagerSingleton

class CenterWidget(QtWidgets.QWidget):

    project_clicked_notifier = QtCore.pyqtSignal(dict)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.sdlTabCount = 0
        self.__draw_line_mode = False
        self.initUI()
        self.addSchemeTabWidget()

    @property
    def draw_line_mode(self):
        return self.__draw_line_mode

    @draw_line_mode.setter
    def draw_line_mode(self, value):
        if isinstance(value, bool):
            self.__draw_line_mode = value
            return
        raise TypeError

    def initUI(self):

        # 用于规划仿真
        self.schedulerTabWidget = QtWidgets.QTabWidget(self)
        self.schedulerTabWidget.setContentsMargins(0, 0, 0, 0)
        self.schedulerTabWidget.setWindowTitle("scheduler")
        self.schedulerTabWidget.setVisible(True)

        # self.viewerTabWidget = QtWidgets.QTabWidget(self)
        # self.viewerTabWidget.setContentsMargins(0, 0, 0, 0)
        # self.viewerTabWidget.setWindowTitle("Layout Viewer")
        # self.viewerTabWidget.setVisible(True)

        self.centerSplitterWidget = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.centerSplitterWidget.addWidget(self.schedulerTabWidget)
        # self.centerSplitterWidget.addWidget(self.viewerTabWidget)
        self.centerSplitterWidget.setHandleWidth(0)

        self.hLayout = QtWidgets.QHBoxLayout()
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout.addWidget(self.centerSplitterWidget)
        self.setLayout(self.hLayout)

    def addSchemeTabWidget(self):
        self.schemeScene = SchemeGraphics.SchemeGraphicsScene(self)
        self.schemeScene.graphicsItem_clicked_notifier.connect(self.emit_project_info)
        self.schemeView = SchemeGraphics.SchemeGraphicsView(self.schemeScene, self)
        self.schedulerTabWidget.addTab(self.schemeView, QtGui.QIcon("icons/draw.png"), self.get_scheme_tab_default_name())

        projectManagerSingleton.project_manager_notifier.connect(self.add_project)

    def add_project(self, project_name, project_type):
        logging.info("add %s project icon" % project_name)

        project_info = dict()
        project_info["project_name"] = project_name
        project_info["project_type"] = project_type
        project_info["position_x"] = 0
        project_info["position_y"] = 0
        project_info["uuid"] = uuid.uuid4().hex #创建图元唯一标识

        pic_path = os.path.join(os.getcwd(), "icons")
        if project_type == "HFSS":
            project_info["pic_path"] = os.path.join(pic_path, "HFSS.png")
        elif project_type == "Comsol":
            project_info["pic_path"] = os.path.join(pic_path, "Comsol.png")
        elif project_type == "Interconnect":
            project_info["pic_path"] = os.path.join(pic_path, "Interconnect.png")

        position_x, position_y = self.init_item_position()
        logging.info("new project initial position(%s, %s)" % (position_x, position_y))

        item = SchemeGraphics.SchemeGraphicsItem(project_info=project_info, view_parent=self.schemeView)
        item.setPos(QtCore.QPointF(position_x, position_y))
        self.schemeScene.add_component(item)

    def init_item_position(self):
        search_x = 0.0
        search_y = 0.0
        search_w = 240
        search_h = 120

        while True:
            topleft = QtCore.QPointF(search_x - search_w / 2, search_y - search_h / 2)
            search_size = QtCore.QSizeF(search_w, search_h)
            rect = QtCore.QRectF(topleft, search_size)

            item_list = self.schemeScene.items(rect)
            # print(item_list)
            if 0 == len(item_list):
                break
            else:
                search_x += search_w / 2
                search_y -= search_h / 2

        return search_x, search_y

    def emit_project_info(self, info: dict):
        if len(info) != 0:
            project_info = info
            if "path" == project_info["type"]:
                logging.info(project_info)
            elif "project" == project_info["type"]:
                project_type = project_info["project_type"]
                project_name = project_info["project_name"]
                if "HFSS" == project_type or "Comsol" == project_type:
                    variables = projectManagerSingleton.get_variables(project_name)
                    project_info["parameters"] = variables
                elif "Interconnect" == project_type:
                    elements = projectManagerSingleton.get_elements(project_name)
                    project_info["elements"] = elements

            self.project_clicked_notifier.emit(project_info)
        else:
            self.project_clicked_notifier.emit(info)

    def get_scheme_tab_default_name(self) -> str:
        '''获取原理图标签页默认标签名称'''
        self.sdlTabCount += 1
        tabDefaultName = 'New Tab %d' % self.sdlTabCount
        return tabDefaultName

    def get_run_item_order(self):
        component_list = self.schemeScene.get_component_list()
        path_list = self.schemeScene.get_path_list()

        if 0 == len(path_list) and 0 == len(component_list):
            logging.warning("item is empty can not run simulation")
            return

        # 获取component 和 path 后进行拓扑排序
        run_item_order_l = list()
        indegree_d = dict()  # 计算模块的入度
        import queue
        zero_indegreee_q = queue.Queue()  # 维持一个入度为0的队列

        for componet in component_list:
            indegree_d[componet.project_name] = 0

        for path in path_list:
            if path.wraped_path.end_item.project_name in indegree_d.keys():
                indegree_d[path.wraped_path.end_item.project_name] += 1
            else:
                logging.error("path without end item")
                return

        for key, value in indegree_d.items():
            if value == 0:
                zero_indegreee_q.put(key)

        while(zero_indegreee_q.empty() == False):
            item = zero_indegreee_q.get()

            prj_info = dict()
            prj_info["type"] = "project"
            prj_info["project name"] = item
            run_item_order_l.append(prj_info)
            for path in path_list:
                if item == path.wraped_path.start_item.project_name:
                    indegree_d[path.wraped_path.end_item.project_name] -= 1
                    if indegree_d[path.wraped_path.end_item.project_name] == 0:
                        zero_indegreee_q.put(path.wraped_path.end_item.project_name)

                    path_info = dict()
                    path_info["type"] = "path"
                    path_info["path uuid"] = path.wraped_path.path_uuid
                    run_item_order_l.append(path_info)

        logging.info("simulation order: %s" % run_item_order_l)
        return run_item_order_l




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    centerWidget = CenterWidget()
    centerWidget.show()
    sys.exit(app.exec_())