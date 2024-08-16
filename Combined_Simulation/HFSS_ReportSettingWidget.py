from Combined_Simulation import SimulationAdapter

import os, sys
from enum import Enum

from PyQt5 import QtWidgets, QtCore, QtGui

class Mathematical_formulas(Enum):
    none = "<none>"
    abs = "abs"
    acos = "acos"
    acosh = "acosh"
    ang = "ang"
    ang_deg = "ang_deg"
    ang_deg_val = "ang_deg_val"
    ang_rad = "ang_rad"
    arg = "arg"
    asin = "asin"


class Output_Variables_GroupBox(QtWidgets.QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Output Variables")
        self.setFixedHeight(250)

        self.variables_table = QtWidgets.QTableWidget()
        self.variables_table.setFixedHeight(130)
        self.variables_table.setColumnCount(2)
        self.variables_table.setColumnWidth(0, 352)
        self.variables_table.setColumnWidth(1, 352)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("Name")
        self.variables_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        item.setText("Expression")
        self.variables_table.setHorizontalHeaderItem(1, item)

        self.name_label = QtWidgets.QLabel("Name:")
        self.name_lineEdit = QtWidgets.QLineEdit()
        self.add_button = QtWidgets.QPushButton()
        self.add_button.setText("Add")
        self.update_button = QtWidgets.QPushButton()
        self.update_button.setText("Update")
        self.delete_button = QtWidgets.QPushButton()
        self.delete_button.setText("Delete")

        self.expression_label = QtWidgets.QLabel("Expression:")
        self.expression_textEdit = QtWidgets.QTextEdit()

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.variables_table, 0, 0, 4, 8)
        grid_layout.addWidget(self.name_label, 4, 0, 1, 1)
        grid_layout.addWidget(self.name_lineEdit, 4, 1, 1, 4)
        grid_layout.addWidget(self.add_button, 4, 5, 1, 1)
        grid_layout.addWidget(self.update_button, 4, 6, 1, 1)
        grid_layout.addWidget(self.delete_button, 4, 7, 1, 1)
        grid_layout.addWidget(self.expression_label, 5, 0, 1, 1)
        grid_layout.addWidget(self.expression_textEdit, 5, 1, 1, 7)

        self.setLayout(grid_layout)

        self.add_button.clicked.connect(self.add_expression)
        self.update_button.clicked.connect(self.update_expression)
        self.delete_button.clicked.connect(self.delete_expression)
        self.variables_table.clicked.connect(self.variable_item_selected)
        self.variables_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # 设置选择行为，按行选择
        self.variables_table.setStyleSheet("selection-background-color:rgb(255,209,128)")  # 设置选中行背景颜色
        self.variables_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 设置表格不可修改

    def init_variables_table(self):
        pass

    def add_expression(self):
        name = self.name_lineEdit.text()
        expression = self.expression_textEdit.toPlainText()

        if len(name) == 0 or len(expression) == 0:
            return

        row_count = self.variables_table.rowCount()
        for index in range(row_count):
            if name == self.variables_table.item(index, 0).text():
                reply = QtWidgets.QMessageBox.about(self, "变量名重复", "变量名不能重复")
                return

        self.variables_table.setRowCount(row_count + 1)

        item = QtWidgets.QTableWidgetItem(name)
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.variables_table.setItem(row_count, 0, item)

        item = QtWidgets.QTableWidgetItem(expression)
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.variables_table.setItem(row_count, 1, item)

    def update_expression(self):
        name = self.name_lineEdit.text()
        expression = self.expression_textEdit.toPlainText()

        if len(name) == 0 or len(expression) == 0:
            return

        selected_row = self.variables_table.currentRow()
        row_count = self.variables_table.rowCount()
        for index in range(row_count):
            if selected_row == index:
                continue
            if name == self.variables_table.item(index, 0).text():
                reply = QtWidgets.QMessageBox.about(self, "变量名重复", "变量名不能重复")
                return

        item_list = self.variables_table.selectedItems()
        item_list[0].setText(name)
        item_list[1].setText(expression)

    def delete_expression(self):
        row_id = self.variables_table.currentRow()
        self.variables_table.removeRow(row_id)

    def variable_item_selected(self):
        item_list = self.variables_table.selectedItems()
        name = item_list[0].text()
        expression = item_list[1].text()

        self.name_lineEdit.setText(name)
        self.expression_textEdit.setText(expression)

    def insert_expression(self, expression):
        # self.expression_textEdit.setText(expression)
        self.expression_textEdit.insertPlainText(expression)

    def get_variables_list(self):
        variables_list = []
        row_count = self.variables_table.rowCount()
        for index in range(row_count):
            name = self.variables_table.item(index, 0).text()
            expression = self.variables_table.item(index, 1).text()
            variables_list.append([name, expression])

        return variables_list

