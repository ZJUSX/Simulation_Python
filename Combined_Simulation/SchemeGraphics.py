from __future__ import annotations

import math
import sys
import uuid
import traceback
import logging
import typing
from typing import Union

from PyQt5 import QtWidgets, QtCore, QtGui

import CenterWidget

class SchemeGraphicsScene(QtWidgets.QGraphicsScene):
    """原理图绘制区域的背景"""
    graphicsItem_clicked_notifier = QtCore.pyqtSignal(dict)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.gridSize = 20
        self.gridSquares = 5

        self.startPos = None
        self.currentItem = None

        self.components = []
        self.scheme_paths = []
        # 组件初始时候的名称instance name 例如：BendEuler_1
        self.initInstanceName = dict()

        # self.setSceneRect(-800, -600, 1600, 1200)

        # 设置白色背景
        self.x_line = None
        self.y_line = None
        self.set_theme(theme="white")

    def set_theme(self, theme):
        if self.x_line is not None:
            self.removeItem(self.x_line)
        if self.y_line is not None:
            self.removeItem(self.y_line)

        if theme == "white":
            # 设置白色背景
            self.theme = "white"
            self.colorBackground = QtGui.QColor('#ffffff')
            self.colorLight = QtGui.QColor('#d1dee8')
            self.colorDark = QtGui.QColor('#e0e5ec')

            self.penLight = QtGui.QPen(self.colorLight)
            self.penLight.setWidth(1)
            self.penDark = QtGui.QPen(self.colorDark)
            self.penDark.setWidth(2)

            self.setBackgroundBrush(self.colorBackground)

            self.pen_line = QtGui.QPen(QtGui.QColor('#292929'))
            self.pen_line.setWidth(3)
            self.x_line = QtWidgets.QGraphicsLineItem()
            self.x_line.setLine(-40, 0, 40, 0)
            self.x_line.setPen(self.pen_line)
            self.y_line = QtWidgets.QGraphicsLineItem()
            self.y_line.setLine(0, -40, 0, 40)
            self.y_line.setPen(self.pen_line)
            self.addItem(self.x_line)
            self.addItem(self.y_line)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRect):
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        leftStart = left - left % self.gridSize
        topStart = top - top % self.gridSize

        linesDark, linesLight = [], []
        for x in range(leftStart, right, self.gridSize):
            if x % (self.gridSize * self.gridSquares) != 0:
                linesLight.append(QtCore.QLine(x, top, x, bottom))
            else:
                linesDark.append(QtCore.QLine(x, top, x, bottom))

        for y in range(topStart, bottom, self.gridSize):
            if y % (self.gridSize * self.gridSquares) != 0:
                linesLight.append(QtCore.QLine(left, y, right, y))
            else:
                linesDark.append(QtCore.QLine(left, y, right, y))

        painter.setPen(self.penLight)
        if linesLight:
            painter.drawLines(linesLight)

        painter.setPen(self.penDark)
        if linesDark:
            painter.drawLines(linesDark)

    def add_component(self, item: SchemeGraphicsItem):
        self.components.append(item)
        self.addItem(item)

    def delete_component(self, item: SchemeGraphicsItem):
        self.components.remove(item)
        self.removeItem(item)

    def get_component_list(self) -> list[SchemeGraphicsItem]:
        return self.components

    def add_path(self, path: WrapGraphicsPath):
        self.scheme_paths.append(path)
        self.addItem(path)

    def remove_path(self, path: WrapGraphicsPath):
        self.scheme_paths.remove(path)
        self.removeItem(path)

    def get_path_list(self) -> list[WrapGraphicsPath]:
        return self.scheme_paths

    # def setGraphicItemProperty(self, currentProperty):
    #     itemUUID = currentProperty['uuid']
    #     logging.info(currentProperty)
    #     try:
    #         if self.currentItem is not None and self.currentItem.getuuid() == itemUUID:
    #             self.currentItem.setProperty(currentProperty)
    #     except:
    #         traceback.print_exc()

    def click_item(self, item: SchemeGraphicsItem):
        info = None
        if item is not None:
            logging.info("%s item is clicked" % item.project_name)
            info = item.get_project_info()
            self.currentItem = item

        self.graphicsItem_clicked_notifier.emit(info)

    # def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
    #     # logging.info("scene event: %s" % (type(event)))
    #     # logging.info("scene scenePos: (%d, %d), pos: (%d, %d), screenPos: (%d, %d)" % (
    #     #     event.scenePos().x(), event.scenePos().y(), # event.scenePos() 鼠标事件在场景坐标系下的位置
    #     #     event.pos().x(), event.pos().y(),
    #     #     event.screenPos().x(), event.screenPos().y())) # event.screenPos() 鼠标事件在屏幕坐标系下的位置
    #     super().mouseMoveEvent(event)

