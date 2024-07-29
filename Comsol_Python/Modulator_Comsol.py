import os

import mph
from jpype import JInt

class Modulator_Comsol_Model:

    def __init__(self, project_name, loadProject=False):
        """
        加载或新建项目
        :param project_name:
        :param loadProject:
        """
        self.__project_name = project_name
        self.__client = mph.start(version='6.1')

        if False == loadProject:
            self.__model = self.__client.create(project_name)
            self.__model.java.param().label("参数")
        else:
            self.__model = self.__client.load(file=project_name)

    def save_project(self, project_name=None):
        if project_name == None:
            self.__model.save(self.__project_name)
        else:
            self.__model.save(project_name)

    def close_project(self):
        self.__client.remove(self.__model)
        self.__client.clear()

    def load_parameters(self, parameters_filename):
        with open(parameters_filename, 'r', encoding="UTF-8") as f:
            for line in f:
                columns = line.split()
                paraName = columns[0]
                paraExpress = columns[1]
                paraDes = columns[2]
                # print(columns, " ", paraName, " ", paraExpress, " ", paraDes)
                if paraDes != '""':
                    self.__model.java.param().set(paraName, paraExpress, paraDes)
                else:
                    self.__model.java.param().set(paraName, paraExpress)

    def set_parameter(self, paraName, paraExpress, paraDes= '""'):
        if paraDes != '""':
            self.__model.java.param().set(paraName, paraExpress, paraDes)
        else:
            self.__model.java.param().set(paraName, paraExpress)

        self.__model.java.component("comp1").geom("geom1").run("fin")

    def get_parameter(self, paraName):
        return self.__model.java.param().get(paraName)

    def create_parameters_case(self, case_name, parameters_filename):
        self.__model.java.param("default").paramCase().create(case_name)
        with open(parameters_filename, 'r', encoding="UTF-8") as f:
            for line in f:
                columns = line.split()
                paraName = columns[0]
                paraExpress = columns[1]
                paraDes = columns[2]
                self.__model.java.param("default").paramCase(case_name).set(paraName, paraExpress)


    def create_component(self, component_label, component_tag):
        self.__model.java.component().create("tag1", True)
        self.__model.java.component("tag1").label(component_label)
        self.__model.java.component("tag1").tag(component_tag)

        return self.__model.java.component(component_tag)

    def create_geometry(self, comp, gemo_lable, gemo_tag):
        comp.geom().create("part1", 2)
        comp.geom("part1").label(gemo_lable)
        comp.geom("part1").tag(gemo_tag)

        return comp.geom(gemo_tag)

    def create_geometries(self):
        self.__model.java.component().create("tag1", True)
        self.__model.java.component("tag1").label("组件1")
        self.__model.java.component("tag1").tag("comp1")

        self.__model.java.component("comp1").geom().create("part1", 2)
        self.__model.java.component("comp1").geom("part1").label("几何1")
        self.__model.java.component("comp1").geom("part1").tag("geom1")

        self.__model.java.component("comp1").geom("geom1").create("r1", "Rectangle")
        self.__model.java.component("comp1").geom("geom1").feature("r1").set("size", ["sio2w", "sio2h"])
        self.__model.java.component("comp1").geom("geom1").feature("r1").set("base", "center")
        self.__model.java.component("comp1").geom("geom1").feature("r1").label("矩形1")
        self.__model.java.component("comp1").geom("geom1").run("r1")

        self.__model.java.component("comp1").geom("geom1").create("r2", "Rectangle")
        self.__model.java.component("comp1").geom("geom1").feature("r2").set("size", ["LNw", "LNh"])
        self.__model.java.component("comp1").geom("geom1").feature("r2").set("base", "center")
        self.__model.java.component("comp1").geom("geom1").feature("r2").set("pos", ["0", "sio2h/2+LNh/2"])
        self.__model.java.component("comp1").geom("geom1").feature("r2").label("矩形2")
        self.__model.java.component("comp1").geom("geom1").run("r2")

        self.__model.java.component("comp1").geom("geom1").create("pol1", "Polygon")
        self.__model.java.component("comp1").geom("geom1").feature("pol1").set("source", "table")
        self.__model.java.component("comp1").geom("geom1").feature("pol1").setIndex("table", "-LNBDxw/2", 0, 0)
        self.__model.java.component("comp1").geom("geom1").feature("pol1").setIndex("table", "sio2h/2+LNh", 0, 1)
        self.__model.java.component("comp1").geom("geom1").feature("pol1").setIndex("table", "LNBDxw/2", 1, 0)
        self.__model.java.component("comp1").geom("geom1").feature("pol1").setIndex("table", "sio2h/2+LNh", 1, 1)
        self.__model.java.component("comp1").geom("geom1").feature("pol1").setIndex("table", "LNBDsw/2", 2, 0)
        self.__model.java.component("comp1").geom("geom1").feature("pol1").setIndex("table", "sio2h/2+LNh+LNBDh", 2, 1)
        self.__model.java.component("comp1").geom("geom1").feature("pol1").setIndex("table", "-LNBDsw/2", 3, 0)
        self.__model.java.component("comp1").geom("geom1").feature("pol1").setIndex("table", "sio2h/2+LNh+LNBDh", 3, 1)
        self.__model.java.component("comp1").geom("geom1").feature("pol1").label("多边形1")
        self.__model.java.component("comp1").geom("geom1").run("pol1")

        self.__model.java.component("comp1").geom("geom1").create("r3", "Rectangle")
        self.__model.java.component("comp1").geom("geom1").feature("r3").set("size", ["DJw", "DJh"])
        self.__model.java.component("comp1").geom("geom1").feature("r3").set("base", "corner")
        self.__model.java.component("comp1").geom("geom1").feature("r3").set("pos", ["gap/2", "sio2h/2+LNh"])
        self.__model.java.component("comp1").geom("geom1").feature("r3").label("矩形3")
        self.__model.java.component("comp1").geom("geom1").feature("r3").set("selresult", True)
        self.__model.java.component("comp1").geom("geom1").feature("r3").set("color", "4")
        self.__model.java.component("comp1").geom("geom1").run("r3")

        self.__model.java.component("comp1").geom("geom1").create("r4", "Rectangle")
        self.__model.java.component("comp1").geom("geom1").feature("r4").set("size", ["DJw", "DJh"])
        self.__model.java.component("comp1").geom("geom1").feature("r4").set("base", "corner")
        self.__model.java.component("comp1").geom("geom1").feature("r4").set("pos", ["-gap/2-DJw", "sio2h/2+LNh"])
        self.__model.java.component("comp1").geom("geom1").feature("r4").label("矩形4")
        self.__model.java.component("comp1").geom("geom1").feature("r4").set("selresult", True)
        self.__model.java.component("comp1").geom("geom1").feature("r4").set("color", "4")
        self.__model.java.component("comp1").geom("geom1").run("r4")

        self.__model.java.component("comp1").geom("geom1").create("pol5", "Polygon")
        self.__model.java.component("comp1").geom("geom1").feature("pol5").set("source", "table")
        self.__model.java.component("comp1").geom("geom1").feature("pol5").setIndex("table", "-sio2xw/2", 0, 0)
        self.__model.java.component("comp1").geom("geom1").feature("pol5").setIndex("table", "sio2xw/2", 1, 0)
        self.__model.java.component("comp1").geom("geom1").feature("pol5").setIndex("table", "SIO2sw/2", 2, 0)
        self.__model.java.component("comp1").geom("geom1").feature("pol5").setIndex("table", "-SIO2sw/2", 3, 0)
        self.__model.java.component("comp1").geom("geom1").feature("pol5").setIndex("table", "sio2h/2+LNh", 0, 1)
        self.__model.java.component("comp1").geom("geom1").feature("pol5").setIndex("table", "sio2h/2+LNh", 1, 1)
        self.__model.java.component("comp1").geom("geom1").feature("pol5").setIndex("table", "sio2h/2+LNh+d_sio2up", 2, 1)
        self.__model.java.component("comp1").geom("geom1").feature("pol5").setIndex("table", "sio2h/2+LNh+d_sio2up", 3, 1)
        self.__model.java.component("comp1").geom("geom1").feature("pol5").label("多边形5")
        self.__model.java.component("comp1").geom("geom1").run("pol5")

        self.__model.java.component("comp1").geom("geom1").create("r7", "Rectangle")
        self.__model.java.component("comp1").geom("geom1").feature("r7").set("size", ["KQw", "KQh"])
        self.__model.java.component("comp1").geom("geom1").feature("r7").set("base", "center")
        self.__model.java.component("comp1").geom("geom1").feature("r7").set("pos", ["0", "sio2h/2+LNh+KQh/2"])
        self.__model.java.component("comp1").geom("geom1").feature("r7").label("矩形7")
        self.__model.java.component("comp1").geom("geom1").run("r7")

        self.__model.java.component("comp1").geom("geom1").create("dif2", "Difference")
        self.__model.java.component("comp1").geom("geom1").feature("dif2").selection("input").set("pol5")
        self.__model.java.component("comp1").geom("geom1").feature("dif2").selection("input2").set("pol1")
        self.__model.java.component("comp1").geom("geom1").feature("dif2").set("keepsubtract", True)
        self.__model.java.component("comp1").geom("geom1").feature("dif2").label("差集2")
        self.__model.java.component("comp1").geom("geom1").run("dif2")

        self.__model.java.component("comp1").geom("geom1").create("uni1", "Union")
        self.__model.java.component("comp1").geom("geom1").feature("uni1").selection("input").set("pol1", "r2")
        self.__model.java.component("comp1").geom("geom1").feature("uni1").label("并集1")
        self.__model.java.component("comp1").geom("geom1").feature("uni1").set("selresult", True)
        self.__model.java.component("comp1").geom("geom1").feature("uni1").set("color", "8")
        self.__model.java.component("comp1").geom("geom1").feature("uni1").set("intbnd", False)
        self.__model.java.component("comp1").geom("geom1").run("uni1")

        self.__model.java.component("comp1").geom("geom1").create("dif3", "Difference")
        self.__model.java.component("comp1").geom("geom1").feature("dif3").selection("input").set("r7")
        self.__model.java.component("comp1").geom("geom1").feature("dif3").selection("input2").set("dif2", "r3", "r4", "uni1")
        self.__model.java.component("comp1").geom("geom1").feature("dif3").set("keepsubtract", True)
        self.__model.java.component("comp1").geom("geom1").feature("dif3").label("差集3")
        self.__model.java.component("comp1").geom("geom1").run("dif3")

        self.__model.java.component("comp1").geom("geom1").create("pt2", "Point")
        self.__model.java.component("comp1").geom("geom1").feature("pt2").setIndex("p", "sio2h/2+LNh", 1)
        self.__model.java.component("comp1").geom("geom1").feature("pt2").label("点2")

        self.__model.java.component("comp1").geom("geom1").run("fin")

    def import_material(self, comp_name=None, xmlfile=None):
        import xml.etree.ElementTree as ET

        if xmlfile == None:
            print('material xml file is None')
            return

        cfgTree = ET.parse(xmlfile)
        root = cfgTree.getroot()

        for model in root.findall("model"):
            for material in list(model):
                if comp_name == None:
                    comp_name = material.attrib["component"]

                self.__model.java.component(comp_name).material().create(material.attrib["tag"], material.attrib["type"])

                for property in list(material):
                    if property.tag == "label":
                        self.__model.java.component(comp_name).material(material.attrib["tag"]).label(
                            property.attrib["label"])
                    elif property.tag == "propertyGroup":
                        if property.attrib["tag"] != "def":
                            self.__model.java.component(comp_name).material(
                                material.attrib["tag"]).propertyGroup().create(property.attrib["tag"], property.attrib["descr"])

                        for ele in list(property):
                            if ele.tag == "set":
                                print(ele.attrib["name"], ele.attrib["value"])
                                attrib = ele.attrib["value"]
                                if ele.attrib["value"].find("{") == 0:
                                    attrib = eval(attrib.replace("{", "[").replace("}", "]"))

                                self.__model.java.component(comp_name).material(material.attrib["tag"]).propertyGroup(
                                    property.attrib["tag"]).set(ele.attrib["name"], attrib)
                            elif ele.tag == "func":
                                self.__model.java.component(comp_name).material(material.attrib["tag"]).propertyGroup(
                                    property.attrib["tag"]).func().create(ele.attrib["tag"], ele.attrib["oper"])
                                for func_ele in list(ele):
                                    if func_ele.tag == "set":
                                        print(func_ele.attrib["name"], func_ele.attrib["value"])
                                        if func_ele.attrib["name"] == "table":
                                            table = eval(func_ele.attrib["value"].replace("{", "[").replace("}", "]"))
                                            for idx in range(len(table)):
                                                self.__model.java.component(comp_name).material(
                                                    material.attrib["tag"]).propertyGroup(property.attrib["tag"]).func(
                                                    ele.attrib["tag"]).setIndex("table", table[idx][0], idx, 0)
                                                self.__model.java.component(comp_name).material(
                                                    material.attrib["tag"]).propertyGroup(property.attrib["tag"]).func(
                                                    ele.attrib["tag"]).setIndex("table", table[idx][0], idx, 1)
                                        else:
                                            attrib = func_ele.attrib["value"]
                                            if attrib.find("{") == 0:
                                                attrib = eval(attrib.replace("{", "[").replace("}", "]"))
                                            self.__model.java.component(comp_name).material(
                                                material.attrib["tag"]).propertyGroup(property.attrib["tag"]).func(
                                                ele.attrib["tag"]).set(func_ele.attrib["name"], attrib)
                            elif ele.tag == "addInput":
                                self.__model.java.component(comp_name).material(material.attrib["tag"]).propertyGroup(
                                    property.attrib["tag"]).addInput(ele.attrib["quantity"])
                            elif ele.tag == "descr":
                                self.__model.java.component(comp_name).material(material.attrib["tag"]).propertyGroup(
                                    property.attrib["tag"]).descr(ele.attrib["name"], ele.attrib["descr"])

    def set_material(self):
        self.__model.java.component("comp1").material("mat1").selection().set(1, 4, 5)
        self.__model.java.component("comp1").material("mat4").selection().set(2)
        self.__model.java.component("comp1").material("mat6").selection().set(4)
        self.__model.java.component("comp1").material("mat9").selection().set(3, 6)

    def create_Electrostatics(self):
        self.__model.java.component("comp1").geom("geom1").run()

        self.__model.java.component("comp1").physics().create("es", "Electrostatics", "geom1")
        self.__model.java.component("comp1").physics("es").create("gnd1", "Ground", 1)
        self.__model.java.component("comp1").physics("es").create("term1", "Terminal", 1)
        self.__model.java.component("comp1").physics("es").feature("gnd1").selection().set(10)
        self.__model.java.component("comp1").physics("es").feature("term1").selection().set(21)
        self.__model.java.component("comp1").physics("es").feature("term1").set("TerminalType", "Voltage")
        self.__model.java.component("comp1").physics("es").feature("term1").set("V0", "VV")

    def create_EWFD(self):

        self.__model.java.component("comp1").physics().create("ewfd", "ElectromagneticWavesFrequencyDomain", "geom1")
        self.__model.java.component("comp1").physics("ewfd").create("sctr1", "Scattering", 1)
        self.__model.java.component("comp1").physics("ewfd").feature("sctr1").selection().set(1, 2, 3, 5, 7, 9, 24, 25, 26, 27)

    def create_Mesh(self):

        self.__model.java.component("comp1").mesh().create("mesh1")
        # self.__model.java.component("comp1").mesh("mesh1").feature("size").set("predefined", True)
        # self.__model.java.component("comp1").mesh("mesh1").feature("size").set("hmax", "1.34")
        # self.__model.java.component("comp1").mesh("mesh1").feature("size").set("hmin", "6E-3") # 注意单位
        self.__model.java.component("comp1").mesh("mesh1").create("ftri1", "FreeTri")
        self.__model.java.component("comp1").mesh("mesh1").feature("size").set("custom", False)
        # self.__model.java.component("comp1").mesh("mesh1").feature("size").set("hauto", 2)
        self.__model.java.component("comp1").mesh("mesh1").feature("ftri1").selection().geom("geom1")
        self.__model.java.component("comp1").mesh("mesh1").feature("size").set("hauto", JInt(2))
        self.__model.java.component("comp1").mesh("mesh1").run()

    def create_Study(self):
        self.__model.java.study().create("std1")
        self.__model.java.study("std1").create("param", "Parametric")
        self.__model.java.study("std1").feature("param").label("电极间距+刻蚀深度")
        self.__model.java.study("std1").feature("param").set("sweeptype", "filled")
        self.__model.java.study("std1").feature("param").setIndex("pname", "sio2h", 0)
        self.__model.java.study("std1").feature("param").setIndex("plistarr", "", 0)
        self.__model.java.study("std1").feature("param").setIndex("punit", "m", 0)
        self.__model.java.study("std1").feature("param").setIndex("pname", "sio2h", 0)
        self.__model.java.study("std1").feature("param").setIndex("plistarr", "", 0)
        self.__model.java.study("std1").feature("param").setIndex("punit", "m", 0)
        self.__model.java.study("std1").feature("param").setIndex("pname", "LNBDh", 0)
        self.__model.java.study("std1").feature("param").setIndex("plistarr", "range(0.1,0.1,0.5)", 0)
        self.__model.java.study("std1").feature("param").setIndex("punit", "um", 0)
        self.__model.java.study("std1").feature("param").setIndex("pname", "sio2h", 1)
        self.__model.java.study("std1").feature("param").setIndex("plistarr", "", 1)
        self.__model.java.study("std1").feature("param").setIndex("punit", "m", 1)
        self.__model.java.study("std1").feature("param").setIndex("pname", "sio2h", 1)
        self.__model.java.study("std1").feature("param").setIndex("plistarr", "", 1)
        self.__model.java.study("std1").feature("param").setIndex("punit", "m", 1)
        self.__model.java.study("std1").feature("param").setIndex("pname", "gap", 1)
        self.__model.java.study("std1").feature("param").setIndex("plistarr", "range(3.5,0.5,8)", 1)
        self.__model.java.study("std1").feature("param").setIndex("punit", "um", 1)

        self.__model.java.study("std1").create("param2", "Parametric")
        self.__model.java.study("std1").feature("param2").setIndex("pname", "sio2h", 0)
        self.__model.java.study("std1").feature("param2").setIndex("plistarr", "", 0)
        self.__model.java.study("std1").feature("param2").setIndex("punit", "m", 0)
        self.__model.java.study("std1").feature("param2").setIndex("pname", "sio2h", 0)
        self.__model.java.study("std1").feature("param2").setIndex("plistarr", "", 0)
        self.__model.java.study("std1").feature("param2").setIndex("punit", "m", 0)
        self.__model.java.study("std1").feature("param2").setIndex("pname", "VV", 0)
        self.__model.java.study("std1").feature("param2").setIndex("plistarr", "range(-10,2,10)", 0)
        self.__model.java.study("std1").feature("param").active(False)


        self.__model.java.study("std1").create("stat", "Stationary")
        self.__model.java.study("std1").feature("stat").label("稳态")

        self.__model.java.study("std1").create("mode", "ModeAnalysis")
        self.__model.java.study("std1").feature("mode").label("模式分析")
        self.__model.java.study("std1").feature("mode").set("modeFreq", "f0")
        self.__model.java.study("std1").feature("mode").set("neigsactive", True)
        self.__model.java.study("std1").feature("mode").set("neigs", JInt(1))
        self.__model.java.study("std1").feature("mode").set("shift", "1.94")
        self.__model.java.study("std1").feature("mode").setEntry("activate", "es", False)

    def create_Definitions(self):
        self.__model.java.component("comp1").variable().create("var1")
        self.__model.java.component("comp1").variable("var1").label("变量 1")
        self.__model.java.component("comp1").variable("var1").set("EE", "es.normE")
        self.__model.java.component("comp1").variable("var1").set("ratio", "intop1(ewfd.normE)/intop2(ewfd.normE)")

        self.__model.java.component("comp1").selection().create("sel1", "Explicit")
        self.__model.java.component("comp1").selection("sel1").label("SIO2")
        self.__model.java.component("comp1").selection("sel1").set(1, 5)
        self.__model.java.component("comp1").selection().create("sel2", "Explicit")
        self.__model.java.component("comp1").selection("sel2").label("Al")
        self.__model.java.component("comp1").selection("sel2").set(3, 6)
        self.__model.java.component("comp1").selection().create("sel3", "Explicit")
        self.__model.java.component("comp1").selection("sel3").label("LN")
        self.__model.java.component("comp1").selection("sel3").set(2)
        self.__model.java.component("comp1").selection().create("sel4", "Explicit")
        self.__model.java.component("comp1").selection("sel4").label("AIR")
        self.__model.java.component("comp1").selection("sel4").set(4)

        self.__model.java.component("comp1").cpl().create("intop1", "Integration")
        self.__model.java.component("comp1").cpl("intop1").set("axisym", True)
        self.__model.java.component("comp1").cpl("intop1").selection().named("sel3")
        self.__model.java.component("comp1").cpl("intop1").label("积分 1")
        self.__model.java.component("comp1").cpl().create("intop2", "Integration")
        self.__model.java.component("comp1").cpl("intop2").set("axisym", True)
        self.__model.java.component("comp1").cpl("intop2").label("积分 2")
        self.__model.java.component("comp1").cpl("intop2").selection().set(1, 2, 3, 4, 5, 6)

        self.__model.java.component("comp1").coordSystem("sys1").label("边界坐标系 1")

        self.__model.java.component("comp1").view("view1").label("视图 1")

    def run_build_mesh_solve(self):
        self.__model.build()
        self.__model.mesh()
        self.__model.solve()

    def create_resutl_table(self, export_path=None):
        """用于联合仿真的报表"""

        self.__model.java.result().numerical().create("gev1", "EvalGlobal")
        self.__model.java.result().numerical("gev1").set("data", "dset3")
        self.__model.java.result().numerical("gev1").setIndex("looplevelinput", "manualindices", 0)
        self.__model.java.result().numerical("gev1").setIndex("looplevelindices", JInt(1), JInt(0))
        self.__model.java.result().numerical("gev1").setIndex("expr", "real(2.14^3*30.8[pm/V]*VV/1[V]*(intop1(ewfd.normE^2*EE)/intop2(ewfd.normE^2)))", 0)

        self.__model.java.result().table().create("tbl1", "Table")
        self.__model.java.result().table("tbl1").comments("Global Evaluation 1")
        self.__model.java.result().numerical("gev1").set("table", "tbl1")
        self.__model.java.result().numerical("gev1").setResult()

        if export_path is not None:
            self.__model.java.result().table("tbl1").save(export_path)

    def create_resutl_table_2(self, export_path=None):
        """用于联合仿真的报表 新版本"""
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

    def create_resutl_table_module_optimization(self, export_path=None):
        """用于单模块优化的报表"""

        self.__model.java.result().numerical().create("gev1", "EvalGlobal")
        self.__model.java.result().numerical("gev1").setIndex("expr", "gap*1.55[um]/(ne^3*30.8[pm/V]*gap/0.4[V]*(intop1(ewfd.normE^2*EE)/intop2(ewfd.normE^2)))", 0)
        self.__model.java.result().numerical("gev1").setIndex("unit", "V*cm", 0)
        self.__model.java.result().numerical("gev1").setIndex("expr", "ewfd.dampzdB", 1)

        self.__model.java.result().table().create("tbl1", "Table")
        self.__model.java.result().table("tbl1").comments("Global Evaluation 1")
        self.__model.java.result().numerical("gev1").set("table", "tbl1")
        self.__model.java.result().numerical("gev1").setResult()

        if export_path is not None:
            self.__model.java.result().table("tbl1").save(export_path)