class Context_GroupBox(QtWidgets.QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Context")

        self.report_type_label = QtWidgets.QLabel("Repoer Type:")
        self.solution_label = QtWidgets.QLabel("Solution:")
        self.report_type_ComBox = QtWidgets.QComboBox()
        self.solution_ComBox = QtWidgets.QComboBox()
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.report_type_label, 0, 0, 1, 1)
        grid_layout.addWidget(self.report_type_ComBox, 0, 1, 1, 2)
        grid_layout.addWidget(self.solution_label, 1, 0, 1, 1)
        grid_layout.addWidget(self.solution_ComBox, 1, 1, 1, 2)
        grid_layout.addWidget(spacer, 2, 0, 1, 3)

        self.setLayout(grid_layout)

    def set_report_type(self, report_type_list):
        for item in report_type_list:
            self.report_type_ComBox.addItem(item)

    def set_solution(self, solution_list):
        for item in solution_list:
            self.solution_ComBox.addItem(item)

    def get_current_solution(self):
        return self.solution_ComBox.currentText()


class Quantities_GroupBox(QtWidgets.QGroupBox):
    def __init__(self, parent_window=None):
        super().__init__(parent_window)
        self.parent_window = parent_window

        self.setTitle("Quantities")
        self.setFixedHeight(250)
        self.setFixedWidth(350)

        self.category_label = QtWidgets.QLabel("Category")
        self.category_Combox = QtWidgets.QComboBox()
        self.quantity_label = QtWidgets.QLabel("Quantity:")
        self.function_label = QtWidgets.QLabel("Function:")
        self.quantity_list_widget = QtWidgets.QListWidget()
        self.function_list_widget = QtWidgets.QListWidget()
        self.insert_button = QtWidgets.QPushButton()
        self.insert_button.setText("Insert Into Expression")

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.category_label, 0, 0, 1, 1)
        grid_layout.addWidget(self.category_Combox, 0, 1, 1, 3)
        grid_layout.addWidget(self.quantity_label, 1, 0, 1, 2)
        grid_layout.addWidget(self.function_label, 1, 2, 1, 2)
        grid_layout.addWidget(self.quantity_list_widget, 2, 0, 3, 2)
        grid_layout.addWidget(self.function_list_widget, 2, 2, 3, 2)
        grid_layout.addWidget(self.insert_button, 5, 0, 1, 4)
        self.setLayout(grid_layout)

        for name in Mathematical_formulas.__members__.keys():
            self.function_list_widget.addItem(name)
        if self.function_list_widget.count() != 0:
            self.function_list_widget.setCurrentRow(0)

        self.category_Combox.currentIndexChanged.connect(self.selectionCategory)
        self.insert_button.clicked.connect(self.insert_expression)

    def insert_expression(self):
        name = self.quantity_list_widget.currentItem().text()
        function = self.function_list_widget.currentItem().text()
        self.parent_window.insert_expression(name=name, function=function)

    def selectionCategory(self):
        current_category = self.category_Combox.currentText()
        quantity_list = None
        if current_category == "Variables":
            quantity_list = self.parent_window.get_hfssAdapter().get_variable_names()
        elif current_category == "Output Variables":
            quantity_list = self.parent_window.get_hfssAdapter().get_output_variables()
        else:
            quantity_list = self.parent_window.get_hfssAdapter().get_quantity(quantities_category=current_category)
        self.quantity_list_widget.clear()
        for item in quantity_list:
            self.quantity_list_widget.addItem(item)

        if self.quantity_list_widget.count() != 0:
            self.quantity_list_widget.setCurrentRow(0)

    def add_category(self, category):
        if isinstance(category, str):
            self.category_Combox.addItem(category)
        elif isinstance(category, list):
            for item in category:
                self.category_Combox.addItem(item)


