import logging
import os.path
import queue
from multiprocessing import Process
from PyQt5 import QtCore

import SimulationAdapter

# class ProjectDict(QtCore.QObject):
#
#     def __init__(self):
#         super().__init__()
#
#         self.project_dict = dict()

class ProjectLoader(QtCore.QThread):

    project_loader_notifier = QtCore.pyqtSignal(str, str)

    def __init__(self, prj_manager):
        super().__init__()
        self.prj_manager = prj_manager
        self.project_path = None
        self.project_name = None
        self.project_type = None

    def set_cfg(self, project_path, project_name, project_type):
        self.project_path = project_path
        self.project_name = project_name
        self.project_type = project_type

    def run(self) -> None:
        logging.info("%s, %s %s" % (self.project_path, self.project_name, self.project_type))
        adapter = SimulationAdapter.simulationAdapterFactory.produce_adapter(project_name=self.project_name, type=self.project_type)

        info = dict()
        info["adapter"] = adapter
        info["project path"] = self.project_path
        sub_path = self.project_path.split(".", 1)
        info["project result path"] = sub_path[0] + "_result." + sub_path[-1]
        info["project type"] = self.project_type
        self.prj_manager.project_dict[self.project_name] = info
        adapter.open_project(self.project_path)
        if adapter.type == "Interconnect":
            # 将 Interconnect 的 element及property 保存到文件中
            interconnect_property_tmpFile = os.path.join(os.getcwd(), "tmp", self.project_name + "_property.xml")
            if os.path.exists(interconnect_property_tmpFile) is True:
                os.remove(interconnect_property_tmpFile)

            import xml.etree.ElementTree as ET
            declaration = ET.Element('?xml')
            declaration.attrib['version'] = '1.0'
            declaration.attrib['encoding'] = 'UTF-8'
            # 创建ElementTree对象
            tree = ET.ElementTree(declaration)

            root = ET.Element('root')
            elements = adapter.get_element_name_list()
            for ele_item in elements:
                # print("======================= %s =======================" % ele_item)
                element = ET.SubElement(root, 'element', {'name': ele_item})
                property_list = adapter.get_element_property(ele_item)
                for property_item in property_list:
                    # print("---------------- %s ----------------" % property_item)
                    property_value = adapter.get_element_property(ele_item, property_item)
                    porperty = ET.SubElement(element, 'porperty', {'name': property_item})

            tree = ET.ElementTree(root)
            tree.write(interconnect_property_tmpFile, encoding='UTF-8', xml_declaration=True)

        self.project_loader_notifier.emit(self.project_name, self.project_type)

def run_simulation_function(prj_name, prj_type, prj_path, prj_result_path):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    logging.info("%s, %s, %s" % (prj_name, prj_path, prj_result_path))
    adapter = SimulationAdapter.simulationAdapterFactory.produce_adapter(project_name=prj_name, type=prj_type)
    adapter.open_project(prj_path)
    adapter.run_simulation()
    adapter.save_project_as(project_newFile=prj_result_path)
    adapter.close_project()

