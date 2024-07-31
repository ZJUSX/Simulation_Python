import os
import sys
import logging
import winreg
import re
from pathlib import Path

import pyaedt
from pyaedt import Hfss
import mph

def search_registry():
    python_api_list = list()

    main_path = r'SOFTWARE\ANSYS, Inc.'
    try:
        main_node = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, main_path)

    except FileNotFoundError:
        logging.error('Did not find Comsol registry entry.')
        return []

    index = 0
    while True:

        # Get name of next node. Exit loop when list exhausted.
        try:
            node_name = winreg.EnumKey(main_node, index)
            logging.info("node name%s" % node_name)
            index += 1
        except OSError:
            break

        # Ignore nodes that don't follow naming pattern.
        if not re.match(r'(?i)Lumerical v\d+', node_name):
            logging.error(f'Ignoring registry node "{node_name}".')
            continue

        # Open the child node.
        node_path = main_path + '\\' + node_name
        logging.info(f'Checking registry node "{node_path}".')
        try:
            node = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, node_path)
        except FileNotFoundError:
            logging.debug(f'Could not open registry node "{node_name}".')
            continue

        # Get installation folder from corresponding key.
        key = 'installFolder'
        try:
            value = winreg.QueryValueEx(node, key)
        except FileNotFoundError:
            logging.error(f'Key "{key}" missing in node "{node_name}".')
            continue
        root = Path(value[0])
        logging.info(f'Checking installation folder "{root}".')

        python_api = root/'api'/'python'
        python_api_list.append(python_api)
        return python_api_list

# os.add_dll_directory('F:\\devTool\\Lumerical\\v202\\api\\python')
# sys.path.append("F:\\devTool\\Lumerical\\v202\\api\\python")

api_list = search_registry()
os.add_dll_directory(str(api_list[0]))
sys.path.append(str(api_list[0]))

import lumapi

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

class SimulationSoftwareAdapter():

    def __init__(self, project_name):
        self.__project_file_path = None # 存放仿真文件的路径
        self.__name = project_name

    def open_project(self, project_file):
        raise NotImplementedError()

    def save_project(self):
        raise NotImplementedError()

    def close_project(self):
        raise NotImplementedError()

    def run_simulation(self):
        raise  NotImplementedError()

    @property
    def type(self):
        raise NotImplementedError()

    @property
    def project_name(self):
        return self.__name

    @project_name.setter
    def project_name(self, value):
        self.__name = value

    def log_wrap_function_handler(self):
        pass

class HfssAdapter(SimulationSoftwareAdapter):

    def __init__(self, project_name):
        super().__init__(project_name)
        self.__aedtapp = Hfss(new_desktop_session=True, close_on_exit=True)
        self.__variables_dict = dict() # 存放变量列表

    def __del__(self):
        if self.__aedtapp is not None:
            self.__aedtapp.close_desktop()

    @property
    def type(self):
        return "HFSS"

    def open_project(self, project_file):
        """ Open an AEDT project.

        :param project_file: str
            Full path and name for the project.
        :return: bool
            ``True`` when successful, ``False`` when failed.
        """

        self.__project_file_path = project_file
        logging.info("open hfss project from %s" % project_file)
        ret = self.__aedtapp.load_project(project_file=project_file)
        if False == ret:
            logging.error("open hfss project from %s failed" % project_file)
        else:
            logging.info("open hfss project from %s success" % project_file)
        return ret

    def save_project(self):

        self.__aedtapp.save_project()

    def save_project_as(self, project_newFile=None):

        if project_newFile is None:
            logging.error("save project path is None")
            return False
        self.__aedtapp.save_project(project_file=project_newFile)

    def close_project(self):
        """ Close AEDT and release it.

        :return:
        """
        if self.__aedtapp is not None:
            self.__aedtapp.close_desktop()
            self.__aedtapp = None

    def get_variables(self):
        """ Get all variables

        :return: dict
            return variables and expressions
        """
        variables = self.__aedtapp.variable_manager.variables
        for key, value in variables.items():
            expression = self.__aedtapp.variable_manager.get_expression(key)
            self.__variables_dict[key] = expression

        return self.__variables_dict

    def set_variables(self, variable_name, expression):
        """ Set the value of a variable

        :param variable_name: str
            Name of the variable
        :param expression: str
            Valid string expression
        :return:
        """
        ret = self.__aedtapp.variable_manager.set_variable(variable_name=variable_name, expression=expression)
        if False == ret:
            logging.error("set_variable(%s, %s) failed" % (variable_name, expression))

        return ret

    def create_output_variable(self, variable, expression, solution):

        self.__aedtapp.create_output_variable(variable=variable, expression=expression, solution=solution)

    def create_report(self, expressions):

        self.__aedtapp.post.create_report(expressions)

    def export_report(self, export_path):

        self.__aedtapp.export_results(export_folder=export_path)

    def run_simulation(self):

        validate_msg, validate_ret = self.__aedtapp.validate_full_design()
        logging.info(validate_msg)
        if isinstance(validate_ret, bool):
            if validate_ret is False:
                logging.error("hfss validate check failed")
                return False

        analyze_ret = self.__aedtapp.analyze_setup()
        # analyze_ret = self.__aedtapp.analyze()
        if analyze_ret is False:
            logging.error("hfss analyze failed")
            return False
        else:
            logging.error("hfss analyze success")
            return True