class Function_GroupBox(QtWidgets.QGroupBox):
    def __init__(self, parent_window=None):
        super().__init__(parent_window)
        self.parent_window = parent_window

        self.setTitle("Function")
        self.setFixedHeight(60)

        self.func_list_ComBox = QtWidgets.QComboBox()
        self.insert_expression_button = QtWidgets.QPushButton()
        self.insert_expression_button.setText("Insert into Expression")

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.func_list_ComBox)
        h_layout.addWidget(self.insert_expression_button)
        self.setLayout(h_layout)

        for name in Mathematical_formulas.__members__.keys():
            self.func_list_ComBox.addItem(name)

        self.insert_expression_button.clicked.connect(self.insert_expression)

    def insert_expression(self):
        function = self.func_list_ComBox.currentText()
        self.parent_window.insert_expression(function=function)


class Output_Variables_Widget(QtWidgets.QDialog):
    def __init__(self, parent_window=None):
        super().__init__(parent_window)
        self.setFixedSize(QtCore.QSize(800, 600))
        # self.setStyleSheet("background-color:white;border: none;")
        self.setWindowTitle("Output Variables")

        self.output_variables_group = Output_Variables_GroupBox()
        self.context_group = Context_GroupBox()
        self.quantities_group = Quantities_GroupBox(self)
        self.function_group = Function_GroupBox(self)

        self.import_button = QtWidgets.QPushButton()
        self.import_button.setText("Import")
        self.export_button = QtWidgets.QPushButton()
        self.export_button.setText("Export")
        self.done_button = QtWidgets.QPushButton()
        self.done_button.setText("Done")

        widget_1 = QtWidgets.QWidget()
        widget_1_v_layout = QtWidgets.QVBoxLayout()
        widget_1_v_layout.addWidget(self.context_group)
        widget_1_v_layout.addWidget(self.function_group)
        widget_1.setLayout(widget_1_v_layout)

        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.done_button)
        button_widget.setLayout(button_layout)

        widget_2 = QtWidgets.QWidget()
        widget_2_v_layout = QtWidgets.QVBoxLayout()
        widget_2_v_layout.addWidget(self.quantities_group)
        widget_2_v_layout.addWidget(button_widget)
        widget_2.setLayout(widget_2_v_layout)

        widget_3 = QtWidgets.QWidget()
        widget_3_h_layout = QtWidgets.QHBoxLayout()
        widget_3_h_layout.addWidget(widget_1)
        widget_3_h_layout.addWidget(widget_2)
        widget_3.setLayout(widget_3_h_layout)

        v_box_layout = QtWidgets.QVBoxLayout()
        v_box_layout.addWidget(self.output_variables_group)
        v_box_layout.addWidget(widget_3)

        self.setLayout(v_box_layout)

        self.done_button.clicked.connect(self.insert_output_variables)

        if parent_window != None:
            self.hfssAdapter = parent_window.get_hfssAdapter()

            self.context_group.set_report_type(self.hfssAdapter.get_reprot_type())
            self.context_group.set_solution(self.hfssAdapter.get_solution())
            self.quantities_group.add_category("Variables")
            self.quantities_group.add_category("Output Variables")
            self.quantities_group.add_category(self.hfssAdapter.get_category())

            self.hfssAdapter.get_output_variables()

    def get_hfssAdapter(self):
        return self.hfssAdapter

    def insert_expression(self, name="", function=""):
        expression = None
        if function == "none":
            expression = name
        else:
            expression = function + "(" + name + ")"
        self.output_variables_group.insert_expression(expression)

    def insert_output_variables(self):
        variables_list = self.output_variables_group.get_variables_list()
        for item in variables_list:
            name = item[0]
            expression = item[1]

            solution = self.context_group.get_current_solution()
            self.hfssAdapter.create_output_variable(variable=name, expression=expression, solution=solution)

        self.close()



