from Modulator_HFSS import Modulator_HFSS
from Modulator_Comsol import Modulator_Comsol
from Modulator_Interconnect import Modulator_Interconnect

import os, sys
import time
os.add_dll_directory('F:\\devTool\\Lumerical\\v202\\api\\python')
sys.path.append("F:\\devTool\\Lumerical\\v202\\api\\python")
import traceback
import logging
from multiprocessing import  Process
import lumapi

def delete_files(directory):
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

def process_ENA_interconnect(dir_name, element_name):
    file_path = os.path.join(os.getcwd(), dir_name, element_name + ".csv")
    with open(file_path, 'r') as fd_csv:
        data_flag = False
        for line_index, line_content in enumerate(fd_csv.readlines()):
            line_content = line_content.replace('\n', '')
            if False == data_flag:
                if line_content == ".DATA":
                    data_flag = True
            else:
                if line_content.find(".HEADER") != -1:
                    break
                content_list = line_content.split(",")
                import math
                if len(content_list[-1]) != 0 and math.isclose(float(content_list[-1]), -3, abs_tol=0.2):
                    return float(content_list[0]) / 1e9

def hfss_simulation():
    print(" ------------------------------------------------ Start Hfss Simulation ------------------------------------------------ ")

    # ---------------------- hfss ----------------------
    hfss_modulator = Modulator_HFSS.Modulator_HFSS_Model(projectname="Modulator", designname="1mm")
    # 通过文件添加变量
    variable_file = os.path.join(os.getcwd(), "source", "hfss", "hfss_variables.txt")
    hfss_modulator.set_variable_by_file(variable_file=variable_file)
    # 添加 LINBO3
    material_name = "LINbO3"
    material_cfg_name = "permittivity"
    material_cfg_value = ['44.3', '44.3', '30']
    hfss_modulator.add_material(material_name=material_name, material_cfg_name=material_cfg_name,
                           material_cfg_value=material_cfg_value)
    # 添加坐标系
    hfss_modulator.add_coordinate_systems()
    # 创建模型
    hfss_modulator.create_model_solids()
    # 创建Port
    hfss_modulator.create_ports()
    # 设置边界
    hfss_modulator.create_boundaries()
    # 设置Analysis
    hfss_modulator.create_setup()
    # 验证并仿真
    validate_msg, validate_state = hfss_modulator.validate_check()
    if validate_state == True:
        print("hfss validata is OK")
        if hfss_modulator.run_analyze() == True:
            print("hfss run analyze finish")
        else:
            print("hfss run analyze failed")
            # del hfss_modulator
            hfss_modulator.close_project()
            return
    else:
        print("validata is Failed: ", validate_msg)
        # del hfss_modulator
        hfss_modulator.close_project()
        return

    # 创建报告
    export_file = os.path.join(os.getcwd(), "result", "aedt_output")
    delete_files(export_file)

    hfss_modulator.create_reports()
    hfss_modulator.export_reports(export_filename=export_file)
    project_filename = "Modulator_1mm_result.aedt"
    filepath = os.path.join(os.getcwd(), "result", project_filename)
    hfss_modulator.save_project(project_filename=filepath)
    # del hfss_modulator
    hfss_modulator.close_project()

    # 处理数据
    Modulator_HFSS.process_aedt_data(export_filename=export_file)

    print(" ------------------------------------------------ End Hfss Simulation ------------------------------------------------ ")