def process_data(input_path, output_path):
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

def process_module_optimization_data(input_path):
    import re

    with open(input_path, encoding='gb18030', errors='ignore') as fd_input:
        for line_index, line_content in enumerate(fd_input.readlines()):
            if line_index < 5:
                continue
            content_after = re.sub(' +', ' ', line_content)
            context_list = content_after.split(" ")
            # print(context_list[1], context_list[2])
            return float(context_list[1]), float(context_list[2])

def test_comsol():
    modulator = Modulator_Comsol_Model(project_name="调制器截面仿真")
    filepath = os.path.join(os.getcwd(), "comsol_source", "parameters.txt")
    modulator.load_parameters(parameters_filename=filepath)
    filepath = os.path.join(os.getcwd(), "comsol_source", "parameters_case.txt")
    modulator.create_parameters_case(case_name="实例1", parameters_filename=filepath)
    modulator.create_geometries()
    filepath = os.path.join(os.getcwd(), "comsol_source", "Comsol_Material_modulator.xml")
    modulator.import_material(comp_name="comp1", xmlfile=filepath)
    modulator.set_material()
    modulator.create_Electrostatics()
    modulator.create_EWFD()
    modulator.create_Mesh()
    modulator.create_Study()
    modulator.create_Definitions()
    modulator.run_build_mesh_solve()

    project_name = os.path.join(os.getcwd(), "comsol_result", "调制器截面仿真.mph")
    modulator.save_project(project_name)

def test_comsol_ret():
    project_name = os.path.join(os.getcwd(), "comsol_result", "调制器截面仿真.mph")
    modulator = Modulator_Comsol_Model(project_name=project_name, loadProject=True)
    export_path = os.path.join(os.getcwd(), "comsol_result", "modulator_ret.txt")
    modulator.create_resutl_table_2(export_path)

    project_name = os.path.join(os.getcwd(), "comsol_result", "调制器截面仿真结果.mph")
    modulator.save_project(project_name)

    input_path = os.path.join(os.getcwd(), "comsol_result", "modulator_ret.txt")
    output_path = os.path.join(os.getcwd(), "comsol_result", "comsol_ret.txt")
    process_data(input_path=input_path, output_path=output_path)

if __name__ == "__main__":
    test_comsol()

    # test_comsol_ret()