# def test_output_variables_widget():
#     # test_report_setting()
#
#     app = QtWidgets.QApplication(sys.argv)
#     sampleWidget = Output_Variables_Widget()
#     sampleWidget.show()
#     sys.exit(app.exec_())



class Report_Context_GroupBox(QtWidgets.QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Context")
        self.setFixedWidth(230)

        self.solution_label = QtWidgets.QLabel("Solution:")
        self.domain_label = QtWidgets.QLabel("Domain:")
        self.solution_ComBox = QtWidgets.QComboBox()
        self.domain_ComBox = QtWidgets.QComboBox()

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.solution_label, 0, 0, 1, 1)
        grid_layout.addWidget(self.solution_ComBox, 0, 1, 1, 2)
        grid_layout.addWidget(self.domain_label, 1, 0, 1, 1)
        grid_layout.addWidget(self.domain_ComBox, 1, 1, 1, 2)
        grid_layout.addWidget(spacer, 2, 0, 1, 3)

        self.setLayout(grid_layout)

        domain_type_list = ["Sweep", "Time"]
        self.set_domain_type(domain_type_list)

    def set_solution(self, solution_list):
        for item in solution_list:
            self.solution_ComBox.addItem(item)

    def get_solution(self):
        return self.solution_ComBox.currentText()

    def set_domain_type(self, domain_type_list):
        for item in domain_type_list:
            self.domain_ComBox.addItem(item)

