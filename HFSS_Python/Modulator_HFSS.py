import time

import pyaedt
from pyaedt import Hfss
import os

class Modulator_HFSS_Model:
    """
    创建铌酸锂调制器模型
    """
    def __init__(self, projectname="tmpProject", designname="tmpDesign"):

        if projectname is not None and designname is not None:
            self.aedtapp = Hfss(projectname=projectname,
                                designname=designname,
                                non_graphical=False,
                                new_desktop_session=True,
                                close_on_exit=True)
        else:
            self.aedtapp = Hfss()

    # def __del__(self):
    #     print("close project")
    #     self.aedtapp.close_desktop()

    def close_project(self):
        print("close project")
        self.aedtapp.close_desktop()

    def save_project(self, project_filename):
        """
        保存工程文件
        :param project_filename: 工程文件完整路径名
        :return:
        """

        if project_filename is None:
            print("project file name is None")
            return

        self.aedtapp.save_project(project_file=project_filename)

    def set_variable(self, variable_name, expression):
        """
        添加变量，如果变量不存在则添加，如果存在则修改值
        :param variable_name: 变量名
        :param expression: 变量值
        :return:
        """
        self.aedtapp.variable_manager.set_variable(variable_name=variable_name, expression=expression)

    def get_variable(self, variable_name):
        """
        获取变量名的表达式
        :param variable_name: 变量名
        :return:
        """
        return self.aedtapp.variable_manager.get_expression(variable_name=variable_name)

    def set_variable_by_file(self, variable_file):
        """
        通过文件添加变量
        :param variable_file: 文件路径
        :return:
        """
        if variable_file is None:
            print("variables file path is None")
            return

        # variables_fd = open(variable_file, mode="r")
        with open(variable_file, mode="r") as variables_fd:
            for line_index, line_context in enumerate(variables_fd.readlines()):
                list_context = line_context.split("\t")
                if list_context[0] == "Name":
                    continue

                if 0 == len(list_context[2]):
                    self.set_variable(variable_name=list_context[0], expression=list_context[1])
                else:
                    self.set_variable(variable_name=list_context[0], expression=list_context[3])

        # variables_fd.close()

    def add_material(self, material_name, material_cfg_name, material_cfg_value):
        """
        添加材料
        :param material_name: 材料名称
        :param material_cfg_name: 属性
        :param material_cfg_value: 属性值
        :return:
        """

        print(material_name, material_cfg_name, material_cfg_value)
        mat = self.aedtapp.materials.add_material(material_name)
        attrib = getattr(mat, material_cfg_name)
        attrib = material_cfg_value

    def add_coordinate_systems(self):
        """
        添加坐标系
        """
        self.aedtapp.modeler.create_coordinate_system(
            origin=["0mm", "(l-w_sig-gap*2-w_au*2)/2", "d_si+d_siodw+d_ln+d_au"],
            reference_cs="Global",
            name="RelativeCS1",
            x_pointing=[1, 0, 0],
            y_pointing=[0, 1, 0]
        )

    def create_model_solids_aluminum(self):

        self.aedtapp.modeler.set_working_coordinate_system("Global")
        position = ["0mm", "(l-w_sig-gap*2-w_au*2)/2+r2", "d_si+d_siodw+d_ln"]
        dimensions_list = ["ly", "w_au-r2", "d_au"]
        # self.aedtapp.modeler.create_box(position=position, dimensions_list=dimensions_list, name="Box1", matname="aluminum")
        self.aedtapp.modeler.create_box(origin=position, sizes=dimensions_list, name="Box1", material="aluminum")
        # self.aedtapp.modeler.duplicate_along_line(objid="Box1", vector=["0mm", "w_au-r2+w_sig+gap*2", "0mm"], attachObject=True)
        self.aedtapp.modeler.duplicate_along_line(assignment="Box1", vector=["0mm", "w_au-r2+w_sig+gap*2", "0mm"], attach=True)
        self.aedtapp.modeler["Box1"].color = [255, 128, 64]
        self.aedtapp.modeler["Box1"].transparency = 0


        point_list = [["0mm", "(l-w_sig-gap*2-w_au*2)/2", "d_si+d_siodw+d_ln+d_au"],
                     ["0mm", "(l-w_sig-gap*2-w_au*2)/2+w_au", "d_si+d_siodw+d_ln+d_au"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list, name="Polyline1")
        self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline1")
        self.aedtapp.modeler.set_working_coordinate_system("RelativeCS1")
        # self.aedtapp.modeler.sweep_around_axis(objid="Polyline1", cs_axis="Z", sweep_angle=90, draft_angle=0)
        self.aedtapp.modeler.sweep_around_axis(assignment="Polyline1", axis="Z", sweep_angle=90, draft_angle=0)

        self.aedtapp.modeler.set_working_coordinate_system("Global")
        point_list = [["0mm", "(l-w_sig-gap*2-w_au*2)/2+r2", "d_si+d_siodw+d_ln+d_au"],
                      ["0mm", "(l-w_sig-gap*2-w_au*2)/2", "d_si+d_siodw+d_ln+d_au"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list, name="Polyline18")
        self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline18")
        self.aedtapp.modeler.set_working_coordinate_system("RelativeCS1")
        # self.aedtapp.modeler.sweep_around_axis(objid="Polyline18", cs_axis="Z", sweep_angle=90, draft_angle=0)
        self.aedtapp.modeler.sweep_around_axis(assignment="Polyline18", axis="Z", sweep_angle=90, draft_angle=0)
        self.aedtapp.modeler.subtract(blank_list="Polyline1", tool_list=["Polyline18"], keep_originals=False)

        point_list = [["-w_au", "0mm", "0mm"],
                      ["-w_au+(w_sig2-w_sig)/2+gap2-gap", "-l_shouzhai", "0mm"],
                      ["-w_au+(w_sig2-w_sig)/2+gap2-gap", "-l_taper-l_shouzhai", "0mm"],
                      ["ly+w_au*2+gap*2+w_sig+ w_s", "-l_taper-l_shouzhai", "0mm"],
                      ["ly+w_au*2+gap*2+w_sig+ w_s", "0mm", "0mm"],
                      ["-w_au", "0mm", "0mm"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list, name="Polyline16")
        self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline16")
        # self.aedtapp.modeler.cover_lines(selection="Polyline16")
        self.aedtapp.modeler.cover_lines(assignment="Polyline16")
        # self.aedtapp.modeler.duplicate_around_axis(objid="Polyline16", cs_axis="Z", angle=180)

        point_list = [["-w_au+(w_au-r2)", "0mm", "0mm"],
                      ["-w_au+(w_sig2-w_sig)/2+gap2-gap+(w_au-r2)", "-l_shouzhai", "0mm"],
                      ["-w_au+(w_sig2-w_sig)/2+gap2-gap+(w_au-r2)", "-l_taper-l_shouzhai", "0mm"],
                      ["ly+w_au*2+gap*2+w_sig+ w_s", "-l_taper-l_shouzhai", "0mm"],
                      ["ly+w_au*2+gap*2+w_sig+ w_s", "0mm", "0mm"],
                      ["-w_au+(w_au-r2)", "0mm", "0mm"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list, name="Polyline20")
        self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline20")
        # self.aedtapp.modeler.cover_lines(selection="Polyline20")
        self.aedtapp.modeler.cover_lines(assignment="Polyline20")
        self.aedtapp.modeler.subtract(blank_list="Polyline16", tool_list=["Polyline20"], keep_originals=False)
        # self.aedtapp.modeler.unite(unite_list=["Polyline1", "Polyline16"])
        self.aedtapp.modeler.unite(assignment=["Polyline1", "Polyline16"])
        # self.aedtapp.modeler.thicken_sheet(objid="Polyline1", thickness="-d_au")
        self.aedtapp.modeler.thicken_sheet(assignment="Polyline1", thickness="-d_au")
        # self.aedtapp.modeler.duplicate_around_axis(objid="Polyline1", cs_axis="Z", angle=180)
        self.aedtapp.modeler.duplicate_around_axis(assignment="Polyline1", axis="Z", angle=180)
        # self.aedtapp.modeler.move(objid="Polyline1_1", vector=["ly", "w_au*2+gap*2+w_sig", "0mm"])
        self.aedtapp.modeler.move(assignment="Polyline1_1", vector=["ly", "w_au*2+gap*2+w_sig", "0mm"])

        self.aedtapp.modeler.set_working_coordinate_system("Global")
        point_list = [["0mm", "(l-w_sig-gap*2-w_au*2)/2+w_au-r2+gap+w_sig+gap+w_au", "d_si+d_siodw+d_ln+d_au"],
                      ["0mm", "(l-w_sig-gap*2-w_au*2)/2+w_au+gap+w_sig+gap", "d_si+d_siodw+d_ln+d_au"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list, name="Polyline4")
        self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline4")
        self.aedtapp.modeler.set_working_coordinate_system("RelativeCS1")
        # self.aedtapp.modeler.sweep_around_axis(objid="Polyline4", cs_axis="Z", sweep_angle=90, draft_angle=0)
        self.aedtapp.modeler.sweep_around_axis(assignment="Polyline4", axis="Z", sweep_angle=90, draft_angle=0)
        # self.aedtapp.modeler.duplicate_around_axis(objid="Polyline4", cs_axis="Z", angle=180)

        point_list = [["-w_au-w_sig-gap*2", "0mm", "0mm"],
                      ["-w_au-w_sig-gap-(w_sig2-w_sig)/2-gap2", "-l_shouzhai", "0mm"],
                      ["-w_au-w_sig-gap-(w_sig2-w_sig)/2-gap2", "-l_taper-l_shouzhai", "0mm"],
                      ["-w_au-w_sig-gap-(w_sig2-w_sig)/2-gap2-(w_au-r2)", "-l_taper-l_shouzhai", "0mm"],
                      ["-w_au-w_sig-gap-(w_sig2-w_sig)/2-gap2-(w_au-r2)", "-l_shouzhai", "0mm"],
                      ["-w_au-w_sig-gap*2-(w_au-r2)", "0mm", "0mm"],
                      ["-w_au-w_sig-gap*2", "0mm", "0mm"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list, name="Polyline13")
        self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline13")
        # self.aedtapp.modeler.cover_lines(selection="Polyline13")
        self.aedtapp.modeler.cover_lines(assignment="Polyline13")
        # self.aedtapp.modeler.unite(unite_list=["Polyline4", "Polyline13"])
        self.aedtapp.modeler.unite(assignment=["Polyline4", "Polyline13"])
        # self.aedtapp.modeler.thicken_sheet(objid="Polyline4", thickness="d_au")
        self.aedtapp.modeler.thicken_sheet(assignment="Polyline4", thickness="d_au")
        # self.aedtapp.modeler.duplicate_around_axis(objid="Polyline4", cs_axis="Z", angle=180)
        self.aedtapp.modeler.duplicate_around_axis(assignment="Polyline4", axis="Z", angle=180)
        # self.aedtapp.modeler.move(objid="Polyline4_1", vector=["ly", "w_au*2+gap*2+w_sig", "0mm"])
        self.aedtapp.modeler.move(assignment="Polyline4_1", vector=["ly", "w_au*2+gap*2+w_sig", "0mm"])

        # self.aedtapp.modeler.unite(unite_list=["Box1", "Polyline1", "Polyline4", "Polyline1_1", "Polyline4_1"])
        self.aedtapp.modeler.unite(assignment=["Box1", "Polyline1", "Polyline4", "Polyline1_1", "Polyline4_1"])

        self.aedtapp.modeler.set_working_coordinate_system("Global")
        position = ["0mm", "(l-w_sig-gap*2-w_au*2)/2+gap+w_au", "d_si+d_siodw+d_ln"]
        dimensions_list = ["ly", "w_sig", "d_au"]
        # self.aedtapp.modeler.create_box(position=position, dimensions_list=dimensions_list, name="Box2", matname="aluminum")
        self.aedtapp.modeler.create_box(origin=position, sizes=dimensions_list, name="Box2", material="aluminum")
        self.aedtapp.modeler["Box2"].color = [255, 128, 64]
        self.aedtapp.modeler["Box2"].transparency = 0

        self.aedtapp.modeler.set_working_coordinate_system("RelativeCS1")
        point_list = [["-w_au-w_sig-gap", "0mm", "0mm"],
                      ["-w_au-gap", "0mm" , "0mm"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list, name="Polyline12")
        self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline12")

        point_list = [["-w_au-w_sig-gap", "0mm", "0mm"],
                      ["-w_au-w_sig-gap-(w_sig2-w_sig)/2", "-l_shouzhai", "0mm"],
                      ["-w_au-w_sig-gap-(w_sig2-w_sig)/2", "-l_shouzhai-l_taper", "0mm"],
                      ["-w_au-w_sig-gap-(w_sig2-w_sig)/2+w_sig2", "-l_taper-l_shouzhai", "0mm"],
                      ["-w_au-w_sig-gap-(w_sig2-w_sig)/2+w_sig2", "-l_shouzhai", "0mm"],
                      ["-w_au-gap", "0mm", "0mm"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list, name="Polyline17")
        self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline17")
        # self.aedtapp.modeler.unite(unite_list=["Polyline12", "Polyline17"])
        self.aedtapp.modeler.unite(assignment=["Polyline12", "Polyline17"])
        # self.aedtapp.modeler.cover_lines(selection="Polyline12")
        self.aedtapp.modeler.cover_lines(assignment="Polyline12")

        self.aedtapp.modeler.set_working_coordinate_system("Global")
        point_list = [["0mm", "(l-w_sig-gap*2-w_au*2)/2+w_au+gap+w_sig", "d_si+d_siodw+d_ln+d_au"],
                      ["0mm", "(l-w_sig-gap*2-w_au*2)/2+w_au+gap", "d_si+d_siodw+d_ln+d_au"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list, name="Polyline3")
        self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline3")
        self.aedtapp.modeler.set_working_coordinate_system("RelativeCS1")
        # self.aedtapp.modeler.sweep_around_axis(objid="Polyline3", cs_axis="Z", sweep_angle=90, draft_angle=0)
        self.aedtapp.modeler.sweep_around_axis(assignment="Polyline3", axis="Z", sweep_angle=90, draft_angle=0)
        # self.aedtapp.modeler.unite(unite_list=["Polyline12", "Polyline3"])
        self.aedtapp.modeler.unite(assignment=["Polyline12", "Polyline3"])
        # self.aedtapp.modeler.duplicate_around_axis(objid="Polyline12", cs_axis="Z", angle=180)
        self.aedtapp.modeler.duplicate_around_axis(assignment="Polyline12", axis="Z", angle=180)
        # self.aedtapp.modeler.thicken_sheet(objid="Polyline12", thickness="d_au")
        self.aedtapp.modeler.thicken_sheet(assignment="Polyline12", thickness="d_au")
        # self.aedtapp.modeler.move(objid="Polyline12_1", vector=["ly", "w_au*2+gap*2+w_sig", "0mm"])
        self.aedtapp.modeler.move(assignment="Polyline12_1", vector=["ly", "w_au*2+gap*2+w_sig", "0mm"])
        # self.aedtapp.modeler.thicken_sheet(objid="Polyline12_1", thickness="d_au")
        self.aedtapp.modeler.thicken_sheet(assignment="Polyline12_1", thickness="d_au")
        # self.aedtapp.modeler.unite(unite_list=["Box2", "Polyline12", "Polyline12_1"])
        self.aedtapp.modeler.unite(assignment=["Box2", "Polyline12", "Polyline12_1"])

    def create_model_solids_LINBO3_step_1(self):
        self.aedtapp.modeler.set_working_coordinate_system("Global")

        point_list = [["0mm", "(l-w_sig-gap*2-w_au*2)/2+w_au+gap/2", "d_si+d_siodw+d_ln+d_lnbd/2"],
                      ["ly", "(l-w_sig-gap*2-w_au*2)/2+w_au+gap/2", "d_si+d_siodw+d_ln+d_lnbd/2"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list,
        #                                      name="LNBD1",
        #                                      matname="LINBO3",
        #                                      xsection_type="Isosceles Trapezoid",
        #                                      xsection_orient="Auto",
        #                                      xsection_width="LNBDXW",
        #                                      xsection_topwidth="LNBDSW",
        #                                      xsection_height="d_lnbd",
        #                                      xsection_bend_type="Corner")
        self.aedtapp.modeler.create_polyline(points=point_list,
                                             name="LNBD1",
                                             material="LINBO3",
                                             xsection_type="Isosceles Trapezoid",
                                             xsection_orient="Auto",
                                             xsection_width="LNBDXW",
                                             xsection_topwidth="LNBDSW",
                                             xsection_height="d_lnbd",
                                             xsection_bend_type="Corner")
        # self.aedtapp.modeler.duplicate_along_line(objid="LNBD1", vector=["0mm", "w_sig+gap", "0mm"], attachObject=True)
        self.aedtapp.modeler.duplicate_along_line(assignment="LNBD1", vector=["0mm", "w_sig+gap", "0mm"], attach=True)
        self.aedtapp.modeler["LNBD1"].color = [128, 64, 64]
        self.aedtapp.modeler["LNBD1"].transparency = 0.6

    def create_model_solids_LINBO3_step_2(self):
        self.aedtapp.modeler.set_working_coordinate_system("Global")

        # obj = self.aedtapp.modeler.create_object_from_face(face=[self.aedtapp.modeler["SIOdw"].top_face_z],
        #                                                    non_model=False)
        obj = self.aedtapp.modeler.create_object_from_face(assignment=[self.aedtapp.modeler["SIOdw"].top_face_z],
                                                           non_model=False)
        obj.name = "LN"
        # self.aedtapp.modeler.thicken_sheet(objid="LN", thickness="d_ln")
        self.aedtapp.modeler.thicken_sheet(assignment="LN", thickness="d_ln")
        self.aedtapp.modeler["LN"].material_name = "LINBO3"
        self.aedtapp.modeler["LN"].color = [128, 64, 64]
        self.aedtapp.modeler["LN"].transparency = 0.6

    def create_model_solids_silicon(self):
        self.aedtapp.modeler.set_working_coordinate_system("Global")

        position = ["-l_tanzhen", "0mm", "0mm"]
        dimensions_list = ["l_all", "l", "d_si"]
        # self.aedtapp.modeler.create_box(position=position, dimensions_list=dimensions_list, name="si", matname="silicon")
        self.aedtapp.modeler.create_box(origin=position, sizes=dimensions_list, name="si", material="silicon")
        self.aedtapp.modeler["si"].color = [143, 175, 143]
        self.aedtapp.modeler["si"].transparency = 0

    def create_model_solids_silicon_dioxide(self):
        self.aedtapp.modeler.set_working_coordinate_system("Global")

        # obj = self.aedtapp.modeler.create_object_from_face(face=[self.aedtapp.modeler["si"].top_face_z], non_model=False)
        obj = self.aedtapp.modeler.create_object_from_face(assignment=[self.aedtapp.modeler["si"].top_face_z], non_model=False)
        obj.name = "SIOdw"
        # self.aedtapp.modeler.thicken_sheet(objid="SIOdw", thickness="d_siodw")
        self.aedtapp.modeler.thicken_sheet(assignment="SIOdw", thickness="d_siodw")
        self.aedtapp.modeler["SIOdw"].material_name = "silicon_dioxide"
        self.aedtapp.modeler["SIOdw"].color = [128, 128, 128]
        self.aedtapp.modeler["SIOdw"].transparency = 0

        point_list = [["0mm", "(l-w_sig-gap*2-w_au*2)/2+w_au+gap/2", "d_si+d_siodw+d_ln+d_sioup/2"],
                      ["ly", "(l-w_sig-gap*2-w_au*2)/2+w_au+gap/2", "d_si+d_siodw+d_ln+d_sioup/2"]]
        # self.aedtapp.modeler.create_polyline(position_list=point_list,
        #                                      name="sioup",
        #                                      matname="silicon_dioxide",
        #                                      xsection_type="Isosceles Trapezoid",
        #                                      xsection_orient="Auto",
        #                                      xsection_width="sioxw",
        #                                      xsection_topwidth="siosw",
        #                                      xsection_height="d_sioup",
        #                                      xsection_bend_type="Corner")
        self.aedtapp.modeler.create_polyline(points=point_list,
                                             name="sioup",
                                             material="silicon_dioxide",
                                             xsection_type="Isosceles Trapezoid",
                                             xsection_orient="Auto",
                                             xsection_width="sioxw",
                                             xsection_topwidth="siosw",
                                             xsection_height="d_sioup",
                                             xsection_bend_type="Corner")
        # self.aedtapp.modeler.duplicate_along_line(objid="sioup", vector=["0mm", "w_sig+gap", "0mm"], attachObject=True)
        self.aedtapp.modeler.duplicate_along_line(assignment="sioup", vector=["0mm", "w_sig+gap", "0mm"], attach=True)
        self.aedtapp.modeler.subtract(blank_list="sioup", tool_list=["LNBD1"], keep_originals=True)

    def create_model_solids_vacuum(self):
        self.aedtapp.modeler.set_working_coordinate_system("Global")
        obj = self.aedtapp.modeler.create_region(pad_value=[0, 0, 0, 0, 30, 0])
        obj.name = "Region"
        self.aedtapp.modeler["Region"].material_name = "vacuum"

    def create_ports(self):
        """
        设置 ports
        :return:
        """
        self.aedtapp.modeler.set_working_coordinate_system("RelativeCS1")

        # 创建Port
        position = ["-w_au+(w_sig2-w_sig)/2+gap2-gap-gap2-w_sig2/2-(2*gap2+w_sig2)*2/2", "-l_taper-l_shouzhai", "-160um"]
        dimension_list = ["(2*gap2+w_sig2)*2", "320um"]
        # port1 = self.aedtapp.modeler.create_rectangle(csPlane=pyaedt.constants.PLANE.ZX,
        #                                               position=position,
        #                                               dimension_list=dimension_list,
        #                                               name='Rectangle1',
        #                                               matname='None')
        port1 = self.aedtapp.modeler.create_rectangle(orientation=pyaedt.constants.PLANE.ZX,
                                                      origin=position,
                                                      sizes=dimension_list,
                                                      name='Rectangle1',
                                                      material=None)

        position = ["ly-(-w_au-gap+(w_sig2-w_sig)/2 )+w_sig2/2-(2*gap2+w_sig2)*2/2", "w_au*2+gap*2+w_sig+l_taper+l_shouzhai", "-160um"]
        dimension_list = ["(2*gap2+w_sig2)*2", "320um"]
        # port2 = self.aedtapp.modeler.create_rectangle(csPlane=pyaedt.constants.PLANE.ZX,
        #                                               position=position,
        #                                               dimension_list=dimension_list,
        #                                               name='Rectangle2',
        #                                               matname='None')
        port2 = self.aedtapp.modeler.create_rectangle(orientation=pyaedt.constants.PLANE.ZX,
                                                      origin=position,
                                                      sizes=dimension_list,
                                                      name='Rectangle2',
                                                      material=None)

        # 设置Port
        self.aedtapp.wave_port(port1.faces[0], name='1')
        self.aedtapp.wave_port(port2.faces[0], name='2')

    def create_boundaries(self):
        """
        设置边界
        :return:
        """

        rad_faces = set()
        for face in self.aedtapp.modeler["Region"].faces:
            rad_faces.add(face.id)

        rad_faces = rad_faces - {self.aedtapp.modeler["Region"].bottom_face_z.id}
        # self.aedtapp.assign_radiation_boundary_to_faces(faces_id=list(rad_faces), boundary_name='Rad1')
        self.aedtapp.assign_radiation_boundary_to_faces(assignment=list(rad_faces), name='Rad1')

        perfe_faces = [self.aedtapp.modeler["Region"].bottom_face_z.id]
        # self.aedtapp.assign_radiation_boundary_to_faces(faces_id=perfe_faces, boundary_name='PerfE1')
        self.aedtapp.assign_radiation_boundary_to_faces(assignment=perfe_faces, name='PerfE1')

    def create_setup(self):
        # 设置Setup
        # self.aedtapp.create_setup(setupname="Setup1",
        #                           setuptype="HFSSDriven",
        #                           Frequency="40GHz",
        #                           MaximumPasses=20,
        #                           MaxDeltaS=0.02)
        self.aedtapp.create_setup(name="Setup1",
                                  setup_type="HFSSDriven",
                                  Frequency="40GHz",
                                  MaximumPasses=20,
                                  MaxDeltaS=0.02)

        # self.aedtapp.create_linear_count_sweep(setupname="Setup1",
        #                                        sweepname="Sweep",
        #                                        unit="GHz",
        #                                        freqstart=0.6,
        #                                        freqstop=60,
        #                                        sweep_type="Interpolating",
        #                                        num_of_freq_points=401)
        self.aedtapp.create_linear_count_sweep(setup="Setup1",
                                               name="Sweep",
                                               units="GHz",
                                               start_frequency=39,
                                               stop_frequency=60,
                                               sweep_type="Interpolating",
                                               num_of_freq_points=401)

    def sweep_variable(self):
        self.aedtapp.parametrics.add(sweep_var="w_sig2", start_point=30, end_point=80, step=10, variation_type="LinearStep", parametricname="ParametricSetup1")

    def validate_check(self, design=None):
        return self.aedtapp.validate_full_design(design=design)

    def run_analyze(self):

        # return self.aedtapp.analyze()
        return self.aedtapp.analyze_setup(name='Setup1')

    def create_model_solids(self):
        self.create_model_solids_aluminum()
        self.create_model_solids_silicon()
        self.create_model_solids_LINBO3_step_1()
        self.create_model_solids_silicon_dioxide()
        self.create_model_solids_LINBO3_step_2()
        self.create_model_solids_vacuum()

    def load_project(self, project_file):
        """
        加载工程文件
        :param project_file:
        :return:
        """
        self.aedtapp.load_project(project_file=project_file)

    def create_reports(self):
        print(self.aedtapp.get_sweeps(name="Setup1"))
        self.aedtapp.create_output_variable(variable="loss",
                                            expression="Re(Gamma(1))*8.68/100",
                                            solution="Setup1:Sweep")

        self.aedtapp.create_output_variable(variable="neff",
                                            expression="300000000*Im(Gamma(1))/2/3.14/freq",
                                            solution="Setup1:Sweep")

        self.aedtapp.post.create_report(expressions="loss")
        self.aedtapp.post.create_report(expressions="neff")
        self.aedtapp.post.create_report(expressions="Zo(1)")

    def export_reports(self, export_filename):
        exported_files = self.aedtapp.export_results(export_folder=export_filename)
        print(exported_files)

    def delete_report(self, plot_name=None):
        self.aedtapp.post.delete_report(plot_name=plot_name)

def process_aedt_data(export_filename="aedt_output"):
    dir_path = os.getcwd()
    result_dir = os.path.join(dir_path, export_filename)

    files = [os.path.join(result_dir, file) for file in os.listdir(result_dir)]
    for file in files:
        if os.path.splitext(file)[-1] == ".csv":
            print(file)
            fd_csv = open(file, 'r')

            fd_dat = None
            for line_index, line_content in enumerate(fd_csv.readlines()):
                # print(line_index, line_content)
                if line_index == 0:
                    if line_content.find('loss') != -1:
                        fd_dat = open(os.path.join(result_dir, "loss.dat"), "w")
                    elif line_content.find('neff') != -1:
                        fd_dat = open(os.path.join(result_dir, "neff.dat"), "w")
                    elif line_content.find('Zo(1)') != -1:
                        fd_dat = open(os.path.join(result_dir, "Port Zo.dat"), "w")
                else:
                    line_content = line_content.replace(',', ' ')
                    line_content = line_content.replace(' + ', ' ')
                    line_content = line_content.replace('i', '')
                    fd_dat.writelines(line_content)

            if fd_dat is not None:
                fd_dat.close()

            fd_csv.close()

def test_create_model(current_dir):

    modulator = Modulator_HFSS_Model(projectname="Modulator", designname="1mm")
    # 通过文件添加变量
    # variable_file = os.path.join(os.getcwd(), "hfss_source", "hfss_variables.txt")
    variable_file = os.path.join(current_dir, "hfss_source", "hfss_variables.txt")
    modulator.set_variable_by_file(variable_file=variable_file)
    # 添加 LINBO3
    material_name="LINbO3"
    material_cfg_name="permittivity"
    material_cfg_value=['44.3', '44.3', '30']
    modulator.add_material(material_name=material_name, material_cfg_name=material_cfg_name, material_cfg_value=material_cfg_value)
    # 添加坐标系
    modulator.add_coordinate_systems()
    # 创建模型
    modulator.create_model_solids()
    # 创建Port
    modulator.create_ports()
    # 设置边界
    modulator.create_boundaries()
    # 设置Analysis
    modulator.create_setup()
    # 验证并仿真
    validate_msg, validate_state = modulator.validate_check()
    if validate_state == True:
        print("validata is OK")
        if modulator.run_analyze() == True:
            print("run analyze finish")
        else:
            print("run analyze failed")
            modulator.close_project()
            return
    else:
        print("validata is Failed: ", validate_msg)
        modulator.close_project()
        return

    # 保存文件
    project_filename = "Modulator_1mm.aedt"
    # filepath = os.path.join(os.getcwd(), "hfss_result", project_filename)
    filepath = os.path.join(current_dir, "hfss_result", project_filename)
    modulator.save_project(project_filename=filepath)
    # del modulator
    modulator.close_project()

def test_export_result(current_dir):
    modulator = Modulator_HFSS_Model()
    # 加载工程
    # project_file = os.path.join(os.getcwd(), "hfss_result", "Modulator_1mm.aedt")
    project_file = os.path.join(current_dir, "hfss_result", "Modulator_1mm.aedt")
    modulator.load_project(project_file=project_file)
    # 创建报告
    modulator.create_reports()
    # export_file = os.path.join(os.getcwd(), "aedt_output")
    export_file = os.path.join(current_dir, "aedt_output")
    modulator.export_reports(export_filename=export_file)
    project_filename = "Modulator_1mm_result.aedt"
    # filepath = os.path.join(os.getcwd(), "hfss_result", project_filename)
    filepath = os.path.join(current_dir, "hfss_result", project_filename)
    modulator.save_project(project_filename=filepath)
    # del modulator
    modulator.close_project()


if __name__ == "__main__":
    start_time = time.time()

    test_create_model(os.path.dirname(__file__))

    print(time.time() - start_time)

