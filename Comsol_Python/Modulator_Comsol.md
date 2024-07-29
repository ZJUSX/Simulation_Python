# 使用Python对铌酸锂调制器进行Comsol仿真
&emsp;&emsp;本文介绍了如何基于mph创建Comsol的python仿真脚本，以铌酸锂调制器为例，演示了使用python创建铌酸锂的二维仿真模型、设置材料参数、设置边界条件、运行仿真以及报告的创建和数据的导出。<br>
## 运行环境
&emsp;&emsp;本文使用的Comsol版本是6.1。<br>
&emsp;&emsp;使用的python版本是3.11.5。<br>
&emsp;&emsp;在Anaconda的python环境中，使用`pip install MPh`命令安装MPh，Comsol提供的是Java API，未提供Python接口，MPh利用jype与Java建立起连接来访问Comsol API。MPh库封装了文件加载模型、修改参数、导入数据，然后运行模拟、评估结果等操作的接口，但对于复杂操作，需要参考Comsol API文档，通过MPh调用Java接口实现。<br>
## 启动HFSS并创建工程
&emsp;&emsp;mph通过session的方式与Comsol建立连接，mph提供了与Comsol连接的两种模式，一种是
当前执行的python程序与Comsol软件都在同一台计算机上，则在本地创建client，并通过jpype运行Java虚拟机与Comsol交互；另一种是Comsol与python程序在不同的计算机上，以client-server的方式通信。本文使用本地方式连接Comsol，调用`mph.start`接口与Comsol创立连接，再调用`create`接口创建Comsol工程，`create`函数返回的对象是mph封装的类，后续使用该类的java成员完成复杂操作。<br>
```angular2html
# 通过mph创建client
self.__client = mph.start(version='6.1')
if False == loadProject:
    # 通过create接口创建工程
    self.__model = self.__client.create(project_name)
    self.__model.java.param().label("参数")
else:
    # load接口可以加载现在仿真文件
    self.__model = self.__client.load(file=project_name)
...
# 保存Comsol文件
self.__model.save(self.__project_name)
```
![comsol工程](.\comsol_images\comsol.png)
## 设置自定义变量
&emsp;&emsp;从文件中读取自定义变量并设置到comsol中，使用的是`java.param().set()`接口，Comsol的Java API大部分接口都进行了重载，具体使用方式可以查看Comsol官网。<br>
```angular2html
def load_parameters(self, parameters_filename):
    with open(parameters_filename, 'r', encoding="UTF-8") as f:
        for line in f:
            columns = line.split()
            paraName = columns[0]
            paraExpress = columns[1]
            paraDes = columns[2]
            if paraDes != '""':
                self.__model.java.param().set(paraName, paraExpress, paraDes)
            else:
                self.__model.java.param().set(paraName, paraExpress)
```
![parameters](.\comsol_images\parameter.png)
## 添加材料
&emsp;&emsp;本文将材料的特性参数保存在xml，解析xml文件设置材料参数，主要使用以下接口设置添加材料。<br>
```angular2html
for model in root.findall("model"):
    for material in list(model):
        if comp_name == None:
            comp_name = material.attrib["component"]

        # 指定组件创建材料
        self.__model.java.component(comp_name).material().create(material.attrib["tag"], material.attrib["type"])

        for property in list(material):
            if property.tag == "label":
                # 设置材料标签
                self.__model.java.component(comp_name).material(material.attrib["tag"]).label(
                    property.attrib["label"])
            elif property.tag == "propertyGroup":
                if property.attrib["tag"] != "def":
                    # 设置材料的描述信息
                    self.__model.java.component(comp_name).material(
                        material.attrib["tag"]).propertyGroup().create(property.attrib["tag"], property.attrib["descr"])

                for ele in list(property):
                    if ele.tag == "set":
                        print(ele.attrib["name"], ele.attrib["value"])
                        attrib = ele.attrib["value"]
                        if ele.attrib["value"].find("{") == 0:
                            attrib = eval(attrib.replace("{", "[").replace("}", "]"))
                        # 设置材料的属性
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
```
![material](.\comsol_images\material.png)