class SchemeGraphicsView(QtWidgets.QGraphicsView):
    """原理图绘制区域"""

    def __init__(self, graphicScene: SchemeGraphicsScene, parent: CenterWidget):
        super().__init__(parent)

        self.graphicScene = graphicScene
        self.parent = parent
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.drag_path = None
        self.selected_path = None

        # component 的 action
        self.itemCutAction = QtWidgets.QAction("Item Cut", self)
        self.itemCopyAction = QtWidgets.QAction("Item Copy", self)
        self.itemPasteAction = QtWidgets.QAction("Item Paste", self)
        self.itemDeleteAction = QtWidgets.QAction("Item Delete", self)
        # 非component 的 action
        self.undoAction = QtWidgets.QAction("Undo", self)
        self.redoAction = QtWidgets.QAction("Redo", self)

        self.pathDeleteAction = QtWidgets.QAction("Path Delete", self)
        self.pathDeleteAction.triggered.connect(self.path_delete_action)

        self.initUI()

    def initUI(self):
        self.setScene(self.graphicScene)

        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.HighQualityAntialiasing |
                            QtGui.QPainter.TextAntialiasing |
                            QtGui.QPainter.SmoothPixmapTransform |
                            QtGui.QPainter.LosslessImageRendering)

        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        # self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.AnchorUnderMouse)

        # 设置右击图元显示菜单
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.item_right_mouse_clicked)

        self.setDragMode(self.RubberBandDrag)
        # self.centerOn(0, 0)

    def update_component_info(self, info):
        self.parent.emit_project_info(info)

    def item_right_mouse_clicked(self):
        right_mousr_clicked_menu = QtWidgets.QMenu()
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor(255, 255, 255))
        right_mousr_clicked_menu.setPalette(palette)

        right_mousr_clicked_menu.addAction(self.itemCutAction)
        right_mousr_clicked_menu.addAction(self.itemCopyAction)
        right_mousr_clicked_menu.addAction(self.itemPasteAction)
        right_mousr_clicked_menu.addAction(self.itemDeleteAction)
        right_mousr_clicked_menu.addAction(self.undoAction)
        right_mousr_clicked_menu.addAction(self.redoAction)
        right_mousr_clicked_menu.addAction(self.pathDeleteAction)

        right_mousr_clicked_menu.triggered[QtWidgets.QAction].connect(self.item_right_clicked_trigger)
        right_mousr_clicked_menu.exec_(QtGui.QCursor.pos())

    def item_right_clicked_trigger(self, request):
        command = request.text()
        logging.info('item right mouse clicked trigger command: %s' % (command))
        if 'Delete' == command:
            items = self.graphicScene.selectedItems()
            for item in items:
                self.graphicScene.delete_component(item)

    def path_delete_action(self):
        logging.info("delete paht")
        if self.selected_path is None:
            logging.warning("path is not selected")
            return

        self.selected_path.wraped_path.remove_item()
        self.selected_path = None

    def path_drag_start(self, item: SchemeGraphicsItem):
        # print("path_drag_start")
        self.drag_start_item = item
        self.drag_path = SchemeGraphicsPath(self.graphicScene, self.drag_start_item, None)
        # print("path_drag_start ", self.drag_path)

    def path_drag_end(self, item: SchemeGraphicsItem):
        self.drag_path.remove_item()
        self.drag_path = SchemeGraphicsPath(self.graphicScene, self.drag_start_item, item)
        self.drag_path = None

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        # logging.info("mousePressEvent")
        logging.info("view position----: %s, %s" % (event.pos().x(), event.pos().y()))
        scene_pos = self.mapToScene(event.pos())
        logging.info("scene position------: %s, %s" % (scene_pos.x(), scene_pos.y()))

        if self.selected_path is not None:
            self.selected_path.path_pen.setWidthF(2.0)
            self.selected_path = None

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.pos()
            item = self.itemAt(pos)
            if isinstance(item, SchemeGraphicsItem):
                if self.parent.draw_line_mode == True:
                    self.path_drag_start(item)
                    return
                self.graphicScene.click_item(item)
            elif isinstance(item, WrapGraphicsPath):
                logging.info("path select")
                self.selected_path = item
                self.selected_path.path_pen.setWidthF(4.0)

                info = dict()
                info["type"] = "path"
                info["uuid"] = self.selected_path.wraped_path.path_uuid
                info["start_item"] = self.selected_path.wraped_path.start_item.get_project_info()
                info["end_item"] = self.selected_path.wraped_path.end_item.get_project_info()
                self.graphicScene.graphicsItem_clicked_notifier.emit(info)
            elif item is None:
                self.graphicScene.graphicsItem_clicked_notifier.emit(dict())


        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            item = self.itemAt(event.pos())
            if item is not None and item.isSelected():
                # 右键点击的是component 则以下action可见
                logging.info("item is selected")
                if isinstance(item, WrapGraphicsPath):
                    self.selected_path = item
                    self.selected_path.path_pen.setWidthF(4.0)

                    self.pathDeleteAction.setVisible(True)
                    self.pathDeleteAction.setEnabled(True)

                    self.itemCutAction.setVisible(False)
                    self.itemCopyAction.setVisible(False)
                    self.itemPasteAction.setVisible(False)
                    self.itemDeleteAction.setVisible(False)
                    self.itemCutAction.setEnabled(False)
                    self.itemCopyAction.setEnabled(False)
                    self.itemPasteAction.setEnabled(False)
                    self.itemDeleteAction.setEnabled(False)
                else:
                    self.itemCutAction.setVisible(True)
                    self.itemCopyAction.setVisible(True)
                    self.itemPasteAction.setVisible(True)
                    self.itemDeleteAction.setVisible(True)
                    self.itemCutAction.setEnabled(True)
                    self.itemCopyAction.setEnabled(True)
                    self.itemPasteAction.setEnabled(True)
                    self.itemDeleteAction.setEnabled(True)

                    self.pathDeleteAction.setVisible(False)
                    self.pathDeleteAction.setEnabled(False)

                self.redoAction.setVisible(False)
                self.undoAction.setVisible(False)
                self.redoAction.setEnabled(False)
                self.undoAction.setEnabled(False)
            else:
                # 右键点击的是空白区域则以下action不可见
                self.itemCutAction.setVisible(False)
                self.itemCopyAction.setVisible(False)
                self.itemPasteAction.setVisible(False)
                self.itemDeleteAction.setVisible(False)
                self.itemCutAction.setEnabled(False)
                self.itemCopyAction.setEnabled(False)
                self.itemPasteAction.setEnabled(False)
                self.itemDeleteAction.setEnabled(False)

                self.pathDeleteAction.setVisible(False)
                self.pathDeleteAction.setEnabled(False)

                self.redoAction.setVisible(True)
                self.undoAction.setVisible(True)
                self.redoAction.setEnabled(True)
                self.undoAction.setEnabled(True)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: typing.Optional[QtGui.QMouseEvent]) -> None:
        # print("mouseReleaseEvent")
        if self.parent.draw_line_mode is True:
            if self.drag_path is not None:
                pos = event.pos()
                item = self.itemAt(pos)
                if isinstance(item, SchemeGraphicsItem) and item is not self.drag_start_item:
                    self.path_drag_end(item)
                else:
                    self.drag_path.remove_item()
                    self.drag_path = None

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:
        # logging.info("mouseMoveEvent")
        # logging.info("view %s" % (type(event)))
        # logging.info("view pos: (%d, %d)， screenPos: (%d, %d)" %(
        #             event.pos().x(), event.pos().y(), # event.pos()鼠标在控件坐标系下的位置
        #             event.screenPos().x(), event.screenPos().y())) # event.screenPos()鼠标事件在屏幕坐标系下的位置

        pos = event.pos()
        if self.parent.draw_line_mode is True and self.drag_path is not None:
            # print(type(self.drag_path))
            cursor_scene_pos = self.mapToScene(pos)
            self.drag_path.wrap_graphics_path.set_dst_position(cursor_scene_pos.x(), cursor_scene_pos.y())
            self.drag_path.wrap_graphics_path.update()
        super().mouseMoveEvent(event)

