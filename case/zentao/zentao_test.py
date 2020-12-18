from base.base_HTMLlTestRunner import TestCase
from base.base_box import BoxDriver, Browser
from biz.zentao.login_page import LoginPage

class ZentaoTest(TestCase):

    base_url = None
    main_page = None

    def set_up(self):
        """ 测试前置条件 """
        self.log("开始测试前置条件")
        self.base_driver = BoxDriver(Browser.Chrome)
        self.base_url = "https://demo.zentao.net/user-login.html"
        self.login_page = LoginPage(self.base_driver, self.logger)
        self.log("完成测试前置条件")

    def tear_down(self):
        """ 测试收尾条件 """
        self.base_driver.quit()

    def test_01(self):
        """  测试代码  """

        # 读取测试用例输入数据
        "D:/MrLiu_User/GitHubPycharmCode/python-selenium-unittest/case/data/csv/"
        "../case/data/csv/"
        csv_data = self.read_csv_as_dict("D:/MrLiu_User/GitHubPycharmCode/python-selenium-unittest/case/data/csv/"
                                         + "zentao_test.csv")


        # 调用业务逻辑方法测试测试点
        for row in csv_data:
            account = row["用户名"].strip()
            password = row["密码"].strip()
            self.login_page.open(self.base_url)
            # self.login_page.login_and_submit(account, password)
            # 这里对当前步骤进行截图
            # self.snapshot()
            # 获取登陆后的网页标题(实际结果)
            actual_url = self.login_page.get_loging_title()

            # 预期结果
            expected_url = "我的地盘 - 禅道"
            # 断言：预期结果与实际结果对比
            self.assertEqual(expected_url, actual_url, "登陆前后，网页标题不匹配！")