## 创建模型
&emsp;&emsp;创建平面模型主要涉及到矩形、多边形的创建，以及对多边形的合并、求差等几何操作，创建完几何模型后要对各个区域设置材料。<br>
```angular2html
    # 创建矩形
    self.__model.java.component("comp1").geom("geom1").create("r1", "Rectangle")
    self.__model.java.component("comp1").geom("geom1").feature("r1").set("size", ["sio2w", "sio2h"])
    self.__model.java.component("comp1").geom("geom1").feature("r1").set("base", "center")
    self.__model.java.component("comp1").geom("geom1").feature("r1").label("矩形1")
    self.__model.java.component("comp1").geom("geom1").run("r1")

    ...
    # 创建多边形
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

    ...
    # 两个多边形相减
    self.__model.java.component("comp1").geom("geom1").create("dif2", "Difference")
    self.__model.java.component("comp1").geom("geom1").feature("dif2").selection("input").set("pol5")
    self.__model.java.component("comp1").geom("geom1").feature("dif2").selection("input2").set("pol1")
    self.__model.java.component("comp1").geom("geom1").feature("dif2").set("keepsubtract", True)
    self.__model.java.component("comp1").geom("geom1").feature("dif2").label("差集2")
    self.__model.java.component("comp1").geom("geom1").run("dif2")

    # 合并多边形
    self.__model.java.component("comp1").geom("geom1").create("uni1", "Union")
    self.__model.java.component("comp1").geom("geom1").feature("uni1").selection("input").set("pol1", "r2")
    self.__model.java.component("comp1").geom("geom1").feature("uni1").label("并集1")
    self.__model.java.component("comp1").geom("geom1").feature("uni1").set("selresult", True)
    self.__model.java.component("comp1").geom("geom1").feature("uni1").set("color", "8")
    self.__model.java.component("comp1").geom("geom1").feature("uni1").set("intbnd", False)
    self.__model.java.component("comp1").geom("geom1").run("uni1")

    ...
    # 创建点
    self.__model.java.component("comp1").geom("geom1").create("pt2", "Point")
    self.__model.java.component("comp1").geom("geom1").feature("pt2").setIndex("p", "sio2h/2+LNh", 1)
    self.__model.java.component("comp1").geom("geom1").feature("pt2").label("点2")
```
```angular2html
# 给几何模型设置材料
self.__model.java.component("comp1").material("mat1").selection().set(1, 4, 5)
self.__model.java.component("comp1").material("mat4").selection().set(2)
self.__model.java.component("comp1").material("mat6").selection().set(4)
self.__model.java.component("comp1").material("mat9").selection().set(3, 6)
```
![model](.\comsol_images\geometry.png)

## 设置Electrostatics、EWFD、Mesh、Study
```angular2html
# 设置Electrostatics
self.__model.java.component("comp1").physics().create("es", "Electrostatics", "geom1")
self.__model.java.component("comp1").physics("es").create("gnd1", "Ground", 1)
self.__model.java.component("comp1").physics("es").create("term1", "Terminal", 1)
self.__model.java.component("comp1").physics("es").feature("gnd1").selection().set(10)
self.__model.java.component("comp1").physics("es").feature("term1").selection().set(21)
self.__model.java.component("comp1").physics("es").feature("term1").set("TerminalType", "Voltage")
self.__model.java.component("comp1").physics("es").feature("term1").set("V0", "VV")
```
```angular2html
# 设置 EWFD
self.__model.java.component("comp1").physics().create("ewfd", "ElectromagneticWavesFrequencyDomain", "geom1")
self.__model.java.component("comp1").physics("ewfd").create("sctr1", "Scattering", 1)
self.__model.java.component("comp1").physics("ewfd").feature("sctr1").selection().set(1, 2, 3, 5, 7, 9, 24, 25, 26, 27)
```
```angular2html
# 设置mesh
self.__model.java.component("comp1").mesh().create("mesh1")
self.__model.java.component("comp1").mesh("mesh1").create("ftri1", "FreeTri")
self.__model.java.component("comp1").mesh("mesh1").feature("size").set("custom", False)
self.__model.java.component("comp1").mesh("mesh1").feature("ftri1").selection().geom("geom1")
self.__model.java.component("comp1").mesh("mesh1").feature("size").set("hauto", JInt(2))
self.__model.java.component("comp1").mesh("mesh1").run()
```
```angular2html
# 添加Study
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
```
![mesh](.\comsol_images\mesh.png)

## 添加自定义变量、视图、坐标系等
```angular2html
# 创建变量
self.__model.java.component("comp1").variable().create("var1")
self.__model.java.component("comp1").variable("var1").label("变量 1")
self.__model.java.component("comp1").variable("var1").set("EE", "es.normE")
self.__model.java.component("comp1").variable("var1").set("ratio", "intop1(ewfd.normE)/intop2(ewfd.normE)")

# 创建selection
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
```

## 运行仿真
```angular2html
self.__model.build()
self.__model.mesh()
self.__model.solve()
```
## 创建报告并导出
```angular2html
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
```
![table](.\comsol_images\table.png)
