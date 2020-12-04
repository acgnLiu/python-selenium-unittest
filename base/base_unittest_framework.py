import contextlib
import datetime
import io
import sys
import time
from unittest import TestCase, TestResult, TestProgram, TestSuite, SkipTest
from xml.sax import saxutils

from base.HtmlTestRunner import _TemplateReport, __version__, stdout_redirect, stderr_redirect
from base.base_box import TestLogger, DataHelper


class TestCase(TestCase):
    ''' 重构 TestCase 类 '''
    images = None
    base_driver = None
    logger = None

    def __init__(self, methodName='runTest', logger_file=None):
        """ 重新 TestCase的构造方法，并继承 methodName """
        super().__init__(methodName)

        if self.images is not None:
            self.images = []
        if logger_file is not None:
            self.logger = TestLogger(logger_file)
        else:
            test_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            self.logger = TestLogger("test_log_%s.log" % test_time)

    def set_up(self):
        """
        :return:
        """
        pass

    def tear_down(self):
        """
        :return:
        """
        pass

    def run(self, result=None):
        """
        :param result:
        :return:
        """
        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()

        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        if (getattr(self.__class__, "__unittest_skip__", False) or
                getattr(testMethod, "__unittest_skip__", False)):
            # If the class or method was skipped.
            try:
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            or getattr(testMethod, '__unittest_skip_why__', ''))
                self._addSkip(result, self, skip_why)
            finally:
                result.stopTest(self)
            return
        expecting_failure_method = getattr(testMethod,
                                           "__unittest_expecting_failure__", False)
        expecting_failure_class = getattr(self,
                                          "__unittest_expecting_failure__", False)
        expecting_failure = expecting_failure_class or expecting_failure_method
        outcome = _Outcome(result)
        try:

            self._outcome = outcome

            with outcome.testPartExecutor(self):
                self.set_up()
            if outcome.success:
                outcome.expecting_failure = expecting_failure
                with outcome.testPartExecutor(self, isTest=True):
                    testMethod()
                outcome.expecting_failure = False

                # 尝试异常继续运行
                with outcome.testPartExecutor(self):
                    self.tear_down()

            for test, reason in outcome.skipped:
                self._addSkip(result, test, reason)
            self._feedErrorsToResult(result, outcome.errors)
            if outcome.success:
                if expecting_failure:
                    if outcome.expectedFailure:
                        self.snapshot()
                        self._addExpectedFailure(result, outcome.expectedFailure)
                    else:
                        self._addUnexpectedSuccess(result)
                else:
                    result.addSuccess(self)

            self.doCleanups()
            return result
        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

            outcome.errors.clear()
            outcome.expectedFailure = None

            self._outcome = None

    def snapshot(self):
        """  截图
        :return:
        """
        self.images.append(self.base_driver.save_window_snapshot_by_io())

    def log(self, msg):
        """  添加日志
        :param msg:
        :return:
        """
        if self.logger is not None:
            self.logger.info(msg)

    def read_csv_as_dict(self, file_name):
        """ 读 CSV 作为 DICT 类型
        :type file_name: csv 文件路径 和名字
        :return:
        """
        return DataHelper().csv_read_data_as_dict(file_name)

    def shortDescription(self):
        """Returns a one-line description of the test, or None if no
        description has been provided.
        The default implementation of this method returns the first line of
        the specified test method's docstring.
        """
        doc = self._testMethodDoc
        # 修改前：
        # 执行多条用例是报错：IndexError: list index out of range
        # return doc and doc.split("\n")[1].strip() or None

        # 修改后 无报错。
        try:
            return doc and doc.split("\n")[1].strip() or None
        except:
            return None


class _Outcome(object):
    def __init__(self, result=None):
        self.expecting_failure = False
        self.result = result
        self.result_supports_subtests = hasattr(result, "addSubTest")
        self.success = True
        self.skipped = []
        self.expectedFailure = None
        self.errors = []

    @contextlib.contextmanager
    def testPartExecutor(self, test_case, isTest=False):
        old_success = self.success
        self.success = True
        try:
            yield
        except KeyboardInterrupt:
            raise
        except SkipTest as e:
            self.success = False
            self.skipped.append((test_case, str(e)))
        # except _ShouldStop:
        #     pass
        except:
            exc_info = sys.exc_info()
            if self.expecting_failure:
                self.expectedFailure = exc_info
            else:
                self.success = False
                test_case.images.append(test_case.base_driver.save_window_snapshot_by_io())

                self.errors.append((test_case, exc_info))
            exc_info = None
        else:
            if self.result_supports_subtests and self.success:
                self.errors.append((test_case, None))
        finally:
            self.success = self.success and old_success


