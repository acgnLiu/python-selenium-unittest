import csv
import logging
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum, unique

import yaml
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


@unique
class Browser(Enum):
    ''' 定义支持的浏览器, 支持 Chrome, Firefox, Ie '''
    Chrome = 0
    Firefox = 1
    Ie = 3


class BoxDriver(object):
    """ 封装 selenium 工具中的方法 """

    _base_driver = None
    _by_char = None
    _browser_driver_path = None

    def __init__(self, brower_type=0, by_char=","):
        """  实例化 BoxDriver 时，选择要使用的浏览器。
        :param brower_type:
        :param browser_driver_path:
        """
        self._by_char = by_char

        if brower_type == 0 or brower_type == Browser.Chrome:
            driver = webdriver.Chrome()
        elif brower_type == 1 or brower_type == Browser.Firefox:
            driver = webdriver.Firefox()
        elif brower_type == 2 or brower_type == Browser.Ie:
            driver = webdriver.Ie()
        else:
            driver = webdriver.PhantomJS()

        # 未能打开浏览器时，抛出异常
        try:
            self._base_driver = driver
            self._by_char = by_char
        except Exception:
            raise NameError("Browser %s Not Found! " % brower_type)

    def _concert_selector_to_locator(self, selector):
        """  将自定义定位元素 selector 格式 转换为 Selenium 支持的 locator 格式
            :param selector: 定位字符，字符串类型，"i, xxx"
            :return: locator: "By.ID, value"
        """
        if self._by_char not in selector:
            return By.ID, selector

        # 拆分 "i, xxx"
        selector_by = selector.split(self._by_char)[0].strip()
        selector_value = selector.split(self._by_char)[1].strip()

        # 定位方法
        if selector_by == "i" or selector_by == "id":
            locator = (By.ID, selector_value)
        elif selector_by == "n" or selector_by == "name":
            locator = (By.NAME, selector_value)
        elif selector_by == "c" or selector_by == "class_name":
            locator = (By.CLASS_NAME, selector_value)
        elif selector_by == "l" or selector_by == "link_text":
            locator = (By.LINK_TEXT, selector_value)
        elif selector_by == "p" or selector_by == "partial_link_text":
            locator = (By.PARTIAL_LINK_TEXT, selector_value)
        elif selector_by == "t" or selector_by == "tag_name":
            locator = (By.TAG_NAME, selector_value)
        elif selector_by == "x" or selector_by == "xpath":
            locator = (By.XPATH, selector_value)
        elif selector_by == "s" or selector_by == "css_selector":
            locator = (By.CSS_SELECTOR, selector_value)
        else:
            raise NameError("Please enter a valid selector of targeting elements.")

        return locator

    def _locate_element(self, selector):
        """  查找页面中符合条件的第一个节点,并返回，没有找到会报错。
        :param selector:定位字符，字符串类型，"i, xxx"
        :return:  /
        """
        locator = self._concert_selector_to_locator(selector)

        if locator is not None:
            self._base_driver.find_element(*locator)
        else:
            raise NameError("Please enter a valid locator of targeting elements.")

    def _locate_elements(self, selector):
        """  查找页面中符合条件的多个节点,并返回列表，没有找到不会报错，列表返回为空。
        :param selector:定位字符，字符串类型，"i, xxx"
        :return: /
        """

        locator = self._concert_selector_to_locator(selector)

        if locator is not None:
            self._base_driver.find_elements(*locator)
        else:
            raise NameError("Please enter a valid locator of targeting elements.")

    """ cookies 相关方法 """

    def clear_all_cookies(self):
        """  驱动初始化后，清除浏览器所有的cookies。
        :return:  /
        """
        self._base_driver.delete_all_cookies()

    def add_dict_cookies(self, cookie_dict):
        """  按字典的格式添加cookie，如果cookie已存在，则先删除后添加。
        :param cookie_dict:
        :return:
        """
        cookie_name = cookie_dict["name"]
        cookie_value = self._base_driver.get_cookie(cookie_name)

        if cookie_value is not None:
            self._base_driver.delete_cookie(cookie_name)
        self._base_driver.add_cookie(cookie_dict)

    def remove_name_cookies(self, name):
        """  删除指定name的cookie。
        :param name:
        :return: /
        """
        old_cookies_value = self._base_driver.get_cookie(name)

        if old_cookies_value is not None:
            self._base_driver.delete_cookie(name)

    """ 浏览器 相关方法 """

    def refresh(self, url=None):
        """ 刷新页面，如果 url 是空值，就刷新当前页面，否则就刷新指定页面
        :param url: 默认值： None
        :return:
        """
        if url is None:
            self._base_driver.refresh()
        else:
            self._base_driver.get(url)

    def maximize_window(self):
        """ 最大化当前浏览器的窗口 """
        self._base_driver.maximize_window()

    def navigate(self, url):
        """ 打开 URL """
        self._base_driver.get(url)

    def quit(self):
        """ 退出 驱动 """
        self._base_driver.quit()

    def close_browser(self):
        """ 关闭浏览器 """
        self._base_driver.close()

    """ web页面元素、鼠标等相关操作方法 """

    def type(self, selector, text):
        """ 操作输入框
        :param selector: "i, XXX"
        :param text:
        :return:
        """
        el = self._locate_element(selector)
        el.clear()
        el.send_keys(text)

    def click(self, selector):
        """ 鼠标点击 """
        el = self._locate_element(selector)
        el.click()

    def click_by_enter(self, seletor):
        """ 回车确认键 【enter】"""
        el = self._locate_element(seletor)
        el.send_keys(Keys.ENTER)

    def click_by_text(self, text):
        """ 通过链接文本单击元素 """
        self._locate_element('p%s' % self._by_char + text).click()

    def submit(self, selector):
        """ 递交指定表格 """
        el = self._locate_element(selector)
        el.submit()

    def move_to(self, selector):
        """ 将鼠标指针移动到指定元素地点
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        ActionChains(self._base_driver).move_to_element(el).perform()

    def right_click(self, selector):
        """ 用鼠标右键点击选择器
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        ActionChains(self._base_driver).context_click(el).perform()

    def count_elements(self, selector):
        """ 数一下元素的个数
        :param selector: 定位符
        :return:
        """
        els = self._locate_elements(selector)
        return len(els)

    def drag_element(self, source, target):
        """ 拖拽元素
        :param source:
        :param target:
        :return:
        """

        el_source = self._locate_element(source)
        el_target = self._locate_element(target)

        if self._base_driver.w3c:
            ActionChains(self._base_driver).drag_and_drop(el_source, el_target).perform()
        else:
            ActionChains(self._base_driver).click_and_hold(el_source).perform()
            ActionChains(self._base_driver).move_to_element(el_target).perform()
            ActionChains(self._base_driver).release(el_target).perform()

    def lost_focus(self):
        """ 当前元素丢失焦点
        :return:
        """
        ActionChains(self._base_driver).key_down(Keys.TAB).key_up(Keys.TAB).perform()

    """ web页面下拉框 相关处理方法"""

    def get_selected_text(self, selector):
        """ 获取 Select 元素的选择的内容
        :param selector: 选择字符 "i, xxx"
        :return: 字符串
        """
        el = self._locate_element(selector)
        selected_opt = Select(el).first_selected_option()
        return selected_opt.text

    def select_by_index(self, selector, index):
        """ index的方式 点击选择复选框，单选按钮，甚至下拉框 """
        el = self._locate_element(selector)
        Select(el).select_by_index(index)

    def select_by_visible_text(self, selector, text):
        """ text的方式 点击选择复选框，单选按钮，甚至下拉框 """
        el = self._locate_element(selector)
        Select(el).select_by_visible_text(text)

    def select_by_value(self, selector, value):
        """ value的方式 点击选择复选框，单选按钮，甚至下拉框 """
        el = self._locate_element(selector)
        Select(el).select_by_value(value)

    """ web页面 获取元素属性  相关方法 """

    def get_value(self, selector):
        """ 返回元素的 value
        :param selector: 定位字符串
        :return:
        """
        el = self._locate_element(selector)
        return el.get_attribute("value")

    def get_attribute(self, selector, attribute):
        """ 获取元素属性的值.
        Usage:
        driver.get_attribute("i,el","type")
        """
        el = self._locate_element(selector)
        return el.get_attribute(attribute)

    def get_text(self, selector):
        """ 获取元素文本信息
        Usage:
        driver.get_text("i,el")
        """
        el = self._locate_element(selector)
        return el.text

    def get_displayed(self, selector):
        """ 获取要显示的元素，返回的结果为真或假
        Usage:
        driver.get_display("i,el")
        """
        el = self._locate_element(selector)
        return el.is_displayed()

    def get_exist(self, selector):
        ''' 该方法用来确认元素是否存在，如果存在返回flag=true，否则返回false
        :param self:
        :param selector: 元素定位，如'id,account'
        :return: 布尔值
        '''
        flag = True
        try:
            self._locate_element(selector)
            return flag
        except:
            flag = False
            return flag

    def get_enabled(self, selector):
        ''' 判断页面元素是否可点击
        :param selector: 元素定位
        :return: 布尔值
        '''
        if self._locate_element(selector).is_enabled():
            return True
        else:
            return False

    def get_title(self):
        ''' 获取 窗口标题. '''
        return self._base_driver.title

    def get_url(self):
        """获取当前页面的URL地址"""
        return self._base_driver.current_url

    def get_selected(self, selector):
        """ 返回一个网站的选定状态
        :param selector: selector to locate
        :return: True False
        """
        el = self._locate_element(selector)
        return el.is_selected()

    def get_text_list(self, selector):
        """ 根据selector 获取多个元素，取得元素的text 列表
        :param selector:
        :return: list
        """

        el_list = self._locate_elements(selector)

        results = []
        for el in el_list:
            results.append(el.text)

        return results

    """ web页面alert警告框 相关处理方法 """

    def accept_alert(self):
        ''' 接受警告框. '''
        self._base_driver.switch_to.alert.accept()

    def dismiss_alert(self):
        ''' 取消可用的警报.'''
        self._base_driver.switch_to.alert.dismiss()

    def get_alert_text(self):
        ''' 获取alert 弹框的文本'''
        text = self._base_driver.switch_to.alert.text
        return text

    """ web页面窗口 相关处理方法 """

    def switch_to_frame(self, selector):
        """ 切换到指定的窗口."""
        el = self._locate_element(selector)
        self._base_driver.switch_to.frame(el)

    def switch_to_default(self):
        """
        Returns the current form machine form at the next higher level.
        """
        self._base_driver.switch_to.default_content()

    def switch_to_window_by_title(self, title):

        for handle in self._base_driver.window_handles:
            self._base_driver.switch_to.window(handle)
            if self._base_driver.title == title:
                break

            self._base_driver.switch_to.default_content()

    def open_new_window(self, selector):
        ''' 打开新窗口，并切换手柄到新打开的窗口  '''
        original_windows = self._base_driver.current_window_handle
        el = self._locate_element(selector)
        el.click()
        all_handles = self._base_driver.window_handles
        for handle in all_handles:
            if handle != original_windows:
                self._base_driver._switch_to.window(handle)

    """ 屏幕截图 相关方法"""

    def save_window_snapshot(self, file_name):
        """ 保存屏幕截图
        :param file_name: the image file name and path
        :return:
        """
        driver = self._base_driver
        driver.save_screenshot(file_name)

    def save_window_snapshot_by_io(self):
        """ 保存截图为文件流
        :return:
        """
        return self._base_driver.get_screenshot_as_base64()

    def save_element_snapshot_by_io(self, selector):
        """ 控件截图
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        return el.screenshot_as_base64

    """ JavaScript  相关方法 """

    def execute_js(self, script):
        """ 执行JavaScript脚本
        Usage:
        driver.js("window.scrollTo(200,1000);")
        """
        self._base_driver.execute_script(script)

    """  等待方法 """

    def forced_wait(self, seconds):
        """  强制等待
        :param seconds:
        :return:
        """
        time.sleep(seconds)

    def implicitly_wait(self, seconds):
        """ 隐式等待
        :param seconds 等待时间 秒
        """
        self._base_driver.implicitly_wait(seconds)

    def explicitly_wait(self, selector, seconds):
        """ 显式等待
        :param selector: 定位字符
        :param seconds: 最长等待时间，秒
        :return:
        """
        locator = self._concert_selector_to_locator(selector)

        WebDriverWait(self._base_driver, seconds).until(expected_conditions.presence_of_element_located(locator))


class DataHelper(object):
    """ 数据文件 处理"""

    """ csv数据文件 相关操作 """

    def csv_read_data_as_list(self, f, encoding="utf8"):
        """  读取csv文件并以列表形式返回
        :param f:  csv 文件路径
        :param encoding: 字符编码格式
        :return: data_ret 列表类型数据
        """
        data_ret = []
        with open(f, encoding=encoding, mode="r") as csv_file:
            csv_data = csv.reader(csv_file)
            for row in csv_data:
                data_ret.append(row)

        return data_ret

    def csv_read_data_as_dict(self, f, encoding="utf8"):
        data_ret = []
        with open(f, encoding=encoding, mode="r") as csv_file:
            csv_data = csv.DictReader(csv_file)
            for row in csv_data:
                data_ret.append(row)

        return data_ret

    """ yaml数据文件 相关操作 """

    def yaml_get_config_dict(self, f):
        """  获取 yaml文件内所有数据
        :param f: yaml文件类型
        :return: 返回字典类型数据 config_dict
        """
        with open(f, mode='r', encoding='utf8') as file_config:
            config_dict = yaml.load(file_config.read())
            return config_dict


class TestLogger(object):
    """ 测试框架调试日志文件  相关方法"""

    def __init__(self, log_path):
        """   日志文件命名
        :param log_path: 日志存放路径
        """
        self.file_name = log_path
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        # 日志输出格式
        self.formatter = logging.Formatter('[%(asctime)s]-[%(filename)s]-[%(levelname)s]: %(message)s')

    def info(self, message):
        """  添加信息日志
        :param message:
        :return:
        """
        self._console("info", message)

    def warning(self, message):
        """  添加警告日志
        :param message:
        :return:
        """
        self._console("warning", message)

    def error(self, message):
        """  添加错误日志
        :param message:
        :return:
        """
        self._console("error", message)

    def _console(self, level, message):
        # 创建一个FileHandler，用于写到本地
        fh = logging.FileHandler(self.file_name, 'a', encoding='utf8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # 创建一个SteamHandler,用于输出到控制台
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)

        self.logger.addHandler(ch)
        if level == 'info':
            self.logger.info(message)
        elif level == 'debug':
            self.logger.debug(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)

        # 这两行代码为了避免日志输出重复
        self.logger.removeHandler(ch)
        self.logger.removeHandler(fh)
        fh.close()


''' csv文件 '''
class Email(object):
    """ 邮箱 发送"""

    def email_attachment(self, report_file):
        '''配置发送附件测试报告到邮箱'''
        '''发件相关参数'''
        try:
            # 发件服务器
            smtpserver = 'smtp.163.com'
            port = 25
            # 更改如下3项即可
            sender = ''
            psw = ''
            receiver = ''
            msg = MIMEMultipart()
            msg['from'] = sender
            msg['to'] = ';'.join(receiver)
            msg['subject'] = '这个是zentao项目自动化测试报告主题'
            '''读取测试报告内容'''
            with open(report_file, 'rb') as rp:
                zentao_mail_body = rp.read()
            '''正文'''
            body = MIMEText(zentao_mail_body, 'html', 'utf8')
            msg.attach(body)
            '''附件'''
            att = MIMEText(zentao_mail_body, 'base64', 'utf8')
            att['Content-Type'] = 'application/octet-stream'
            att['Content-Disposition'] = 'attachment;filename = "%s"' % report_file
            msg.attach(att)
            '''发送邮件'''
            smtp = smtplib.SMTP()
            smtp.connect(smtpserver, port)
            smtp.login(sender, psw)
            smtp.sendmail(sender, receiver.split(';'), msg.as_string())  # 发送
            smtp.close()
            print("邮件发送成功!")
        except Exception as e:
            print(e)
            print("邮件发送失败!")


""" 测试系统的最基础的页面类，是所有其他页面的基类 """


class BasePage(object):
    base_driver = None

    def __init__(self, driver: BoxDriver, logger=None):
        """  构造方法
        :param driver: 指定了参数类型，BoxDriver
        :param logger:
        """
        self.base_driver = driver
        self.logger = logger

    def open(self, url):
        """   打开页面
        :param url: 页面链接地址
        """
        self.base_driver.navigate(url)
        self.base_driver.maximize_window()
        self.base_driver.forced_wait(2)

    def log(self, msg):
        """   记录日志
        :param msg:
        """
        if self.logger is not None:
            self.logger.info(msg)