class ComsolAdapter(SimulationSoftwareAdapter):
    def __init__(self, project_name):
        super().__init__(project_name)

        self.__client = mph.start(version='6.1')
        self.__model = None
        self.__variables_dict = dict()  # 存放变量列表

    @property
    def type(self):
        return "Comsol"

    def open_project(self, project_file):
        """ Open an Comsol project.

                :param project_file: str
                    Full path and name for the project.
                :return: bool
                    ``True`` when successful, ``False`` when failed.
                """

        self.__project_file_path = project_file
        logging.info("open comsol project from %s" % project_file)
        self.__model = self.__client.load(file=project_file)
        if self.__model is None:
            logging.error("open comsol project from %s failed" % project_file)
            return False
        else:
            logging.info("open comsol project from %s success" % project_file)
            return True

    def save_project(self):

        self.__model.save(self.__project_file_path)

    def save_project_as(self, project_newFile=None):

        if project_newFile is None:
            logging.error("save project path is None")
            return False

        self.__model.save(project_newFile)

    def close_project(self):
        if self.__model is not None:
            self.__client.remove(self.__model)
        self.__model = None
        self.__client.clear()

    def get_variables(self):
        """ Get all variables

        :return: dict
            return variables and expressions
        """

        parameters_file = os.path.join(os.getcwd(), "tmp", "comsol_parameters_tmpFile.txt")
        if os.path.exists(parameters_file) is True:
            os.remove(parameters_file)

        self.__model.java.param().saveFile(parameters_file)

        with open(parameters_file, 'r', encoding="UTF-8") as parameters_fd:
            for line in parameters_fd:
                columns = line.split()
                paraName = columns[0]
                paraExpress = columns[1]
                paraDes = columns[2]
                self.__variables_dict[paraName] = paraExpress

        if os.path.exists(parameters_file) is True:
            os.remove(parameters_file)

        return self.__variables_dict

    def set_variables(self, variable_name, expression):
        """ Set the value of a variable

        :param variable_name: str
            Name of the variable
        :param expression: str
            Valid string expression
        :return:
        """

        self.__model.java.param().set(variable_name, expression)

    def run_simulation(self):
        self.__model.build()
        self.__model.mesh()
        self.__model.solve()

    """
        报表导出封装以下接口
        self.__model.java.result().numerical().create("gev1", "EvalGlobal")
        self.__model.java.result().numerical("gev1").setIndex("expr", "imag(ewfd.neff)", 0)
        self.__model.java.result().numerical("gev1").setIndex("expr", "real(ewfd.neff)", 1)
        self.__model.java.result().numerical("gev1").set("data", "dset3")
        self.__model.java.result().table().create("tbl1", "Table")
        self.__model.java.result().table("tbl1").comments("Global Evaluation 1")
        self.__model.java.result().numerical("gev1").set("table", "tbl1")
        self.__model.java.result().numerical("gev1").setResult()
    
        if export_path is not None:
            self.__model.java.result().table("tbl1").save(export_path)
    """
    def result_numerical_create(self, name, type):
        self.__model.java.result().numerical().create(name, type)

    def result_numerical_setIndex(self, name, expression, index):
        self.__model.java.result().numerical(name).setIndex("expr", expression, index)

    def result_numerical_setData(self, name, data):
        self.__model.java.result().numerical(name).set("data", data)

    def result_table_create(self, name, type):
        self.__model.java.result().table().create(name, type)

    def result_table_comments(self, name, comments):
        self.__model.java.result().table(name).comments(comments)

    def result_numerical_set_table(self, numerical_name, table_name):
        self.__model.java.result().numerical(numerical_name).set("table", table_name)

    def result_numerical_setResult(self, name):
        self.__model.java.result().numerical(name).setResult()

    def result_table_set_export_path(self, table_name, export_path):
        self.__model.java.result().table(table_name).save(export_path)