class _TestResult(TestResult):
    # note: _TestResult is a pure representation of results.
    # It lacks the output and reporting ability compares to unittest._TextTestResult.

    def __init__(self, verbosity=1):
        super().__init__(verbosity=verbosity)
        self.outputBuffer = io.StringIO()
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.verbosity = verbosity

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []

    def startTest(self, test):
        TestResult.startTest(self, test)
        # just one buffer for both stdout and stderr
        stdout_redirect.fp = self.outputBuffer
        stderr_redirect.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirect
        sys.stderr = stderr_redirect

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        self.complete_output()

    def addSuccess(self, test):
        self.success_count += 1
        TestResult.addSuccess(self, test)
        if getattr(test, 'logger', TestLogger):
            test.logger.info("测试用例执行成功")
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def addError(self, test, err):
        self.error_count += 1
        TestResult.addError(self, test, err)
        if getattr(test, 'logger', TestLogger):
            test.logger.error("测试用例执行异常：%s" % str(err))

        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))

        # if not getattr(test, "base_driver", ""):
        #     pass
        # else:
        #     try:
        #         driver = getattr(test, "base_driver")
        #         test.images.append(driver.save_window_snapshot_by_io())
        #     except Exception as e:
        #         pass

        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test, err):
        self.failure_count += 1
        TestResult.addFailure(self, test, err)
        if getattr(test, 'logger', TestLogger):
            test.logger.error("测试用例执行失败：%s" % str(err))
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))

        # if not getattr(test, "base_driver", ""):
        #     pass
        # else:
        #     try:
        #         driver = getattr(test, "base_driver")
        #         test.images.append(driver.save_window_snapshot_by_io())
        #     except Exception as e:
        #         pass

        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')


