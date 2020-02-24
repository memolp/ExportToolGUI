# -*- coding:utf-8 -*-

"""
class BackService:
    后台服务类，用于异步在后台处理逻辑，防止阻塞UI界面和定时刷新等
@author： 覃贵锋
@date： 2020-02-19
"""

from PyQt4.Qt import *

import Queue


class CallTask(object):
    """
    执行任务
    """
    def __init__(self, fn, signal, *args):
        """ """
        self.mFunction = fn
        self.mSignal = signal
        self.mArgs = args
        self.mIsDone = False
        self.mIsError = False

    def run(self):
        """ """
        try:
            self.mResult = self.mFunction(*self.mArgs)
        except Exception as e:
            print(e)
            self.mResult = e
            self.mIsError = True
        self.mIsDone = True

    def done(self):
        """ """
        return self.mIsDone

    def error(self):
        """ """
        return self.mIsError

    def signal(self):
        """ """
        return self.mSignal

    def get_result(self):
        """ """
        return self.mResult


class BackService(QThread):
    """ 
    """
    callback = pyqtSignal(object)

    Instance = None
    def __init__(self):
        """ """
        super(BackService, self).__init__()

        self.mThreadRun = False
        # 线程更新间隔
        self.mInterval = 1
        self.mExecQueue = Queue.Queue()
        self.start()

    def stop_thread(self):
        """
        """
        self.mThreadRun = False

    def exec_async(self, callback, signal, *args):
        """
        异步执行方法，与UI交互
        :param callback: 执行的方法
        :param signal: 返回事件信号
        :param args: 执行方法的传参数列表
        :return 返回True表示成功执行中
        """
        try:
            task = CallTask(callback, signal, *args)
            self.mExecQueue.put(task)
            return task
        except Exception as e:
            print(e)
            return None

    def run(self):
        """
        """
        self.mThreadRun = True
        while self.mThreadRun:
            try:
                task = self.mExecQueue.get(block=True)
                task.run()
                self.callback.emit(task)
            except:
                pass
            self.sleep(self.mInterval)

def get_service():
    """ """
    if BackService.Instance is None:
        BackService.Instance = BackService()
    return BackService.Instance