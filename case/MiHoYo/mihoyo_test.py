from base.base_HTMLlTestRunner import TestCase
from base.base_box import BoxDriver, Browser
from biz.MiHoYo.main_page import MainPage


class MihoyoTest(TestCase):

    base_url = None
    main_page = None

    def set_up(self):
        """ 测试前置条件 """
        self.log("开始测试前置条件")
        self.base_driver = BoxDriver(Browser.Chrome)
        self.base_url = "https://www.mihayo.com/index.html"
        self.main_page = MainPage(self.base_driver, self.logger)
        self.log("完成测试前置条件")

    def tear_down(self):
        """ 测试收尾条件 """
        # 关闭浏览器
        self.base_driver.close_browser()

    def test_01(self):
        """  测试代码  """
        # 打开 米哈游 网站
        self.base_driver.navigate(self.base_url)
        # 最大化浏览器窗口
        self.base_driver.maximize_window()
        self.base_driver.implicitly_wait(2)
        # 刷新网页 默认刷新当前网页
        self.base_driver.refresh()
        self.base_driver.implicitly_wait(3)  # 等待 3S

        for i in range(1,6):
            self.main_page.page_select(i)