class InterconnectAdapter(SimulationSoftwareAdapter):
    def __init__(self, project_name):
        super().__init__(project_name)
        self.__interconnect = lumapi.INTERCONNECT(hide=False)
        self.__interconnect.deleteall()

        self.__module_property_dict = dict()  # 存放模块的属性

    @property
    def type(self):
        return "Interconnect"

    def open_project(self, project_file):
        """ Open an Interconnect project.

        :param project_file: str
            Full path and name for the project.
        :return: bool
            ``True`` when successful, ``False`` when failed.
        """

        self.__project_file_path = project_file
        logging.info("open Interconnect project from %s" % project_file)
        ret = self.__interconnect.load(project_file)
        if False == ret:
            logging.error("open Interconnect project from %s failed" % project_file)
        else:
            self.__interconnect.switchtodesign()
            logging.info("open Interconnect project from %s success" % project_file)
        return ret

    def save_project(self):

        self.__interconnect.save()

    def save_project_as(self, project_newFile=None):

        if project_newFile is None:
            logging.error("save project path is None")
            return False
        self.__interconnect.save(project_newFile)

    def close_project(self):
        """ Close Interconnect and release it.

        :return:
        """
        logging.info("close interconnect project")
        # self.__interconnect.exit()

    def get_element_name_list(self):
        """ Get Interconnect element name list

        :return:
        """

        ele_nameList = []
        self.__interconnect.selectall()
        element_number = int(self.__interconnect.getnumber())
        for index in range(element_number):
            name = self.__interconnect.get("name", index + 1)
            ele_nameList.append(name)

        return ele_nameList

    def get_element_property(self, element_name=None, property_name=None):

        self.__interconnect.select(element_name)
        if property_name is None:
            property_str = self.__interconnect.get()
            property_list = property_str.split("\n")
            return property_list
        else:
            property_value = self.__interconnect.get(property_name)
            return property_value

    def set_element_property(self, element_name=None, property_name=None, property_value=None):

        if element_name is None or property_name is None or property_value is None:
            logging.error("element name or property name or property value is None")
            return

        self.__interconnect.select(element_name)
        self.__interconnect.set(property_name, property_value)

    def run_simulation(self):

        self.__interconnect.run()

class SimulationAdapterFactory():
    def __init__(self):
        pass

    def produce_adapter(self, project_name, type = None):

        if None == type:
            logging.error("type is None")
            return False
        elif "HFSS" == type:
            return HfssAdapter(project_name)
        elif "Comsol" == type:
            return ComsolAdapter(project_name)
        elif "Interconnect" == type:
            return InterconnectAdapter(project_name)
        else:
            logging.info("Undefine type")
            return False

simulationAdapterFactory = SimulationAdapterFactory()


#### ====================================================== 测试代码 ======================================================

## ====================================================== HFSS 测试代码 ======================================================
def test_Hfss():
    test_HfssAdapter = HfssAdapter(project_name="HFSS_Project")

def test_HfssAdapter_open_close():
    project_file = os.path.join(os.getcwd(), "hfss_source", "Modulator_1mm.aedt")

    test_HfssAdapter = HfssAdapter(project_name="HFSS_Project")
    test_HfssAdapter.open_project(project_file=project_file)
    test_HfssAdapter.close_project()

def test_HfssAdapter_save_project():
    project_file = os.path.join(os.getcwd(), "hfss_source", "Modulator_1mm.aedt")

    test_HfssAdapter = HfssAdapter(project_name="HFSS_Project")
    test_HfssAdapter.open_project(project_file=project_file)

    project_newFile = os.path.join(os.getcwd(), "hfss_source", "Modulator_1mm_new.aedt")
    test_HfssAdapter.save_project_as(project_newFile=project_newFile)
    test_HfssAdapter.close_project()

