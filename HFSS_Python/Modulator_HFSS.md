# 使用Python对铌酸锂调制器进行HFSS仿真
&emsp;&emsp;本文介绍了如何基于pyaedt创建HFSS的python仿真脚本，以铌酸锂调制器为例，演示了使用python创建铌酸锂的三维仿真模型、设置材料参数、设置边界条件、运行仿真以及报告的创建和数据的导出。<br>
## 运行环境
&emsp;&emsp;使用的HFSS版本建议在2022 R2及以后，HFSS版本越新，对python的支持度越好，本文使用的HFSS版本是2023 R1。<br>
&emsp;&emsp;使用的python版本是3.11.5。<br>
&emsp;&emsp;在Anaconda的python环境中，使用`pip install pyaedt`命令安装PyAEDT，PyAEDT是Ansys官方提供的python库，PyAEDT封装了Ansys Electronics Desktop (AEDT)的API，使编写python脚本更加简单。<br>
## 启动HFSS并创建工程
&emsp;&emsp;通过`Hfss`接口新建一个HFSS工程，`projectname`和`designname`参数可以对工程名称和设计名称进行设置，`non_graphical`参数用于设置是否显示图形界面，`new_desktop_session`参数用于重新开启一个对话，用于当前环境启动了多个HFSS程序，`close_on_exit`参数用于脚本结束时是否关闭HFSS程序。<br>
```angular2html
from pyaedt import Hfss

    ...
    if projectname is not None and designname is not None:
        self.aedtapp = Hfss(projectname=projectname,
                            designname=designname,
                            non_graphical=False,
                            new_desktop_session=True,
                            close_on_exit=True)
    else:
        self.aedtapp = Hfss()
    ...
```
&emsp;&emsp;用以下代码保存工程文件，需要填入保存文件的完整路径。<br>
```angular2html
...
self.aedtapp.save_project(project_file=project_filename)
...
```
&emsp;&emsp;以下代码用于加载现有文件。<br>
```angular2html
self.aedtapp.load_project(project_file=project_file)
```
![HFSS工程](.\hfss_images\HFSS.png)

## 设置自定义变量
&emsp;&emsp;可以通过`variable_manager.set_variable`接口添加自定义变量，以代码展示的是从文本中导入自定义变量。<br>
```angular2html
...
with open(variable_file, mode="r") as variables_fd:
    for line_index, line_context in enumerate(variables_fd.readlines()):
        list_context = line_context.split("\t")
        if list_context[0] == "Name":
            continue

        if 0 == len(list_context[2]):
            self.set_variable(variable_name=list_context[0], expression=list_context[1])
        else:
            self.set_variable(variable_name=list_context[0], expression=list_context[3])
...
def set_variable(self, variable_name, expression):
    self.aedtapp.variable_manager.set_variable(variable_name=variable_name, expression=expression)
...
```
![自定义变量](.\hfss_images\variables.png)

## 添加自定义材料
&emsp;&emsp;HFSS的材料库里缺少LINbO3材料，需要自定义添加，可以用以下代码实现：<br>
```angular2html
...
# 添加 LINBO3
material_name="LINbO3"
material_cfg_name="permittivity"
material_cfg_value=['44.3', '44.3', '30']
modulator.add_material(material_name=material_name,material_cfg_name=material_cfg_name, material_cfg_value=material_cfg_value)
...
def add_material(self, material_name, material_cfg_name, material_cfg_value):
    mat = self.aedtapp.materials.add_material(material_name)
    attrib = getattr(mat, material_cfg_name)
    attrib = material_cfg_value
...
```
![自定义材料](.\hfss_images\material.png)

## 添加自定义坐标系
&emsp;&emsp;添加自定义的坐标系。<br>
```angular2html
self.aedtapp.modeler.create_coordinate_system(
    origin=["0mm", "(l-w_sig-gap*2-w_au*2)/2", "d_si+d_siodw+d_ln+d_au"],
    reference_cs="Global",
    name="RelativeCS1",
    x_pointing=[1, 0, 0],
    y_pointing=[0, 1, 0]
)
```
![自定义坐标系](.\hfss_images\coordinate.png)