class TestRunner(_TemplateReport):
    """  HtmlTestRunner """
    file_name = None

    def __init__(self, file_name, verbosity=1, title=None, description=None):
        """
        initialize
        :param stream:
        :param verbosity:
        :param title:
        :param description:
        """

        self.file_name = file_name
        self.verbosity = verbosity
        if title is None:
            self.title = self.DEFAULT_TITLE
        else:
            self.title = title
        if description is None:
            self.description = self.DEFAULT_DESCRIPTION
        else:
            self.description = description

        self.startTime = datetime.datetime.now()

    def run(self, test):
        """
        Run the given test case or test suite.
        :param test:
        :return:
        """
        with open(self.file_name, mode="wb") as stream:
            self.stream = stream
            result = _TestResult(self.verbosity)
            test(result)
            self.stopTime = datetime.datetime.now()
            self.generate_report(test, result)
            print('Time Elapsed 花费时间: %s' % (self.stopTime - self.startTime))

        return result

    def sort_result(self, result_list):
        # unittest does not seems to run in any particular order.
        # Here at least we want to group them together by class.
        rmap = {}
        classes = []
        for n, t, o, e in result_list:
            cls = t.__class__
            if not cls in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n, t, o, e))
        r = [(cls, rmap[cls]) for cls in classes]
        return r

    def get_report_attributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)
        status = []
        if result.success_count: status.append(
            '<span class="text text-success">Pass <strong>%s</strong></span>' % result.success_count)
        if result.failure_count: status.append(
            '<span class="text text-danger">Failure <strong>%s</strong></span>' % result.failure_count)
        if result.error_count:   status.append(
            '<span class="text text-warning">Error <strong>%s</strong></span>' % result.error_count)
        if status:
            status = ' '.join(status)
        else:
            status = 'none'
        return [
            ('Start Time 开始时间', startTime),
            ('Duration 用时', duration),
            ('Status 状态', status),
        ]

    def generate_report(self, test, result):
        report_attrs = self.get_report_attributes(result)
        generator = 'HtmlTestRunner %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report(result)
        ending = self._generate_ending()
        output = self.HTML_TMPL % dict(
            title=saxutils.escape(self.title),
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            report=report,
            ending=ending,
        )
        self.stream.write(output.encode())

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                # name = saxutils.escape(name),
                # value = saxutils.escape(value),
                name=name,
                value=value,
            )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title=saxutils.escape(self.title),
            parameters=''.join(a_lines),
            description=saxutils.escape(self.description),
        )
        return heading

    def _generate_report(self, result):
        rows = []
        sortedResult = self.sort_result(result.result)
        for cid, (cls, cls_results) in enumerate(sortedResult):
            # subtotal for a class
            np = nf = ne = 0
            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1

            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = "%s.%s" % (cls.__module__, cls.__name__)
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            desc = doc and '%s: %s' % (name, doc) or name

            row = self.REPORT_CLASS_TMPL % dict(
                style=ne > 0 and 'text text-warning' or nf > 0 and 'text text-danger' or 'text text-success',
                desc=desc,
                count=np + nf + ne,
                Pass=np,
                fail=nf,
                error=ne,
                cid='c%s' % (cid + 1),
            )
            rows.append(row)

            for tid, (n, t, o, e) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, e)

        report = self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(result.success_count + result.failure_count + result.error_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
        )
        return report

    def _generate_report_test(self, rows, cid, tid, n, t, o, e):
        # e.g. 'pt1.1', 'ft1.1', etc
        has_output = bool(o or e)
        tid = (n == 0 and 'p' or 'f') + 't%s.%s' % (cid + 1, tid + 1)
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name
        tmpl = has_output and self.REPORT_TEST_WITH_OUTPUT_TMPL or self.REPORT_TEST_NO_OUTPUT_TMPL

        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(o, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # uo = unicode(o.encode('string_escape'))
            uo = o
        else:
            uo = o
        if isinstance(e, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # ue = unicode(e.encode('string_escape'))
            ue = e
        else:
            ue = e

        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            id=tid,
            output=saxutils.escape(uo + ue),
        )

        # 处理截图
        if getattr(t, 'images', []):
            # 判断截图列表，如果有则追加
            tmp = u""
            for i, img in enumerate(t.images):
                if i == 0:
                    tmp += """ <img src="data:image/jpg;base64,%s" style="display: block;" class="img"/>\n""" % img
                else:
                    tmp += """ <img src="data:image/jpg;base64,%s" style="display: none;" class="img"/>\n""" % img
            images = self.IMG_TMPL % dict(images=tmp)
        else:
            images = u"""无截图"""

        row = tmpl % dict(
            tid=tid,
            # Class = (n == 0 and 'hiddenRow' or 'none'),
            Class=(n == 0 and 'hiddenRow' or 'text text-success'),
            # style = n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'none'),
            style=n == 2 and 'text text-warning' or (n == 1 and 'text text-danger' or 'text text-success'),
            desc=desc,
            script=script,
            status=self.STATUS[n],
            img=images,
        )
        rows.append(row)
        if not has_output:
            return

    def _generate_ending(self):
        return self.ENDING_TMPL


class TestProgram(TestProgram):
    """
    A variation of the unittest.TestProgram. Please refer to the base
    class for command line parameters.
    """

    def runTests(self):
        # Pick HtmlTestRunner as the default test runner.
        # base class's testRunner parameter is not useful because it means
        # we have to instantiate HtmlTestRunner before we know self.verbosity.
        if self.testRunner is None:
            self.testRunner = TestRunner(verbosity=self.verbosity)
        TestProgram.runTests(self)


class TestSuite(TestSuite):

    def run(self, result, debug=False):
        topLevel = False
        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True

        for index, test in enumerate(self):
            if result.shouldStop:
                break

            if not debug:
                test(result)
            else:
                test.debug()

            if self._cleanup:
                self._removeTestAtIndex(index)

        if topLevel:
            self._tearDownPreviousClass(None, result)
            self._handleModuleTearDown(result)
            result._testRunEntered = False
        return result

    def add_test(self, test):
        """
        添加单个测试
        :param test: 测试用例的类实例化的对象
        :return:
        """
        self.addTest(test)

    def add_tests(self, tests):
        """
        添加多个测试
        :param tests:
        :return:
        """
        self.addTests(tests)


main = TestProgram

if __name__ == "__main__":
    main(module=None)