def test_HfssAdapter_get_variables():
    project_file = os.path.join(os.getcwd(), "hfss_source", "Modulator_1mm.aedt")
    print(project_file)

    test_HfssAdapter = HfssAdapter(project_name="HFSS_Project")
    test_HfssAdapter.open_project(project_file=project_file)

    variables = test_HfssAdapter.get_variables()
    for key, value in variables.items():
        print(key, value)

    test_HfssAdapter.close_project()

def test_HfssAdapter_set_variables():
    project_file = os.path.join(os.getcwd(), "hfss_source", "Modulator_1mm.aedt")

    test_HfssAdapter = HfssAdapter(project_name="HFSS_Project")
    test_HfssAdapter.open_project(project_file=project_file)

    print(" ------------------------- before set variable: ------------------------- ")
    variables = test_HfssAdapter.get_variables()
    for key, value in variables.items():
        print(key, value)

    test_HfssAdapter.set_variables("d_sioup", "0.9um")

    print(" ------------------------- after set variable: ------------------------- ")
    variables = test_HfssAdapter.get_variables()
    for key, value in variables.items():
        print(key, value)

    test_HfssAdapter.close_project()

def test_HfssAdapter_run_simulation():
    project_file = os.path.join(os.getcwd(), "hfss_source", "Modulator_1mm.aedt")

    test_HfssAdapter = HfssAdapter(project_name="HFSS_Project")
    test_HfssAdapter.open_project(project_file=project_file)

    test_HfssAdapter.run_simulation()
    project_newFile = os.path.join(os.getcwd(), "hfss_source", "Modulator_1mm_result.aedt")
    test_HfssAdapter.save_project_as(project_newFile=project_newFile)

    test_HfssAdapter.close_project()

def test_HfssAdapter_export_result():
    project_file = os.path.join(os.getcwd(), "hfss_source", "Modulator_1mm_result.aedt")

    test_HfssAdapter = HfssAdapter(project_name="HFSS_Project")
    test_HfssAdapter.open_project(project_file=project_file)

    test_HfssAdapter.create_output_variable(variable="loss", expression="Re(Gamma(1))*8.68/100", solution="Setup1:Sweep")
    test_HfssAdapter.create_output_variable(variable="neff", expression="300000000*Im(Gamma(1))/2/3.14/freq", solution="Setup1:Sweep")

    test_HfssAdapter.create_report(expressions="loss")
    test_HfssAdapter.create_report(expressions="neff")
    test_HfssAdapter.create_report(expressions="Zo(1)")

    export_path = os.path.join(os.getcwd(), "hfss_result")
    test_HfssAdapter.export_report(export_path=export_path)

## ====================================================== Comsol 测试代码 ======================================================

def test_Comsol():
    test_ComsolAdapter = ComsolAdapter(project_name="Comsol_Project")

def test_ComsolAdapter_open_close():
    project_file = os.path.join(os.getcwd(), "comsol_source", "调制器截面仿真.mph")

    test_ComsolAdapter = ComsolAdapter(project_name="Comsol_Project")
    test_ComsolAdapter.open_project(project_file=project_file)
    test_ComsolAdapter.close_project()

def test_ComsolAdapter_save_project():
    project_file = os.path.join(os.getcwd(), "comsol_source", "调制器截面仿真.mph")

    test_ComsolAdapter = ComsolAdapter(project_name="Comsol_Project")
    test_ComsolAdapter.open_project(project_file=project_file)

    project_newFile = os.path.join(os.getcwd(), "comsol_source", "调制器截面仿真_新.mph")
    test_ComsolAdapter.save_project_as(project_newFile=project_newFile)

    test_ComsolAdapter.close_project()

def test_ComsolAdapter_get_variables():
    project_file = os.path.join(os.getcwd(), "comsol_source", "调制器截面仿真.mph")

    test_ComsolAdapter = ComsolAdapter(project_name="Comsol_Project")
    test_ComsolAdapter.open_project(project_file=project_file)

    variables = test_ComsolAdapter.get_variables()
    for key, value in variables.items():
        print(key, value)

    test_ComsolAdapter.close_project()

def test_ComsolAdapter_set_variables():
    project_file = os.path.join(os.getcwd(), "comsol_source", "调制器截面仿真.mph")

    test_ComsolAdapter = ComsolAdapter(project_name="Comsol_Project")
    test_ComsolAdapter.open_project(project_file=project_file)

    print(" ------------------------- before set variable: ------------------------- ")
    variables = test_ComsolAdapter.get_variables()
    for key, value in variables.items():
        print(key, value)

    test_ComsolAdapter.set_variables("sio2h", "4.8[um]")

    print(" ------------------------- after set variable: ------------------------- ")
    variables = test_ComsolAdapter.get_variables()
    for key, value in variables.items():
        print(key, value)

    test_ComsolAdapter.close_project()

