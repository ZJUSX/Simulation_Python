from __future__ import annotations

import sys
import os
import logging
import json
import traceback

from PyQt5 import QtWidgets, QtCore, QtGui

class SamplesManager:
    def __init__(self, cfg_path=None):

        self.cfg_data = None
        self.cfg_path = os.path.join(os.getcwd(), "samples.json")
        if cfg_path is not None:
            self.cfg_path = cfg_path

        with open(self.cfg_path, 'r', encoding='utf-8') as file:
            self.cfg_data = json.load(file)

    def get_items(self):
        if self.cfg_data is None:
            return []
        return self.cfg_data


class SampleInfoWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.height = 400
        self.width = 600

        self.set_UI()

    def set_UI(self):
        self.setMinimumHeight(self.height)
        self.setMaximumHeight(self.height)
        self.setMinimumWidth(self.width)
        self.setMaximumWidth(self.width)
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)

        self.setWindowTitle("Sample")
        self.setWindowIcon(QtGui.QIcon("icons/sample.png"))
        self.setStyleSheet("background-color:lightgray;")

        self.set_layout()

    def set_layout(self):
        self.h_box = QtWidgets.QHBoxLayout()

        self.left_frame = QtWidgets.QFrame()  # 左侧QFrame
        # self.left_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)  # 显示边框
        self.left_frame.setMinimumWidth(self.width // 2 - 50)
        self.left_frame.setMaximumWidth(self.width // 2 - 50)
        self.left_frame.setStyleSheet("background-color:white;")
        # 左侧 QFrame 用于展示案例的文字信息
        self.information_label = QtWidgets.QLabel()
        font = QtGui.QFont("Times New Roman")
        font.setPointSize(14)
        self.information_label.setFont(font)
        self.information_label.setWordWrap(True)
        self.left_frame_v_box = QtWidgets.QVBoxLayout()
        self.left_frame_v_box.addWidget(self.information_label, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.left_frame.setLayout(self.left_frame_v_box)

        self.right_top = QtWidgets.QFrame()  # 右侧上方 QFrame
        # self.right_top.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.right_top.setMinimumHeight(self.height // 2)
        self.right_top.setMaximumHeight(self.height // 2)
        self.right_top.setMinimumWidth(self.width // 2)
        self.right_top.setMaximumWidth(self.width // 2)
        self.right_top.setStyleSheet("background-color:white;")
        # 右侧上方 QFrame 用来展示案例的图片
        self.image_label = QtWidgets.QLabel()
        self.right_top_v_box = QtWidgets.QVBoxLayout()
        self.right_top_v_box.addWidget(self.image_label)
        self.right_top.setLayout(self.right_top_v_box)

        self.right_bottom = QtWidgets.QFrame()  # 右侧下方 QFrame
        # self.right_bottom.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # 右侧下方 QFrame 用来展示案例所用到的软件
        self.logo_list_widget = QtWidgets.QListWidget()
        self.logo_list_widget.setGridSize(QtCore.QSize(50, 50))  # 设置每个item size
        self.logo_list_widget.setIconSize(QtCore.QSize(32, 32))
        self.logo_list_widget.setFlow(QtWidgets.QListView.LeftToRight)  # 设置横向list
        self.logo_list_widget.setWrapping(True)  # 设置换行
        self.logo_list_widget.setResizeMode(QtWidgets.QListView.Adjust)  # 窗口size 变化后重新计算列数
        self.logo_list_widget.setStyleSheet("QListWidget { border: none; }")
        self.right_bottom_v_box = QtWidgets.QVBoxLayout()
        self.right_bottom_v_box.addWidget(self.logo_list_widget)
        self.right_bottom.setLayout(self.right_bottom_v_box)

        splitter_right = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)  # 横向QSplitter
        splitter_right.addWidget(self.right_top)
        splitter_right.addWidget(self.right_bottom)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)  # 竖向QSplitter
        splitter.addWidget(self.left_frame)
        splitter.addWidget(splitter_right)

        self.h_box.addWidget(splitter)
        self.setLayout(self.h_box)

        # self.show_example()

    def show_example(self):
        self.information_label.setText("This is a modulator example.")
        self.image_label.setPixmap(QtGui.QPixmap("images/modulator.png").scaled(QtCore.QSize(300, 200)))

        item1 = QtWidgets.QListWidgetItem()
        item1.setIcon(QtGui.QIcon("icons/ElectronicsDesktop.ico"))
        self.logo_list_widget.addItem(item1)

        item2 = QtWidgets.QListWidgetItem()
        item2.setIcon(QtGui.QIcon("icons/comsol_32.png"))
        self.logo_list_widget.addItem(item2)

        item3 = QtWidgets.QListWidgetItem()
        item3.setIcon(QtGui.QIcon("icons/interconnect_project.ico"))
        self.logo_list_widget.addItem(item3)

    def set_message(self, example_name, example_image, description_text, dependence):
        self.setWindowTitle(example_name)
        self.information_label.setText(description_text)
        self.image_label.setPixmap(QtGui.QPixmap(example_image).scaled(QtCore.QSize(300, 200)))

        for depend_item in dependence:
            item = QtWidgets.QListWidgetItem()
            if "HFSS" == depend_item:
                item.setIcon(QtGui.QIcon("icons/ElectronicsDesktop.ico"))
            elif "Comsol" == depend_item:
                item.setIcon(QtGui.QIcon("icons/comsol_32.png"))
            elif "Interconnect" == depend_item:
                item.setIcon(QtGui.QIcon("icons/interconnect_project.ico"))

            self.logo_list_widget.addItem(item)

class SampleImageListWidget3333(QtWidgets.QListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.image_widget = None

        self.setWindowTitle("Samples")
        self.setWindowIcon(QtGui.QIcon("icons/sample.png"))
        self.resize(800, 600)

class SampleImageListWidget(QtWidgets.QListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.image_widget = None

        self.setWindowTitle("Samples")
        self.setWindowIcon(QtGui.QIcon("icons/sample.png"))
        self.resize(800, 600)

        # 设置每个item size
        self.setGridSize(QtCore.QSize(240, 200))
        # 设置横向list
        self.setFlow(QtWidgets.QListView.LeftToRight)
        # 设置换行
        self.setWrapping(True)
        # 窗口size 变化后重新计算列数
        self.setResizeMode(QtWidgets.QListView.Adjust)
        # 设置选择模式
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # self.setIconSize(QSize(200, 150))

    def load_items(self, sample_items: list):
        for item in sample_items:
            # print(item)
            img_item = SampleImageQListWidgetItem(sample_name=item["name"],
                                                  image_path=item["image path"],
                                                  dependence=item["dependence"],
                                                  description=item["description"])
            self.addItem(img_item)
            self.setItemWidget(img_item, img_item.group)
            # 刷新界面
            QtWidgets.QApplication.processEvents()

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:

        print("show sample information")
        selected_item = self.selectedItems()
        for item in selected_item:
            sample_name = item.get_sample_name()
            image_path = item.get_sample_image_path()
            description = item.get_sample_description()
            dependence = item.get_sample_dependence()
            self.image_widget = SampleInfoWidget()
            self.image_widget.set_message(example_name=sample_name,
                                          example_image=image_path,
                                          dependence=dependence,
                                          description_text=description)
            self.image_widget.show()
            break

        super().mouseDoubleClickEvent(event)

class WrapedGroupBox(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)  # 开启鼠标跟踪以便捕捉鼠标进入和离开事件
        self.setStyleSheet("QGroupBox { border: 1px solid transparent; }")  # 初始状态下边框透明

    def enterEvent(self, event):
        self.setStyleSheet("QGroupBox { border: 1px solid black; }")  # 鼠标进入时显示黑色边框
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("QGroupBox { border: 1px solid transparent; }")  # 鼠标离开时边框透明
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtCore.Qt.GlobalColor.white)
        super().paintEvent(event)

# 自定义的item 继承自QListWidgetItem
class SampleImageQListWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, sample_name, image_path, dependence, description):
        super().__init__()

        self.sample_name = sample_name
        self.image_path = image_path
        self.dependence = dependence
        self.description = description

        self.group = WrapedGroupBox()
        self.name_label = QtWidgets.QLabel(self.group)
        self.name_label.setText(sample_name)

        # 用来显示图像
        self.image_label = QtWidgets.QLabel(self.group)
        self.image_label.setPixmap(QtGui.QPixmap(self.image_path).scaled(QtCore.QSize(200, 150)))
        # 图像自适应窗口大小

        self.v_box = QtWidgets.QVBoxLayout()
        self.v_box.setContentsMargins(0, 0, 0, 0)
        self.v_box.addWidget(self.image_label)
        self.v_box.addWidget(self.name_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter, stretch=1)
        self.v_box.addStretch(1)
        self.group.setLayout(self.v_box)
        # 设置自定义的QListWidgetItem的sizeHint，不然无法显示
        self.setSizeHint(self.group.sizeHint())

    def get_sample_name(self):
        return self.sample_name

    def get_sample_image_path(self):
        return self.image_path

    def get_sample_description(self):
        return self.description

    def get_sample_dependence(self):
        return self.dependence

class SamplesWidget(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(QtCore.QSize(800, 600))
        self.setStyleSheet("background-color:white;border: none;")
        self.setWindowTitle("Samples")
        self.setWindowIcon(QtGui.QIcon("icons/sample.png"))

        sampleListWidget = SampleImageListWidget()
        sampleManager = SamplesManager()
        sample_items = sampleManager.get_items()
        sampleListWidget.load_items(sample_items)

        self.v_box = QtWidgets.QVBoxLayout()
        self.v_box.setContentsMargins(10, 10, 10, 10)
        self.v_box.addWidget(sampleListWidget)
        self.setLayout(self.v_box)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    sampleWidget = SamplesWidget()
    sampleWidget.show()
    sys.exit(app.exec_())
