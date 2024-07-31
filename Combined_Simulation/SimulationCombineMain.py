from __future__ import annotations
import sys
from pathlib import Path
import typing
import traceback
from PyQt5 import QtWidgets, QtGui

import UIMainWindow
import setupLog
from ProjectManager import projectManagerSingleton

class MainWindow(QtWidgets.QMainWindow, UIMainWindow.UIMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUI(self)

    def closeEvent(self, a0: typing.Optional[QtGui.QCloseEvent]) -> None:
        super().closeEvent(a0)

        projectManagerSingleton.close_project()


if __name__ == "__main__":

    try:
        setupLog.setupLog()
        app = QtWidgets.QApplication(sys.argv)
        app.setStyleSheet(Path("cb.qss").read_text())
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec())
    except:
        traceback.print_exc()