class ProjectManager(QtCore.QObject):

    project_manager_notifier = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.HFSS_count = 0
        self.Comsol_count = 0
        self.Interconnect_count = 0
        self.loader_thread = ProjectLoader(self)
        self.loader_thread.project_loader_notifier.connect(self.load_project_finish)
        self.project_dict = dict()

    def load_project(self, project_path, project_type):
        # comsol 对象为单例，目前只能加载一个comsol project
        logging.info("load %s project from %s" % (project_type, project_path))
        project_name = self.initProjectName(project_type)

        """
        # adapter = SimulationAdapter.simulationAdapterFactory.produce_adapter(project_name=project_name, type=project_type)
        # if adapter.type == "HFSS":
        #     project_dict[project_name] = adapter
        #     adapter.open_project(project_path)
        # elif adapter.type == "Comsol":
        #     project_dict[project_name] = adapter
        #     adapter.open_project(project_path)
        # elif adapter.type == "Interconnect":
        #     project_dict[project_name] = adapter
        #     adapter.open_project(adapter)
        """

        self.loader_thread.set_cfg(project_path, project_name, project_type)
        self.loader_thread.start()

    def load_project_finish(self, project_name, project_type):
        logging.info("load %s project finished" % (project_name))
        self.project_manager_notifier.emit(project_name, project_type)

    def close_project(self):
        # 遍历项目字典关闭所有项目
        for prjName, prjInfo in self.project_dict.items():
            logging.info("close %s project" % prjName)
            prjInfo["adapter"].close_project()

    def initProjectName(self, project_type: str) -> str:
        if project_type == "HFSS":
            self.HFSS_count += 1
            return "HFSS_Project_" + str(self.HFSS_count)
        elif project_type == "Comsol":
            self.Comsol_count += 1
            return "Comsol_Project_" + str(self.Comsol_count)
        elif project_type == "Interconnect":
            self.Interconnect_count += 1
            return "Interconnect_Project_" + str(self.Interconnect_count)

    def get_variables(self, project_name):
        prjAdapter = self.project_dict[project_name]["adapter"]
        variables = prjAdapter.get_variables()

        # variables = {
        #     'd_si': '675um',
        #     'd_sioup': '0.8um',
        #     'd_ln': '0.4um',
        #     'd_lnbd': '0.2um',
        #     'd_au': '900nm',
        #     'd_siodw': '4.7um',
        #     'w_sig': '11um',
        #     'gap': '5um',
        #     'ly': '1000um',
        #     'LNBDSW': '1.4um',
        #     'theta1': '60deg',
        #     'w_au': '130um',
        #     'w_sig2': '45um',
        #     'gap2': '25um',
        #     'l_taper': '30um',
        #     'r_bend': '100um',
        #     'l_tanzhen': '500um',
        #     'x_z': '15um',
        #     'w_s': '100um',
        #     'w_t': '0.4um',
        #     'w_t1': '0.2um',
        #     'r2': '40um',
        #     'l_all': 'ly+l_tanzhen*2',
        #     'l_shouzhai': 'l_taper/2+30um',
        #     'l': 'w_au*2+gap*2+w_sig+l_shouzhai*2+2*l_taper',
        #     'LNBDXW': 'd_lnbd/tan(theta1)*2+LNBDSW',
        #     'w_t2': '0.5*(gap-LNBDXW-w_t*2-w_t1*2)',
        #     'sioxw': 'gap-w_t2*2',
        #     'siosw': 'sioxw-d_sioup/tan(theta1)*2'
        # }

        # print(variables)
        return variables

    def get_elements(self, project_name):
        import xml.etree.ElementTree as ET

        base_dir = os.path.join(os.getcwd(), "tmp")
        property_file = None
        for file in os.listdir(base_dir):
            if file[:-13] == project_name:
                property_file = file
                break

        elements = dict()
        property_file = os.path.join(base_dir, property_file)
        cfgTree = ET.parse(property_file)
        root = cfgTree.getroot()
        for element in root.findall("element"):
            ele_attribute = element.attrib
            # print(ele_attribute['name'])
            element_property = list()
            for property in list(element):
                attribute = property.attrib
                # print(attribute['name'])
                element_property.append(attribute['name'])
            elements[ele_attribute['name']] = element_property

        return elements

    def delete_files(self, directory):
        """
        清空目录下的文件
        :param directory:
        :return:
        """
        file_list = os.listdir(directory)
        for file in file_list:
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def process_aedt_data(self, import_dir, file_name):

        file_sub = file_name.split(".", 1)
        file_type = file_sub[0]

        files = [os.path.join(import_dir, file) for file in os.listdir(import_dir)]
        for file in files:
            if os.path.splitext(file)[-1] == ".csv":
                print(file)
                fd_csv = open(file, 'r')

                fd_dat = None
                for line_index, line_content in enumerate(fd_csv.readlines()):
                    # print(line_index, line_content)
                    if line_index == 0:
                        if line_content.find(file_type) != -1:
                            fd_dat = open(os.path.join(import_dir, file_name), "w")
                        else:
                            break
                        # if line_content.find('loss') != -1:
                        #     fd_dat = open(os.path.join(import_dir, "loss.dat"), "w")
                        # elif line_content.find('neff') != -1:
                        #     fd_dat = open(os.path.join(import_dir, "neff.dat"), "w")
                        # elif line_content.find('Zo(1)') != -1:
                        #     fd_dat = open(os.path.join(import_dir, "Port Zo.dat"), "w")
                    else:
                        line_content = line_content.replace(',', ' ')
                        line_content = line_content.replace(' + ', ' ')
                        line_content = line_content.replace('i', '')
                        fd_dat.writelines(line_content)

                if fd_dat is not None:
                    fd_dat.close()

                fd_csv.close()

        return os.path.join(import_dir, file_name)

    def process_comsol_data(self, input_path, output_path):
        import re

        fd_input = open(input_path, encoding='gb18030', errors='ignore')
        fd_ouput = open(output_path, 'w')
        for line_index, line_content in enumerate(fd_input.readlines()):
            if line_index < 5:
                continue

            content_after = re.sub(' +', ' ', line_content)
            content_after = content_after.replace('\n', '')
            content_list = content_after.split(' ')
            content = content_list[0] + ' ' + content_list[3] + ' ' + content_list[2] + '\n'
            fd_ouput.writelines(content)

        fd_input.close()
        fd_ouput.close()

    def run_simulation(self, task_q: queue.Queue):
        while(task_q.empty() == False):
            item = task_q.get()
            logging.info(item)
            if item["type"] == "project":
                prj_info = self.project_dict[item["project name"]]
                if prj_info["project type"] == "Comsol" or prj_info["project type"] == "HFSS":
                    prj_info["adapter"].close_project()
                    simulation_process = Process(target=run_simulation_function,
                                                 args=(item["project name"],
                                                       prj_info["project type"],
                                                       prj_info["project path"],
                                                       prj_info["project result path"]))
                    simulation_process.start()
                    simulation_process.join()
                elif prj_info["project type"] == "Interconnect":
                    adapter = prj_info["adapter"]
                    adapter.run_simulation()
                    adapter.save_project_as(project_newFile=prj_info["project result path"])
                    adapter.close_project()
            elif item["type"] == "path":

                if item["start setting"]["project type"] == "HFSS":
                    prj_info = self.project_dict[item["start setting"]["project name"]]
                    # 1. 清空导出文件目录
                    export_file = item["start setting"]["export dirction"]
                    logging.info("clean export directory: %s" % export_file)
                    self.delete_files(export_file)
                    # 2. 打开仿真完的仿真文件
                    adapter = SimulationAdapter.simulationAdapterFactory.produce_adapter(project_name=item["start setting"]["project name"],
                                                                                         type=prj_info["project type"])
                    adapter.open_project(prj_info["project result path"])
                    # 3. 创建报告
                    for report_item in item["start setting"]["report info list"]:
                        if report_item["user define"] == True:
                            adapter.create_output_variable(variable=report_item["report name"],
                                                           expression=report_item["expression"],
                                                           solution=report_item["solution"])

                    for report_item in item["start setting"]["report info list"]:
                        adapter.create_report(expressions=report_item["report name"])
                    # 4. 设置导出路径
                    adapter.export_report(export_path=export_file)
                    adapter.close_project()
                elif item["start setting"]["project type"] == "Comsol":
                    prj_info = self.project_dict[item["start setting"]["project name"]]
                    # 1. 清空导出文件目录
                    export_file = item["start setting"]["export dirction"]
                    logging.info("clean export directory: %s" % export_file)
                    self.delete_files(export_file)
                    # 2. 打开仿真完的仿真文件
                    # adapter = SimulationAdapter.simulationAdapterFactory.produce_adapter(project_name=item["start setting"]["project name"],
                    #                                                                      type=prj_info["project type"])
                    adapter = prj_info["adapter"]
                    adapter.open_project(prj_info["project result path"])
                    # 3. 创建报告
                    report_list = list()
                    for key, item_value in item["start setting"]["item dict"].items():
                        numerical_name = item_value["numerical name"]
                        numerical_type = item_value["numerical type"]
                        data_type = item_value["data type"]
                        table_name = item_value["table name"]
                        table_comment = item_value["table comment"]
                        expression_list = item_value["expression list"]

                        adapter.result_numerical_create(numerical_name, numerical_type)
                        for index in range(len(expression_list)):
                            adapter.result_numerical_setIndex(numerical_name, expression_list[index], index)
                        adapter.result_numerical_setData(numerical_name, data_type)
                        adapter.result_table_create(table_name, "Table")
                        adapter.result_table_comments(table_name, table_comment)
                        adapter.result_numerical_set_table(numerical_name, table_name)
                        adapter.result_numerical_setResult(numerical_name)
                        export_path = os.path.join(export_file, item_value["export file"])
                        adapter.result_table_set_export_path(table_name, export_path)
                        report_list.append(export_path)

                    for report_index in range(len(report_list)):
                        self.process_comsol_data(report_list[report_index], os.path.join(export_file, item["end setting"]["file list"][report_index]))

                    adapter.close_project()

                if item["end setting"]["project_type"] == "Interconnect":
                    import_dirction = item["end setting"]["import dirction"]
                    logging.info("element list: %s" % item["end setting"]["import list"])
                    logging.info("property list: %s" % item["end setting"]["property list"])
                    logging.info("file list: %s" % item["end setting"]["file list"])
                    processed_file_list = []
                    if item["start setting"]["project type"] == "HFSS":
                        for file_item in item["end setting"]["file list"]:
                            ret = self.process_aedt_data(import_dirction, file_item)
                            if ret != None:
                                processed_file_list.append(ret)
                    elif item["start setting"]["project type"] == "Comsol":
                        for file_item in item["end setting"]["file list"]:
                            processed_file_list.append(os.path.join(import_dirction, file_item))

                    logging.info("input full path: %s" % processed_file_list)

                    prj_info = self.project_dict[item["end setting"]["project name"]]
                    adapter = prj_info["adapter"]

                    for index in range(len(item["end setting"]["import list"])):
                        element_name = item["end setting"]["import list"][index]
                        property_name = item["end setting"]["property list"][index]
                        property_value = processed_file_list[index]
                        adapter.set_element_property(element_name=element_name,
                                                     property_name=property_name,
                                                     property_value=property_value)


projectManagerSingleton = ProjectManager()