def comsol_simulation():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    print(" ------------------------------------------------ Start Comsol Simulation ------------------------------------------------ ")

    # ---------------------- Comsol ----------------------
    comsol_modulator = Modulator_Comsol.Modulator_Comsol_Model(project_name="调制器截面仿真")
    filepath = os.path.join(os.getcwd(), "source", "comsol", "parameters.txt")
    comsol_modulator.load_parameters(parameters_filename=filepath)
    filepath = os.path.join(os.getcwd(), "source", "comsol", "parameters_case.txt")
    comsol_modulator.create_parameters_case(case_name="实例1", parameters_filename=filepath)
    comsol_modulator.create_geometries()
    filepath = os.path.join(os.getcwd(), "source", "comsol", "Comsol_Material_modulator.xml")
    comsol_modulator.import_material(comp_name="comp1", xmlfile=filepath)
    comsol_modulator.set_material()
    comsol_modulator.create_Electrostatics()
    comsol_modulator.create_EWFD()
    comsol_modulator.create_Mesh()
    comsol_modulator.create_Study()
    comsol_modulator.create_Definitions()
    comsol_modulator.run_build_mesh_solve()

    export_path = os.path.join(os.getcwd(), "result", "comsol_output", "modulator_ret.txt")
    # comsol_modulator.create_resutl_table(export_path)
    comsol_modulator.create_resutl_table_2(export_path)

    project_name = os.path.join(os.getcwd(), "result", "调制器截面仿真.mph")
    comsol_modulator.save_project(project_name)


    input_path = os.path.join(os.getcwd(), "result", "comsol_output", "modulator_ret.txt")
    output_path = os.path.join(os.getcwd(), "result", "comsol_output", "comsol_ret.txt")
    Modulator_Comsol.process_data(input_path=input_path, output_path=output_path)

    print(" ------------------------------------------------ End Comsol Simulation ------------------------------------------------ ")

def interconnect_simulation_step_1():
    print(" ------------------------------------------------ Start Interconnect Simulation Modulator ------------------------------------------------ ")

    # ---------------------- Interconnect ----------------------
    def set_property(interconnect: lumapi.INTERCONNECT):
        filepath = os.path.join(os.getcwd(), "result", "comsol_output")

        interconnect.select("OM_1")
        interconnect.set("measurement filename", os.path.join(filepath, 'comsol_ret.txt'))

        interconnect.select("OM_2")
        interconnect.set("measurement filename", os.path.join(filepath, 'comsol_ret.txt'))

        filepath = os.path.join(os.getcwd(), "result", "aedt_output")
        interconnect.select("TW_2")
        interconnect.set("loss filename", os.path.join(filepath, 'loss.dat'))
        interconnect.set("characteristic impedance filename", os.path.join(filepath, 'Port Zo.dat'))
        interconnect.set("microwave index filename", os.path.join(filepath, 'neff.dat'))


    testModel = Modulator_Interconnect.InterconnectModel()

    filepath = os.path.join(os.getcwd(), "source", "interconnect", "Interconnect_modulator_step_1.xml")
    testModel.load_cfg(xmlfile=filepath)
    testModel.set_property(set_property)
    testModel.run_simulation()
    testModel.save_project(project_name='modulator')

    print(" ------------------------------------------------ End Interconnect Simulation Modulator ------------------------------------------------ ")

def interconnect_simulation_step_2():
    print(" ------------------------------------------------ Start Interconnect Simulation ENA ------------------------------------------------ ")

    def set_property(interconnect: lumapi.INTERCONNECT):
        filepath = os.getcwd()
        filepath = os.path.join(filepath, 'result', 'aedt_output')

        interconnect.select("TW_1")
        interconnect.set("loss filename", os.path.join(filepath, 'loss.dat'))
        interconnect.set("characteristic impedance filename", os.path.join(filepath, 'Port Zo.dat'))
        interconnect.set("microwave index filename", os.path.join(filepath, 'neff.dat'))


    testModel = Modulator_Interconnect.InterconnectModel()

    filepath = os.getcwd()
    filepath = os.path.join(filepath, 'source', "interconnect", 'Interconnect_modulator_step_2.xml')
    testModel.load_cfg(xmlfile=filepath)
    testModel.set_property(set_property)
    testModel.run_simulation()
    testModel.save_project(project_name='modulator_ENA')

    dir_name = "result_ENA_1"
    element_name = "ENA_1"
    testModel.export_result(dir_name, element_name)

    print(" ------------------------------------------------ End Interconnect Simulation ENA ------------------------------------------------ ")

################## 联合仿真 ##################
def combine_simulation():

    try:
        hfss_simulation()
        comsol_process = Process(target=comsol_simulation)
        comsol_process.start()
        comsol_process.join()

        interconnect_simulation_step_1()
    except:
        traceback.print_exc()

    # dir_name = "result_ENA_1"
    # element_name = "ENA_1"
    # return process_ENA_interconnect(dir_name, element_name)

def main():

    combine_simulation()


if __name__ == "__main__":
    main()