class SchemeGraphicsItem(QtWidgets.QGraphicsPixmapItem):
    """原理图绘制中的操作对象"""

    # 用于发送 component 的信息
    # pdkInfo = QtCore.pyqtSignal(str)

    def __init__(self, project_info, view_parent: SchemeGraphicsView, parent=None):

        super().__init__(parent)

        """
            project_info 字段信息：
            {
                'project_name': 'HFSS_Project_1',
                'project_type': 'HFSS',
                # position 为图元的中心位置
                'position_x': 0,
                'position_y': 0,
                'uuid': 
                'pic_path': 'F:\\tmp\\src\\img\\BendEuler.jpg'
            }
        """

        self.project_info = project_info
        self.view_parent = view_parent
        self.__project_name = self.project_info["project_name"]
        self.__uuid = self.project_info["uuid"]
        self.pix = QtGui.QPixmap(self.project_info["pic_path"])
        self.project_info['position_y'] = -self.project_info['position_y'] # 添加负号，用于将对象从场景坐标转换到版图坐标系
        self.project_info["type"] = "project"  # 用于和path区分

        # self.width = int(self.pix.width() * 0.2)
        # self.height = int(self.pix.height() * 0.2)

        logging.info("SchemeGraphicsItem pix width: %s, pix height: %s", self.pix.width(), self.pix.height())
        self.newpix = self.pix.scaled(self.pix.width(), self.pix.height())
        self.setPixmap(self.newpix)

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def get_project_info(self) -> dict:
        logging.info(self.project_info)
        return self.project_info

    @property
    def project_uuid(self):
        return self.__uuid

    @property
    def project_name(self):
        return self.__project_name

    def setProperty(self, property: dict):
        # logging.info("setProperty: %s" % (str(property)))
        if 'position_x' in property.keys():
            self.project_info['position_x'] = property['position_x']

        if 'position_y' in property.keys():
            self.project_info['position_y'] = -property['position_y'] # 添加负号，用于将对象从场景坐标转换到版图坐标系

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        # logging.info("mouseMoveEvent")
        # logging.info("Item event type: %s" % (type(event)))
        # logging.info("Item scenePos x: %d, y: %d" % (event.scenePos().x(), event.scenePos().y())) # 鼠标事件在场景坐标系下的位置
        # logging.info("Item bounding width: %d, height: %d, topLeft: (%d, %d)" %(
        #             self.boundingRect().width(), self.boundingRect().height(),
        #             self.boundingRect().topLeft().x(), self.boundingRect().topLeft().y()))
        # logging.info("Item self pos: (%d, %d)" % (self.pos().x(), self.pos().y())) # self.pos()返回父坐标坐标，无父坐标则返回场景坐标系，所以self.pos(), self.scenePos() 获取的坐标值一致
        # logging.info("Item scene pos: (%d, %d)" % (self.scenePos().x(), self.scenePos().y()))

        # 正在绘制路径的时候
        if self.view_parent.parent.draw_line_mode is False and self.view_parent.drag_path is None:
            currentPosition = dict()
            currentPosition['position_x'] = self.pos().x()
            currentPosition['position_y'] = self.pos().y()
            # currentPosition['position_x'] = self.pos().x() + self.boundingRect().topLeft().x() + self.boundingRect().width() / 2
            # currentPosition['position_y'] = self.pos().y() + self.boundingRect().topLeft().y() + self.boundingRect().height() / 2
            # logging.info("Item uuid: %s, pos: (%d, %d)" % (self.getuuid(), self.pos().x(), self.pos().y()))
            self.setProperty(currentPosition)
            self.view_parent.update_component_info(self.get_project_info())

        super().mouseMoveEvent(event)
        if self.isSelected():
            for path in self.scene().scheme_paths:
                path.wraped_path.update_position()


    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        # logging.info("mousePressEvent")
        # logging.info(type(event))
        # logging.info("Item position x: %d, y: %d" % (event.scenePos().x(), event.scenePos().y()))
        #
        # try:
        #     self.pdkInfo.emit(str("test~"))
        # except:
        #     traceback.print_exc()
        super().mousePressEvent(event)


