import os, sys
import xml.etree.ElementTree as ET

os.add_dll_directory('F:\\devTool\\Lumerical\\v202\\api\\python')
sys.path.append("F:\\devTool\\Lumerical\\v202\\api\\python")

import lumapi
import datetime

# print(datetime.date.today().strftime('%Y%m%d'))

class InterconnectModel:
    def __init__(self, hide=False):
        self.__interconnect = lumapi.INTERCONNECT(hide=hide)

        self.__interconnect.switchtodesign()
        self.__interconnect.deleteall()

    def save_project(self, project_name='tmp'):
        self.__interconnect.save(project_name)

    def export_result(self, dir_name, element_name):
        self.__interconnect.exportcsvresults(dir_name, element_name)

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

        return False

    '''
    def modify_filepath(self, xmlfile, input_path=None):
        if xmlfile == None:
            print("xml file is None")
            return

        cfgTree = ET.parse(xmlfile)
        root = cfgTree.getroot()

        for model in root.findall("model"):
            for ele in list(model):
                if ele.tag == 'element':
                    # print(ele.tag, ele.attrib)
                    for sub_ele in list(ele):
                        for sub_propety in list(sub_ele):
                            attribute = sub_propety.attrib
                            # print(attribute)
                            if 'name' in attribute and 'filepath' in attribute:
                                # print(attribute['name'], attribute['filepath'])
                                filepath = os.path.join(input_path, attribute['filepath'])
                                sub_propety.set('filepath', filepath)
    '''

    def load_cfg(self, xmlfile=None):
        if xmlfile == None:
            print("xml file is None")
            return

        cfgTree = ET.parse(xmlfile)
        root = cfgTree.getroot()

        for model in root.findall("model"):
            for ele in list(model):
                if ele.tag == 'property':
                    for sub_ele in list(ele):
                        # print(sub_ele.tag, ':')
                        for sub_propety in list(sub_ele):
                            attribute = sub_propety.attrib
                            # print(attribute)
                            if 'name' in attribute and 'value' in attribute:
                                print(attribute['name'], attribute['value'])
                                if self.is_number(attribute['value']):
                                    self.__interconnect.set(attribute['name'], eval(attribute['value']))
                                elif attribute['value'] == 'true':
                                    self.__interconnect.set(attribute['name'], 1)
                                elif attribute['value'] == 'false':
                                    self.__interconnect.set(attribute['name'], 0)
                                else:
                                    self.__interconnect.set(attribute['name'], attribute['value'])
                            elif 'name' in attribute and 'property' in attribute and 'exp' in attribute:
                                pass

                elif ele.tag == 'element':
                    print(ele.tag, ele.attrib)
                    self.__interconnect.addelement(ele.attrib['type'])
                    self.__interconnect.set("name", ele.attrib['tag'])
                    self.__interconnect.set("x position", eval(ele.attrib['x_position']))
                    self.__interconnect.set("y position", eval(ele.attrib['y_position']))
                    for sub_ele in list(ele):
                        for sub_propety in list(sub_ele):
                            attribute = sub_propety.attrib
                            # print(attribute)
                            if 'name' in attribute and 'value' in attribute:
                                print(attribute['name'], attribute['value'])
                                if self.is_number(attribute['value']):
                                    self.__interconnect.set(attribute['name'], eval(attribute['value']))
                                elif attribute['value'] == 'true':
                                    self.__interconnect.set(attribute['name'], 1)
                                elif attribute['value'] == 'false':
                                    self.__interconnect.set(attribute['name'], 0)
                                else:
                                    self.__interconnect.set(attribute['name'], attribute['value'])
                            elif 'name' in attribute and 'property' in attribute and 'exp' in attribute:
                                self.__interconnect.setexpression(attribute['name'], attribute['property'], attribute['exp'])

        for connect in root.findall("connect"):
            for ele_link in connect:
                print(ele_link.attrib)
                self.__interconnect.connect(ele_link.attrib['out_name'], ele_link.attrib['out_port'], ele_link.attrib['in_name'], ele_link.attrib['in_port'])

    def set_property(self, property_func):
        property_func(self.__interconnect)

    def run_simulation(self):
        self.__interconnect.run()

def test_Interconnect_step_1():
    def set_property(interconnect: lumapi.INTERCONNECT):
        filepath = os.getcwd()
        filepath = os.path.join(filepath, 'interconnect_source')

        interconnect.select("OM_1")
        interconnect.set("measurement filename", os.path.join(filepath, 'comsol_ret.txt'))

        interconnect.select("OM_2")
        interconnect.set("measurement filename", os.path.join(filepath, 'comsol_ret.txt'))

        interconnect.select("TW_2")
        interconnect.set("loss filename", os.path.join(filepath, 'loss.dat'))
        interconnect.set("characteristic impedance filename", os.path.join(filepath, 'Port Zo.dat'))
        interconnect.set("microwave index filename", os.path.join(filepath, 'neff.dat'))


    testModel = InterconnectModel()

    filepath = os.path.join(os.getcwd(), 'interconnect_source', 'Interconnect_modulator_step_1.xml')
    testModel.load_cfg(xmlfile=filepath)
    testModel.set_property(set_property)
    testModel.run_simulation()
    testModel.save_project(project_name='modulator')

def test_Interconnect_step_2():
    def set_property(interconnect: lumapi.INTERCONNECT):
        filepath = os.getcwd()
        filepath = os.path.join(filepath, 'interconnect_source')

        interconnect.select("TW_1")
        interconnect.set("loss filename", os.path.join(filepath, 'loss.dat'))
        interconnect.set("characteristic impedance filename", os.path.join(filepath, 'Port Zo.dat'))
        interconnect.set("microwave index filename", os.path.join(filepath, 'neff.dat'))


    testModel = InterconnectModel()

    filepath = os.getcwd()
    filepath = os.path.join(filepath, 'interconnect_source', 'Interconnect_modulator_step_2.xml')
    testModel.load_cfg(xmlfile=filepath)
    testModel.set_property(set_property)
    testModel.run_simulation()
    testModel.save_project(project_name='modulator_ENA')



if __name__ == '__main__':
    test_Interconnect_step_1()
    # test_Interconnect_step_2()

    # filepath = os.getcwd()
    # filepath = os.path.join(filepath, 'Interconnect_modulator_step_1.xml')
    # load_cfg(xmlfile=filepath)