## 创建三维模型
&emsp;&emsp;创建铌酸锂调制器的三维仿真模型，创建三维模型的代码较长，这里不详细展开，详细创建过程可以查看源码，主要介绍几个常用的函数。<br>
```angular2html
...
# 在创建模型前指定使用的坐标系，默认使用的是Global坐标系
self.aedtapp.modeler.set_working_coordinate_system("Global")
position = ["0mm", "(l-w_sig-gap*2-w_au*2)/2+r2", "d_si+d_siodw+d_ln"]
dimensions_list = ["ly", "w_au-r2", "d_au"]
# 创建Box模型，设置Box原点和尺寸，并指定材料
self.aedtapp.modeler.create_box(origin=position, sizes=dimensions_list, name="Box1", material="aluminum")
# 沿指定方向复制模型
self.aedtapp.modeler.duplicate_along_line(assignment="Box1", vector=["0mm", "w_au-r2+w_sig+gap*2", "0mm"], attach=True)
# 设置模型的颜色和透明度
self.aedtapp.modeler["Box1"].color = [255, 128, 64]
self.aedtapp.modeler["Box1"].transparency = 0
...
point_list = [["-w_au+(w_au-r2)", "0mm", "0mm"],
              ["-w_au+(w_sig2-w_sig)/2+gap2-gap+(w_au-r2)", "-l_shouzhai", "0mm"],
              ["-w_au+(w_sig2-w_sig)/2+gap2-gap+(w_au-r2)", "-l_taper-l_shouzhai", "0mm"],
              ["ly+w_au*2+gap*2+w_sig+ w_s", "-l_taper-l_shouzhai", "0mm"],
              ["ly+w_au*2+gap*2+w_sig+ w_s", "0mm", "0mm"],
              ["-w_au+(w_au-r2)", "0mm", "0mm"]]
# 创建折现
self.aedtapp.modeler.create_polyline(points=point_list, name="Polyline20")
# 折现生成面
self.aedtapp.modeler.cover_lines(assignment="Polyline20")
# 面做裁剪
self.aedtapp.modeler.subtract(blank_list="Polyline16", tool_list=["Polyline20"], keep_originals=False)
# 合并成一个面
self.aedtapp.modeler.unite(assignment=["Polyline1", "Polyline16"])
# 拉伸面成实体
self.aedtapp.modeler.thicken_sheet(assignment="Polyline1", thickness="-d_au")
# 绕z轴旋转复制
self.aedtapp.modeler.duplicate_around_axis(assignment="Polyline1", axis="Z", angle=180)
# 移动模型
self.aedtapp.modeler.move(assignment="Polyline1_1", vector=["ly", "w_au*2+gap*2+w_sig", "0mm"])
...
```
&emsp;&emsp;创建port。<br>
```angular2html
# 设置当前坐标系为相对坐标系
self.aedtapp.modeler.set_working_coordinate_system("RelativeCS1")
# 创建Port
position = ["-w_au+(w_sig2-w_sig)/2+gap2-gap-gap2-w_sig2/2-(2*gap2+w_sig2)*2/2", "-l_taper-l_shouzhai", "-160um"]
dimension_list = ["(2*gap2+w_sig2)*2", "320um"]
port1 = self.aedtapp.modeler.create_rectangle(orientation=pyaedt.constants.PLANE.ZX,
                                              origin=position,
                                              sizes=dimension_list,
                                              name='Rectangle1',
                                              material=None)

position = ["ly-(-w_au-gap+(w_sig2-w_sig)/2 )+w_sig2/2-(2*gap2+w_sig2)*2/2", "w_au*2+gap*2+w_sig+l_taper+l_shouzhai", "-160um"]
dimension_list = ["(2*gap2+w_sig2)*2", "320um"]
port2 = self.aedtapp.modeler.create_rectangle(orientation=pyaedt.constants.PLANE.ZX,
                                              origin=position,
                                              sizes=dimension_list,
                                              name='Rectangle2',
                                              material=None)

# 设置Port
self.aedtapp.wave_port(port1.faces[0], name='1')
self.aedtapp.wave_port(port2.faces[0], name='2')
```
![三维模型](.\hfss_images\model.png)

## 设置边界条件
&emsp;&emsp;设置各个面的边界条件。<br>
```angular2html
# 纪录所有面的id号
...
rad_faces = set()
for face in self.aedtapp.modeler["Region"].faces:
    rad_faces.add(face.id)

# 除了底面外的其他面设置成 Radiation 类型
rad_faces = rad_faces - {self.aedtapp.modeler["Region"].bottom_face_z.id}
self.aedtapp.assign_radiation_boundary_to_faces(assignment=list(rad_faces), name='Rad1')

# 将底面设置成 PerfE 类型
perfe_faces = [self.aedtapp.modeler["Region"].bottom_face_z.id]
self.aedtapp.assign_radiation_boundary_to_faces(assignment=perfe_faces, name='PerfE1')
...
```
![边界条件](.\hfss_images\boundaries.png)

## 设置Analysis
&emsp;&emsp;添加setup并设置线性扫参。<br>
```angular2html
self.aedtapp.create_setup(name="Setup1",
                                  setup_type="HFSSDriven",
                                  Frequency="40GHz",
                                  MaximumPasses=20,
                                  MaxDeltaS=0.02)

self.aedtapp.create_linear_count_sweep(setup="Setup1",
                                       name="Sweep",
                                       units="GHz",
                                       start_frequency=39,
                                       stop_frequency=60,
                                       sweep_type="Interpolating",
                                       num_of_freq_points=401)
```

## 进行有效性检测并执行仿真
```angular2html
...
# 检验design的设置是否有效
self.aedtapp.validate_full_design(design=design)
...
# 运行指定的setup
self.aedtapp.analyze_setup(name='Setup1')
...
```

## 创建报告
&emsp;&emsp;添加自定义的表达式并生成报告，指定完整路径导出report。<br>
```angular2html
self.aedtapp.create_output_variable(variable="loss",
                                    expression="Re(Gamma(1))*8.68/100",
                                    solution="Setup1:Sweep")

self.aedtapp.create_output_variable(variable="neff",
                                    expression="300000000*Im(Gamma(1))/2/3.14/freq",
                                    solution="Setup1:Sweep")

self.aedtapp.post.create_report(expressions="loss")
self.aedtapp.post.create_report(expressions="neff")
self.aedtapp.post.create_report(expressions="Zo(1)")
...
# 导出report
exported_files = self.aedtapp.export_results(export_folder=export_filename)
...
```
![report](.\hfss_images\loss.png)





