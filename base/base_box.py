import csv
import time
import yaml
import smtplib
import pymongo
import pymysql
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import unique, Enum
from tkinter.tix import Select
from selenium import webdriver
from selenium.webdriver import FirefoxProfile, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

'''  slenium 框架工具 '''
class Boxdriver(object):

    """ 私有全局变量 """
    _base_driver = None
    _by_char = None

    """ 构造方法 """
    def __init__(self, brower_type=0, by_char=",", profile=None):
        """
            构造方法：实例化 BoxDriver 时候使用
            :param browser_type: 浏览器类型
            :param by_char: 分隔符，默认使用","
            :param profile:
                可选择的参数，如果不传递，就是None
                如果传递一个 profile，就会按照预先的设定启动火狐
                去掉遮挡元素的提示框等
        """

        self._by_char = by_char

        if brower_type == 0 or brower_type == Browser.Chrome:

            profile = webdriver.ChromeOptions()
            profile.add_experimental_option("excludeSwitches", ["ignore-certidicate-errors"])
            driver = webdriver.Chrome(chrome_options=profile)

        elif brower_type == Browser.Firefox:
            if profile is not None:
                profile = FirefoxProfile(profile)

            driver = webdriver.Firefox(firefox_profile=profile)

        elif brower_type == Browser.Ie:
            driver = webdriver.Ie()
        else:
            driver = webdriver.PhantomJS()

        try:
            self._base_driver = driver
            self._by_char = by_char
        except Exception:
            raise  NameError("Browser %s Not Found! " % brower_type)

    """ 私有方法 """
    def  _concert_selector_to_locator(self, selector):
        """
            转换自定义的 selector 为 Selenium 支持的 locator
            :param selector: 定位字符，字符串类型，"i, xxx"
            :return: locator
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
        """
            to locate element by selector
            :arg
            selector should be passed by an example with "i,xxx"
            "x,//*[@id='langs']/button"
            :returns
            DOM element
        """
        locator = self._concert_selector_to_locator(selector)

        if locator is not None:
            element = self._base_driver.find_element(*locator)
        else:
            raise NameError("Please enter a valid locator of targeting elements.")

        return element

    def _locate_elements(self, selector):
        """
            to locate element by selector
            :arg
            selector should be passed by an example with "i,xxx"
            "x,//*[@id='langs']/button"
            :returns
            DOM element
        """
        locator = self._concert_selector_to_locator(selector)

        if locator is not None:
            elements = self._base_driver.find_elements(*locator)
        else:
            raise NameError("Please enter a valid locator of targeting elements.")

        return elements

    """
        Cookie是客户端(一般指浏览器)请求服务器后服务器发给客户端的一个辨认标识，
            保存在客户端，当客户端再次向服务器发送请求时，会携带着这个辨认标识，
            服务器就可以通过这个标识来识别客户端的身份或状态等
        Cookie的应用：保持用户登录状态， 记录用户名，记录用户浏览记录（信息）
    """
    """ Cookie 相关方法 """
    def clear_cookies(self):
        """ 在驱动程序init后清除所有cookie """
        self._base_driver.delete_all_cookies()

    def add_cookies(self, cookies):
        """
            按字典添加 cookies
        :param cookies:
        :return:
        """

        self._base_driver.add_cookie(cookie_dict=cookies)

    def add_cookie(self, cookie_dict):
        """
            Add single cookie by dict
        添加 单个 cookie
        如果该 cookie 已经存在，就先删除后，再添加
        :param cookie_dict: 字典类型，有两个key：name 和 value
        :return:
        """
        cookie_name = cookie_dict["name"]
        cookie_value = self._base_driver.get_cookie(cookie_name)
        if cookie_value is not None:
            self._base_driver.delete_cookie(cookie_name)

        self._base_driver.add_cookie(cookie_dict)

    def remove_cookie(self, name):
        """
        移除指定 name 的cookie
        :param name:
        :return:
        """
        # 检查 cookie 是否存在，存在就移除
        old_cookie_value = self._base_driver.get_cookie(name)

        if old_cookie_value is not None:
            self._base_driver.delete_cookie(name)

    """ 浏览器 相关方法"""
    def refresh(self, url=None):
        """
        刷新页面
            如果 url 是空值，就刷新当前页面，否则就刷新指定页面
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

    """ 页面元素 相关方法 """
    def type(self, selector, text):
        """
             操作输入框
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
        """
            将鼠标指针移动到指定元素地点
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        ActionChains(self._base_driver).move_to_element(el).perform()

    def right_click(self, selector):
        """
        用鼠标右键点击选择器
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        ActionChains(self._base_driver).context_click(el).perform()

    def count_elements(self, selector):
        """
        数一下元素的个数
        :param selector: 定位符
        :return:
        """
        els = self._locate_elements(selector)
        return len(els)

    def drag_element(self, source, target):
        """
        拖拽元素
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
        """
        当前元素丢失焦点
        :return:
        """
        ActionChains(self._base_driver).key_down(Keys.TAB).key_up(Keys.TAB).perform()

    """
    <select> 元素相关
    """
    def get_selected_text(self, selector):
        """
        获取 Select 元素的选择的内容
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

    """ JavaScript 相关 """
    def execute_js(self, script):
        """
            执行JavaScript脚本
        Usage:
        driver.js("window.scrollTo(200,1000);")
        """
        self._base_driver.execute_script(script)

    """ 元素属性相关方法 """

    def get_value(self, selector):
        """
        返回元素的 value
        :param selector: 定位字符串
        :return:
        """
        el = self._locate_element(selector)
        return el.get_attribute("value")

    def get_attribute(self, selector, attribute):
        """
        获取元素属性的值.
        Usage:
        driver.get_attribute("i,el","type")
        """
        el = self._locate_element(selector)
        return el.get_attribute(attribute)

    def get_text(self, selector):
        """
        获取元素文本信息
        Usage:
        driver.get_text("i,el")
        """
        el = self._locate_element(selector)
        return el.text

    def get_displayed(self, selector):
        """
        获取要显示的元素，返回的结果为真或假
        Usage:
        driver.get_display("i,el")
        """
        el = self._locate_element(selector)
        return el.is_displayed()

    def get_exist(self, selector):
        '''
        该方法用来确认元素是否存在，如果存在返回flag=true，否则返回false
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
        '''
        判断页面元素是否可点击
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
        """
            返回一个网站的选定状态
        :param selector: selector to locate
        :return: True False
        """
        el = self._locate_element(selector)
        return el.is_selected()

    def get_text_list(self, selector):
        """
        根据selector 获取多个元素，取得元素的text 列表
        :param selector:
        :return: list
        """

        el_list = self._locate_elements(selector)

        results = []
        for el in el_list:
            results.append(el.text)

        return results

    """ 窗口相关方法 """

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

    def switch_to_frame(self, selector):
        """ 切换到指定的窗口."""
        el = self._locate_element(selector)
        self._base_driver.switch_to.frame(el)

    def switch_to_default(self):
        """
        Returns the current form machine form at the next higher level.
        Corresponding relationship with switch_to_frame () method.

        Usage:
        driver.switch_to_frame_out()
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

    def save_window_snapshot(self, file_name):
        """
        保存屏幕截图
        :param file_name: the image file name and path
        :return:
        """
        driver = self._base_driver
        driver.save_screenshot(file_name)

    def save_window_snapshot_by_io(self):
        """
        保存截图为文件流
        :return:
        """
        return self._base_driver.get_screenshot_as_base64()

    def save_element_snapshot_by_io(self, selector):
        """
        控件截图
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        return el.screenshot_as_base64

    """  等待方法 """

    def forced_wait(self, seconds):
        """
        强制等待
        :param seconds:
        :return:
        """
        time.sleep(seconds)

    def implicitly_wait(self, seconds):
        """
        Implicitly wait. All elements on the page.
        :param seconds 等待时间 秒
        隐式等待

        Usage:
        driver.implicitly_wait(10)
        """
        self._base_driver.implicitly_wait(seconds)

    def explicitly_wait(self, selector, seconds):
        """
        显式等待
        :param selector: 定位字符
        :param seconds: 最长等待时间，秒
        :return:
        """
        locator = self._concert_selector_to_locator(selector)

        WebDriverWait(self._base_driver, seconds).until(expected_conditions.presence_of_element_located(locator))

    """
    表单数据提交:
        页面校验
        数据库校验
        某条记录选择，编辑，删除
    """

    def del_edit_choose_the_row(self, selector_of_next_page, selector_of_trs_td, selector_of_del_edit_choose,
                                expected_td_value):
        """
        页面表单，选中/编辑/删除 指定内容的行（带多页翻页功能）
        :param selector_of_next_page: ‘下一页’定位，如：'l,下页'
        :param selector_of_trs_td: 所有行的某一列的定位，如 ranzhi 成员列表中，获取所有行的“真实姓名”那列：'x,/html/body/div/div/div/div[2]/div/div/table/tbody//tr/td[2]'
        :param selector_of_del_edit_choose: 指定要操作(删除/编辑/选择)的列，如 ranzhi 成员列表中,获取期望删除的列：'x,/html/body/div/div/div/div[2]/div/div/table/tbody/tr[%d]/td[11]/a[3]'
        :param expected_td_value: 期望的列内容，如ranzhi 成员列表中期望的“真实姓名”: '华仔'
        :return:无
        """

        td_values = self.get_text_list(selector_of_trs_td)
        for i in range(len(td_values)):
            if td_values[i] == expected_td_value:
                print('%s在第%d行显示(首页)！' % (td_values[i], i + 1))
                self.forced_wait(2)
                self.click(selector_of_del_edit_choose % (i + 1))
                break
        try:
            while (self.get_enabled(selector_of_next_page)):
                self.click(selector_of_next_page)
                self.forced_wait(2)
                td_values = self.get_text_list(selector_of_trs_td)
                for i in range(len(td_values)):
                    if td_values[i] == expected_td_value:
                        print('%s在第%d行显示(非首页)' % (td_values[i], i + 1))
                        self.forced_wait(3)
                        self.click(selector_of_del_edit_choose % (i + 1))
                continue
        except Exception as e:
            print('%s 操作成功！' % expected_td_value)

    def assert_new_record_exist_in_table(self, selector_of_next_page, selector_of_trs_td, expected_td_value):
        '''
        此方法针对页面列表（带多页翻页功能），都可以判断新增记录是否添加成功！
        若新增成功，则返回 True 布尔值；否则返回 False 布尔值
        :param selector_of_next_page: "下一页"定位，如： 'l,下页'
        :param selector_of_trs_td:所有行的某一列的定位，如：'x,/html/body/div/div[2]/div/div[1]/div/table/tbody//tr/td[2]'
        :param expected_td_value:期望的列内容,如：'华仔'
        :return: 布尔值
        '''
        # first_count_per_page = self.count_elements(selector_of_real_record)
        # print('当前设置为每页显示 %s 条记录' % first_count_per_page)
        real_records = self.get_text_list(selector_of_trs_td)
        for real_record in real_records:
            if real_record == expected_td_value:
                return True
        # count_per_page_whiles = 0
        try:
            while (self.get_enabled(selector_of_next_page)):
                self.click(selector_of_next_page)
                self.forced_wait(2)
                # count_per_page_while = driver.count_elements("x,//tbody//tr/td[2]")
                # count_per_page_whiles += count_per_page_while
                next_page_real_records = self.get_text_list(selector_of_trs_td)
                for next_page_real_record in next_page_real_records:
                    if next_page_real_record == expected_td_value:
                        # self.log.info('记录新增成功！新增记录 %s 不是在第一页被找到！'%expect_new_record)
                        return True
                continue
        except Exception as e:
            # count_page_real_show = count_per_page_whiles + first_count_per_page
            # print("页面实际显示记录条数：%s" % count_page_real_show)
            # 页面统计总数 VS 页面实际显示记录总数
            # assert count_page_real_show == int(total_num)
            # print("‘页面实际显示记录总数’ 与 ‘页面统计显示记录总数’ 相同！")
            return False

    def assert_new_record_exist_mysql(self, db_yaml_path, db_yaml_name, sql_file_path, select_field_num,
                                      expected_td_value):
        '''
        数据库校验，True为数据库中存在该数据
        :param db_yaml_path: 数据库的yaml格式的配置文件路径
        :param db_yaml_name: 数据库的yaml格式的配置文件中设置的数据库名（默认是在'DbConfig'下面）
        :param sql_file_path: sql文件路径
        :param select_field_num: 查询语句中第几个字段（默认0表示第1个字段）
        :param expected_td_value: 期望要断言的值
        :return: True / False
        '''
        ydata = YamlHelper().get_config_dict(db_yaml_path)
        host = ydata['DbConfig'][db_yaml_name]['host']
        port = ydata['DbConfig'][db_yaml_name]['port']
        user = ydata['DbConfig'][db_yaml_name]['user']
        pwd = ydata['DbConfig'][db_yaml_name]['pwd']
        db = ydata['DbConfig'][db_yaml_name]['db']

        db_helper = DbHelper(host, port, user, pwd, db)
        sql = db_helper.read_sql(sql_file_path)
        result = db_helper.execute(sql)['data']
        db_helper.close()
        try:
            for i in result:
                if i[select_field_num] == expected_td_value:
                    return True
        except Exception:
            return False

''' MySQ 数据库帮助类 '''
class DbHelper(object):
    """
    MySQ 数据库帮助类
    """

    # 使用方法
    # 1. 实例化对象
    # 2. 查询，得到结果
    # 3. 关闭对象
    """
    db_helper = MysqlDbHelper("localhost", 3306, 'root', '', 'tpshop2.0.5', "utf8")
    for i in range(10000):

        result = db_helper.execute("select * from tp_goods order by 1 desc limit 1000;")
        print("第%d次，结果是%r" % (i, result))

    db_helper.close()
    """

    connect = None

    def __init__(self, host, port, user, password, database, charset='utf8'):
        """
        构造方法
        :param host: 数据库的主机地址
        :param port: 数据库的端口号
        :param user: 用户名
        :param password: 密码
        :param database: 选择的数据库
        :param charset: 字符集
        """
        self.connect = pymysql.connect(host=host, port=port,
                                       user=user, password=password,
                                       db=database, charset=charset)

    def read_sql(self, file, encoding="utf8"):
        """
        从 文件中读取 SQL 脚本
        :param file: 文件名 + 文件路径
        :return:
        """
        sql_file = open(file, "r", encoding=encoding)
        sql = sql_file.read()
        sql_file.close()
        return sql

    def execute(self, sql):
        """
        执行 SQL 脚本查询并返回结果
        :param sql: 需要查询的 SQL 语句
        :return: 字典类型
            data 是数据，本身也是个字典类型
            count 是行数
        """
        cursor = self.connect.cursor()

        row_count = cursor.execute(sql)
        rows_data = cursor.fetchall()
        result = {
            "count": row_count,
            "data": rows_data
        }

        cursor.close()
        return result

    def close(self):
        """
        关闭数据库连接
        :return:
        """
        self.connect.close()

''' yaml文件 '''
class YamlHelper(object):

    def get_config_dict(self, f):
        """
        获取所有配置
        :param f:
        :return:
        """
        with open(f, mode='r', encoding='utf8') as file_config:
            config_dict = yaml.load(file_config.read())
            return config_dict

""" 测试系统的最基础的页面类，是所有其他页面的基类 """
class BasePage(object):

    # 变量
    base_driver = None

    # 方法
    def __init__(self, driver: Boxdriver, logger=None):
        """
        构造方法
        :param driver: 指定了参数类型，BoxDriver
        """
        self.base_driver = driver

        self.logger = logger

    def open(self, url):
        """
        打开页面
        :param url:
        :return:
        """
        self.base_driver.navigate(url)
        self.base_driver.maximize_window()
        self.base_driver.forced_wait(2)

    def log(self, msg):
        """
        记录日志
        :param msg:
        :return:
        """
        if self.logger is not None:
            self.logger.info(msg)


''' csv文件 '''
class CsvHelper(object):

    def read_data(self, f, encoding="utf8"):
        """
        读csv文件作为普通list
        :param f:
        :return:
        """
        data_ret = []
        with open(f, encoding=encoding, mode='r') as csv_file:
            csv_data = csv.reader(csv_file)
            for row in csv_data:
                data_ret.append(row)

        return data_ret

    def read_data_as_dict(self, f, encoding="utf8"):
        """
        读csv文件作为普通list
        :param f:
        :return:
        """
        data_ret = []
        with open(f, encoding=encoding, mode='r') as csv_file:
            csv_dict = csv.DictReader(csv_file)
            for row in csv_dict:
                data_ret.append(row)

        return data_ret

class Email(object):

    def email_attachment(self,report_file):
        '''配置发送附件测试报告到邮箱'''
        '''发件相关参数'''
        try:
            # 发件服务器
            smtpserver = 'smtp.163.com'
            port = 25
            # 更改如下3项即可
            sender = '15926723093@163.com'
            psw = 'UUYRBQXQKBVJZQJX'
            receiver = 'Otaku.acgn@qq.com'
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

class MongodbConnect:

    def __init__(self,mongo_host,mongo_port,database,collection,user,pwd):
        """
        建立数据库连接
        (有认证方式 & 无认证方式 )
        :param mongo_host: MongoDB服务器IP
        :param mongo_port: MongoDB服务器端口
        :param database:   MongoDB数据库
        :param collection: MongoDB集合（表）
        :param user: （有认证方式，默认授权admin数据库）用户名
        :param pwd: （有认证方式，默认授权admin数据库）密码
        """

        mongo_host = mongo_host
        mongo_port = mongo_port
        self.client = pymongo.MongoClient('%s:%d' % (mongo_host, mongo_port))
        # 连接到数据库myDatabase
        database = database
        db = self.client[database]
        # 连接到集合(表):database.collection
        collection = collection
        self.db_col = db[collection]
        # mongoDB有不同的认证机制，3.0版本以后采用的是’SCRAM-SHA-1’, 之前的版本采用的是’MONGODB-CR’
        # user,pwd,针对的是 admin 数据库的认证
        if user != None and pwd != None:
            self.client.admin.authenticate(user, pwd, mechanism='SCRAM-SHA-1')

    def query(self, query_args):
        '''
        根据查询参数，返回查询结果
        :param q_find: MongoDB查询参数—find-查找
        :param q_sort: MongoDB查询参数—sort-排序,无此参数时，则输入为 None
        :param q_limit: MongoDB查询参数—limit-前几条,无此参数时，则输入为 None
        :param q_skip: MongoDB查询参数—skip-跳过第几条,无此参数时，则输入为 None
        :return: 数据库查询结果，字典形式
        '''
        try:
            # 字符串方式连接
            # a1 = ["db_col", "find({}, {'by_user': 1})", "sort('likes', -1)", "limit(2)"]
            # b1 = '.'.join(a1)
            # print(b1)

            if query_args['q_find'] != None and query_args['q_sort'] == None and query_args['q_limit'] == None and query_args['q_skip'] == None:
                self.search_result = self.db_col.find(*query_args['q_find'])
            elif query_args['q_find'] != None and query_args['q_sort'] != None and query_args['q_limit'] == None and query_args['q_skip'] == None:
                self.search_result = self.db_col.find(*query_args['q_find']).sort(*query_args['q_sort'])
            elif query_args['q_find'] != None and query_args['q_sort'] == None and query_args['q_limit'] != None and query_args['q_skip'] == None:
                self.search_result = self.db_col.find(*query_args['q_find']).limit(query_args['q_limit'])
            elif query_args['q_find'] != None and query_args['q_sort'] == None and query_args['q_limit'] != None and query_args['q_skip'] != None:
                self.search_result = self.db_col.find(*query_args['q_find']).limit(query_args['q_limit']).skip(query_args['q_skip'])
            elif query_args['q_find'] != None and query_args['q_sort'] != None and query_args['q_limit'] != None and query_args['q_skip'] == None:
                self.search_result = self.db_col.find(*query_args['q_find']).sort(*query_args['q_sort']).limit(query_args['q_limit'])
            elif query_args['q_find'] != None and query_args['q_sort'] != None and query_args['q_limit'] != None and query_args['q_skip'] != None:
                self.search_result = self.db_col.find(*query_args['q_find']).sort(*query_args['q_sort']).limit(query_args['q_limit']).skip(query_args['q_skip'])
            else:
                raise NameError("查询条件输入错误！")
            return self.search_result

        except:
            raise NameError('MongoDB认证方式，数据库查询失败！')

    def close(self):
        """关闭数据库连接，释放资源"""
        self.client.close()
        self.search_result.close()

@unique
class Browser(Enum):
    ''' 定义支持的浏览器, 支持 Chrome, Firefox, Ie '''
    Chrome = 0
    Firefox = 1
    Ie = 3

if __name__ == '__main__':
    pass