class Report_TableWidget(QtWidgets.QTabWidget):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window

        self.setFixedHeight(450)

        self.trace_tab = QtWidgets.QWidget()
        self.families_tab = QtWidgets.QWidget()
        self.families_display_tab = QtWidgets.QWidget()

        self.addTab(self.trace_tab, "Trace")
        self.addTab(self.families_tab, "Families")
        self.addTab(self.families_display_tab, "Families Display")

        self.trace_tab_UI()

    def trace_tab_UI(self):

        primary_sweep_lable = QtWidgets.QLabel("Primary Sweep:")
        self.trace_primary_sweep_combox = QtWidgets.QComboBox()
        self.trace_primary_sweep_edit_line = QtWidgets.QLineEdit()

        x_label = QtWidgets.QLabel("X:")
        self.trace_defalut_check_box = QtWidgets.QCheckBox("Default")
        self.trace_x_edit_line = QtWidgets.QLineEdit()

        y_label = QtWidgets.QLabel("Y:")
        self.trace_y_edit_line = QtWidgets.QLineEdit()

        category_label = QtWidgets.QLabel("Category:")
        quantity_label = QtWidgets.QLabel("Quantity:")
        self.trace_quantity_combox = QtWidgets.QComboBox()
        function_label = QtWidgets.QLabel("Function:")

        self.trace_category_listWidget = QtWidgets.QListWidget()
        self.trace_quantity_listWidget = QtWidgets.QListWidget()
        self.trace_function_listWidget = QtWidgets.QListWidget()

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(primary_sweep_lable, 0, 0, 1, 1)
        grid_layout.addWidget(self.trace_primary_sweep_combox, 0, 1, 1, 1)
        grid_layout.addWidget(self.trace_primary_sweep_edit_line, 0, 2, 1, 6)
        grid_layout.addWidget(x_label, 1, 0, 1, 1)
        grid_layout.addWidget(self.trace_defalut_check_box, 1, 1, 1, 1)
        grid_layout.addWidget(self.trace_x_edit_line, 1, 2, 1, 6)
        grid_layout.addWidget(y_label, 2, 0, 1, 1)
        grid_layout.addWidget(self.trace_y_edit_line, 2, 1, 1, 7)
        grid_layout.addWidget(category_label, 3, 0, 1, 2)
        grid_layout.addWidget(quantity_label, 3, 2, 1, 4)
        grid_layout.addWidget(function_label, 3, 6, 1, 2)
        grid_layout.addWidget(self.trace_category_listWidget, 4, 0, 1, 2)
        grid_layout.addWidget(self.trace_quantity_listWidget, 4, 2, 1, 4)
        grid_layout.addWidget(self.trace_function_listWidget, 4, 6, 1, 2)

        self.trace_tab.setLayout(grid_layout)


        self.trace_primary_sweep_combox.addItem("Freq")
        self.trace_primary_sweep_edit_line.setText("All")
        self.trace_defalut_check_box.setChecked(True)
        self.trace_defalut_check_box.stateChanged.connect(self.set_trace_x_line_edit)
        self.trace_x_edit_line.setText("Freq")
        if self.trace_defalut_check_box.checkState() == QtCore.Qt.CheckState.Checked:
            self.trace_x_edit_line.setEnabled(False)
        else:
            self.trace_x_edit_line.setEnabled(True)

        for name in Mathematical_formulas.__members__.keys():
            self.trace_function_listWidget.addItem(name)
        if self.trace_function_listWidget.count() != 0:
            self.trace_function_listWidget.setCurrentRow(0)

        self.trace_category_listWidget.itemClicked.connect(self.selectionCategory)
        self.trace_quantity_listWidget.itemClicked.connect(self.set_y_edit_line)
        self.trace_function_listWidget.itemClicked.connect(self.set_y_edit_line)

    def set_trace_x_line_edit(self):
        if self.trace_defalut_check_box.checkState() == QtCore.Qt.CheckState.Checked:
            self.trace_x_edit_line.setEnabled(False)
        else:
            self.trace_x_edit_line.setEnabled(True)

    def add_trace_category(self, category):
        if isinstance(category, str):
            self.trace_category_listWidget.addItem(category)
        elif isinstance(category, list):
            for item in category:
                self.trace_category_listWidget.addItem(item)

        if self.trace_category_listWidget.count() != 0:
            self.trace_category_listWidget.setCurrentRow(0)
            self.selectionCategory()
            self.set_y_edit_line()

    def selectionCategory(self):
        current_category = self.trace_category_listWidget.selectedItems()[0].text()

        quantity_list = None
        if current_category == "Variables":
            quantity_list = self.parent_window.get_hfssAdapter().get_variable_names()
        elif current_category == "Output Variables":
            quantity_list = self.parent_window.get_hfssAdapter().get_output_variables()
        else:
            quantity_list = self.parent_window.get_hfssAdapter().get_quantity(quantities_category=current_category)
        self.trace_quantity_listWidget.clear()
        for item in quantity_list:
            self.trace_quantity_listWidget.addItem(item)

        if self.trace_quantity_listWidget.count() != 0:
            self.trace_quantity_listWidget.setCurrentRow(0)

    def set_y_edit_line(self):
        selected_list = self.trace_quantity_listWidget.selectedItems()
        if len(selected_list) == 0:
            return

        name = selected_list[0].text()
        function = self.trace_function_listWidget.selectedItems()[0].text()

        if len(name) == 0 or len(function) == 0:
            return

        self.trace_y_edit_line.clear()
        if function == "none":
            self.trace_y_edit_line.setText(name)
        else:
            self.trace_y_edit_line.setText(function + "(" + name + ")")

    def get_y_edit_line(self):
        return self.trace_y_edit_line.text()

    def get_expression(self):
        return self.get_y_edit_line()

    def get_category(self):
        return self.trace_category_listWidget.selectedItems()[0].text()