class WrapGraphicsPath(QtWidgets.QGraphicsPathItem):
    def __init__(self, wraped_path: SchemeGraphicsPath, parent=None):

        super().__init__(parent)
        self.wraped_path = wraped_path
        self.width = 2.0
        self.pos_src = [0, 0]
        self.pos_dst = [0, 0]

        self.path_pen = QtGui.QPen(QtGui.QColor("#000"))
        self.path_pen.setWidthF(self.width)

        self.path_pen_drag = QtGui.QPen(QtGui.QColor("#000"))
        self.path_pen_drag.setStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.path_pen_drag.setWidthF(self.width)

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        # 设置item的层叠顺序, zValue值大的item在zValue值小的item之上
        self.setZValue(-1)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def set_src_position(self, x, y):
        self.pos_src = [x, y]

    def set_dst_position(self, x, y):
        self.pos_dst = [x, y]

    def calcu_path(self) -> QtGui.QPainterPath:
        # print("src: (%s, %s)---------->(%s, %s)" % ( self.pos_src[0], self.pos_src[1], self.pos_dst[0], self.pos_dst[1]))
        # 绘制斜线
        # path = QtGui.QPainterPath(QtCore.QPointF(self.pos_src[0], self.pos_src[1]))
        # path.lineTo(self.pos_dst[0], self.pos_dst[1])
        # 绘制折现
        path = QtGui.QPainterPath(QtCore.QPointF(self.pos_src[0], self.pos_src[1]))
        path.lineTo(self.pos_dst[0], self.pos_src[1])
        path.lineTo(self.pos_dst[0], self.pos_dst[1])
        return path

    # 会死机，没有错误提示
    # def boundingRect(self):
    #     return self.shape().boundingRect()
    #
    # def shape(self) -> QtGui.QPainterPath:
    #     return self.calcu_path()

    def paint(self, painter: QtGui.QPainter, graphicsItem: QtWidgets.QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.calcu_path())
        path = self.path()
        if self.wraped_path.end_item is None:
            painter.setPen(self.path_pen_drag)
            painter.drawPath(path)
        else:
            painter.setPen(self.path_pen)
            painter.drawPath(path)

