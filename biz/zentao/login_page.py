from base.base_box import BasePage


class LoginPage(BasePage):

    # 读取数据
    # base_driver = None
    # config_dict = YamlHelper().get_config_dict("biz/ranzhi.yaml")["LoginPage"]

    def input_login_info(self, account, password):
        """
            输入用户名密码
        :param account:
        :param password:
        :return:
        """
        print("start")
        self.base_driver.type("i,account", account)
        self.base_driver.type("n,password", password)
        self.base_driver.forced_wait(2)
        print("finish")

    def do_login(self):
        """
        点击登录按钮
        :return:
        """
        self.base_driver.click("i, submit")
        self.base_driver.forced_wait(2)

    def login_and_submit(self, account, password):
        """登录系统"""
        # 输入用户名 密码
        self.base_driver.forced_wait(2)
        self.base_driver.type("i,account", account)
        self.base_driver.type("n,password", password)
        self.base_driver.click("i,submit")

    def login_by_cookie(self, cookie_dict, url=None):
        """
        使用 cookie 登录系统。
        :param url:
        :param cookie_dict: cookie 字典，有两个 key：name 和 value
        :return:
        """
        self.base_driver.add_cookie(cookie_dict)
        self.base_driver.refresh(url)
        self.base_driver.forced_wait(2)

    def get_current_keep_value(self):
        """
        获取当前的 保持登录 复选框 的值
        :return:
        """
        return self.base_driver.get_attribute("i,keepLoginon", "checkbox")

    def change_language(self, lang):
        """
        更改 登录页面语言
        :param lang: en, zh_CN, zh_TW
        :return:
        """
        self.base_driver.click('s,#langs > button')
        self.base_driver.forced_wait(1)

        if lang == "en":
            lang_number = 3
        elif lang == "zh_CN":
            lang_number = 1
        elif lang == "zh_TW":
            lang_number = 2
        else:
            lang_number = 0

        self.base_driver.click("s,langs > ul > li:nth-child(%d) > a" % lang_number)
        self.base_driver.forced_wait(2)

    def get_text_dict_for_language(self):
        """
        获取当前页面的文字，语言按钮和登录按钮，以字典类型返回
        :return: 字典
        """
        lang_button_text = self.base_driver.get_text('s,#langs > button')
        login_button_text = self.base_driver.click("i, submit")
        text_dict = {
            "lang": lang_button_text,
            "login": login_button_text
        }
        return text_dict

    def get_fail_login_message(self):
        """ 返回登录失败alert弹窗的文本 """
        return self.base_driver.get_alert_text()

    def get_loging_title(self):
        """ 获取当前网页标题 """
        return self.base_driver.get_title()