def test_ComsolAdapter_run_simulation():
    project_file = os.path.join(os.getcwd(), "comsol_source", "调制器截面仿真.mph")

    test_ComsolAdapter = ComsolAdapter(project_name="Comsol_Project")
    test_ComsolAdapter.open_project(project_file=project_file)

    test_ComsolAdapter.run_simulation()

    project_newFile = os.path.join(os.getcwd(), "comsol_source", "调制器截面仿真_结果.mph")
    test_ComsolAdapter.save_project_as(project_newFile=project_newFile)

    test_ComsolAdapter.close_project()

## ====================================================== Interconnect 测试代码 ======================================================

def test_Interconnect():
    test_InterconnectAdapter = InterconnectAdapter(project_name="Interconnect_Project")

def test_InterconnectAdapter_open_close():
    project_file = os.path.join(os.getcwd(), "interconnect_source", "modulator.icp")

    test_InterconnectAdapter = InterconnectAdapter(project_name="Interconnect_Project")
    test_InterconnectAdapter.open_project(project_file=project_file)

    test_InterconnectAdapter.close_project()

def test_InterconnectAdapter_save_project():
    project_file = os.path.join(os.getcwd(), "interconnect_source", "modulator.icp")

    test_InterconnectAdapter = InterconnectAdapter(project_name="Interconnect_Project")
    test_InterconnectAdapter.open_project(project_file=project_file)

    project_newFile = os.path.join(os.getcwd(), "interconnect_source", "modulator_new.icp")
    test_InterconnectAdapter.save_project_as(project_newFile=project_newFile)

    test_InterconnectAdapter.close_project()

def test_InterconnectAdapter_get_element_name_list():
    project_file = os.path.join(os.getcwd(), "interconnect_source", "modulator.icp")

    test_InterconnectAdapter = InterconnectAdapter(project_name="Interconnect_Project")
    test_InterconnectAdapter.open_project(project_file=project_file)
    ele_name_list = test_InterconnectAdapter.get_element_name_list()
    for item in ele_name_list:
        print(item)

    test_InterconnectAdapter.close_project()

def test_InterconnectAdapter_get_element_property():
    project_file = os.path.join(os.getcwd(), "interconnect_source", "modulator.icp")

    test_InterconnectAdapter = InterconnectAdapter(project_name="Interconnect_Project")
    test_InterconnectAdapter.open_project(project_file=project_file)
    property_list = test_InterconnectAdapter.get_element_property("CWL_1")
    print(property_list)
    print(type(property_list))

    property_value = test_InterconnectAdapter.get_element_property("CWL_1", "description")
    print("description: ", property_value)

    test_InterconnectAdapter.close_project()

def test_InterconnectAdapter_set_element_property():
    project_file = os.path.join(os.getcwd(), "interconnect_source", "modulator.icp")

    test_InterconnectAdapter = InterconnectAdapter(project_name="Interconnect_Project")
    test_InterconnectAdapter.open_project(project_file=project_file)

    print(" ------------------------- before set variable: ------------------------- ")
    property_value = test_InterconnectAdapter.get_element_property("TW_2", "description")
    print("description: ", property_value)

    test_InterconnectAdapter.set_element_property("TW_2", "description", "Traveling wave electrode transmission line filter 11111")

    print(" ------------------------- after set variable: ------------------------- ")
    property_value = test_InterconnectAdapter.get_element_property("TW_2", "description")
    print("description: ", property_value)

    test_InterconnectAdapter.close_project()

def test_InterconnectAdapter_run_simulation():
    project_file = os.path.join(os.getcwd(), "interconnect_source", "modulator.icp")

    test_InterconnectAdapter = InterconnectAdapter(project_name="Interconnect_Project")
    test_InterconnectAdapter.open_project(project_file=project_file)

    test_InterconnectAdapter.run_simulation()

    project_newFile = os.path.join(os.getcwd(), "interconnect_source", "modulator_result.icp")
    test_InterconnectAdapter.save_project_as(project_newFile=project_newFile)

    test_InterconnectAdapter.close_project()

if __name__ == "__main__":
    test_InterconnectAdapter_get_element_property()