class SchemeGraphicsPath:
    def __init__(self, scheme_scene: SchemeGraphicsScene, start_item: SchemeGraphicsItem, end_item: SchemeGraphicsItem|None):

        self.scheme_scene = scheme_scene
        self.start_item = start_item
        self.end_item = end_item

        self.wrap_graphics_path = WrapGraphicsPath(self)
        self.scheme_scene.add_path(self.wrap_graphics_path)

        if self.start_item is not None:
            self.update_position()

        if end_item is not None:
            self.path_uuid = uuid.uuid4().hex

    # def __del__(self):
        # print("SchemeGraphicsPath finish: ", self)

    def update_position(self):
        src_pos = self.start_item.pos()
        width_offset = self.start_item.pix.width() / 2
        height_offset = self.start_item.pix.height() / 2
        self.wrap_graphics_path.set_src_position(src_pos.x() + width_offset, src_pos.y() + height_offset)
        if self.end_item is not None:
            width_offset = self.end_item.pix.width() / 2
            height_offset = self.end_item.pix.height() / 2
            end_pos = self.end_item.pos()
            self.wrap_graphics_path.set_dst_position(end_pos.x() + width_offset, end_pos.y() + height_offset)
        self.wrap_graphics_path.update()

    def remove_current_item(self):
        self.start_item = None
        self.end_item = None

    def remove_item(self):
        self.remove_current_item()
        self.scheme_scene.remove_path(self.wrap_graphics_path)
        self.wrap_graphics_path = None
        # self.scheme_scene = None