class Report_Widget(QtWidgets.QDialog):
    new_report_notifier = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None, adapter=None):
        super().__init__(parent)

        self.hfss_adapter = adapter

        self.setFixedSize(QtCore.QSize(1000, 520))
        # self.setStyleSheet("background-color:white;border: none;")
        self.setWindowTitle("Report")

        self.report_context_groupbox = Report_Context_GroupBox()
        self.output_variables_button = QtWidgets.QPushButton("Output Variables")
        self.options_button = QtWidgets.QPushButton("Options")
        self.report_table_widget = Report_TableWidget(self)
        self.new_report_button = QtWidgets.QPushButton("New Report")
        self.close_button = QtWidgets.QPushButton("Close")

        widget_1 = QtWidgets.QWidget()
        grid_layout_1 = QtWidgets.QGridLayout()
        grid_layout_1.addWidget(self.report_context_groupbox, 0, 0, 1, 3)
        grid_layout_1.addWidget(self.output_variables_button, 1, 0, 1, 2)
        grid_layout_1.addWidget(self.options_button, 1, 2, 1, 1)
        widget_1.setLayout(grid_layout_1)

        button_widget = QtWidgets.QWidget()
        hbox_layout_1 = QtWidgets.QHBoxLayout()
        hbox_layout_1.addWidget(self.new_report_button)
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        hbox_layout_1.addWidget(spacer)
        hbox_layout_1.addWidget(self.close_button)
        button_widget.setLayout(hbox_layout_1)

        widget_2 = QtWidgets.QWidget()
        vbox_layout_1 = QtWidgets.QVBoxLayout()
        vbox_layout_1.addWidget(self.report_table_widget)
        vbox_layout_1.addWidget(button_widget)
        vbox_layout_1.setContentsMargins(0, 0, 0, 0)
        widget_2.setLayout(vbox_layout_1)

        hbox_layout_2 = QtWidgets.QHBoxLayout()
        hbox_layout_2.addWidget(widget_1)
        hbox_layout_2.addWidget(widget_2)
        self.setLayout(hbox_layout_2)

        self.output_variables_button.clicked.connect(self.show_output_variables_widget)
        self.close_button.clicked.connect(self.close_window)
        self.new_report_button.clicked.connect(self.new_report_information)


        # project_file = os.path.join(os.getcwd(), "hfss_source", "Modulator_1mm_result.aedt")
        # self.test_HfssAdapter = SimulationAdapter.HfssAdapter(project_name="HFSS_Project")
        # self.test_HfssAdapter.open_project(project_file=project_file)
        #
        # self.report_context_groupbox.set_solution(self.test_HfssAdapter.get_solution())
        # self.report_table_widget.add_trace_category("Variables")
        # self.report_table_widget.add_trace_category("Output Variables")
        # self.report_table_widget.add_trace_category(self.test_HfssAdapter.get_category())

        self.report_context_groupbox.set_solution(self.hfss_adapter.get_solution())
        self.report_table_widget.add_trace_category("Variables")
        self.report_table_widget.add_trace_category("Output Variables")
        self.report_table_widget.add_trace_category(self.hfss_adapter.get_category())

    def get_hfssAdapter(self):
        return self.hfss_adapter

    def new_report_information(self):

        category = self.report_table_widget.get_category()
        expression = self.report_table_widget.get_expression()
        solution = self.report_context_groupbox.get_solution()

        new_report_information = dict()
        new_report_information["category"] = category
        new_report_information["expression"] = expression
        new_report_information["solution"] = solution

        self.new_report_notifier.emit(new_report_information)

    def show_output_variables_widget(self):
        output_variables_widget = Output_Variables_Widget(self)
        output_variables_widget.show()

    def close_window(self):
        self.close()


