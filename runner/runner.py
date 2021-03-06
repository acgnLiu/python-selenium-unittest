import time
from base.base_HTMLlTestRunner import HTMLTestRunner, TestSuite
from base.base_box import DataHelper
from case.MiHoYo.mihoyo_test import MihoyoTest


class Runner(object):

    def run_test(self):
        """  运行测试
        """
        suite = TestSuite()

        csv_data = DataHelper().csv_read_data_as_dict("runner/data/runner.csv")

        test_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())

        logger_file = "./runner/log/zentao_automate_log_%s.log" % test_time

        for row in csv_data:

            test_class = row["class"]
            test_method = row["test"]
            test_count = int(row["count"])

            for i in range(test_count):
                # 增加测试用例，这里要增加
                if test_class == "MihoyoTest":
                    suite.add_test(MihoyoTest(test_method, logger_file))

        # 测试报告的文件

        report_file = "./runner/report/zentao_automate_report_%s.html" % test_time

        runner = HTMLTestRunner(file_name=report_file,
                            verbosity=2,
                            title="自动化测试报告",
                            description="具体测试报告内容如下: ")
        runner.run(suite)

        # 发送测试报告到指定邮箱

        # Email().email_attachment(report_file)

