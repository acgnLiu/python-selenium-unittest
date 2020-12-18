import os
import time

from base.base_box import BasePage, DataHelper, Browser, BoxDriver


class MainPage(BasePage):
    """ 米哈游 主页 """

    base_driver = None
    # # 获取当前文件路径
    current_path = os.path.abspath(__file__)
    # # 获取当前文件的父目录
    # father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
    # # config.ini文件路径,获取当前目录的父目录的父目录与congig.ini拼接
    main_data_path = os.path.join(os.path.abspath(os.path.dirname(current_path) + os.path.sep + "./data/"), 'main_data.yaml')

    main_selector = DataHelper().yaml_get_config_dict(main_data_path)["MAIN_SELECTOR"]

    def page_select(self, choose):
        """ MiHoYo 主界面 选择 """

        if choose == 1:
            # 点击 “mihoyo” 图标
            mihoyo_1 = self.main_selector["X_MAIN_SELECTOR"] % choose
            # 检测 web页面元素 是否存在
            if self.base_driver.get_exist(mihoyo_1):
                self.base_driver.click(mihoyo_1)
                self.base_driver.implicitly_wait(2)
        elif choose == 2:
            # 点击 “公司简介”
            mihoyo_2 = self.main_selector["X_MAIN_SELECTOR"] % choose
            if self.base_driver.get_exist(mihoyo_2):
                self.base_driver.click(mihoyo_2)
                self.base_driver.implicitly_wait(2)
        elif choose == 3:
            # 点击 “产品信息”
            mihoyo_3 = self.main_selector["X_MAIN_SELECTOR"] % choose
            if self.base_driver.get_exist(mihoyo_3):
                self.base_driver.click(mihoyo_3)
                self.base_driver.implicitly_wait(2)
        elif choose == 4:
            # 点击 “加入我们”
            mihoyo_4 = self.main_selector["X_MAIN_SELECTOR"] % choose
            if self.base_driver.get_exist(mihoyo_4):
                self.base_driver.click(mihoyo_4)
                self.base_driver.implicitly_wait(2)
        elif choose == 5:
            # 点击 “联系我们”
            mihoyo_5 = self.main_selector["X_MAIN_SELECTOR"] % choose
            if self.base_driver.get_exist(mihoyo_5):
                self.base_driver.click(mihoyo_5)
                self.base_driver.implicitly_wait(2)

if __name__ == '__main__':

    MainPage(BoxDriver(Browser.Chrome)).page_select(3)
    time.sleep(3)
