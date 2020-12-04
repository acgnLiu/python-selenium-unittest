# from runner.ranzhi_runner import RanzhiRunner
from runner.runner import Runner


class main(object):
    """
    自动化测试方案的唯一执行入口
    """

    @staticmethod
    def running():
        """ 静态的执行方法,如果没有用 @staticmethod 需要 Main().run_ranzhi()
        :return:
        """
        print("start-test")
        Runner().run_test()

if __name__ == "__main__":
    main.running()
