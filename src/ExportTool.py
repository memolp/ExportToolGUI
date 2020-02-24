# -*-coding:utf-8-*-

"""
  导表工具GUI界面入口：
    1、快速定位Excel表（编号查询，表名查询）
    2、Excel表选择与取消（支持逐个选择，自定义规则选择即筛选，全选）
    3、支持界面对每个表进行锁表操作
        3.1、锁表需要关联SVN
        3.2、锁表需要知道是谁锁了
@author： 覃贵锋
@date： 2020-02-17
"""

import sys
import Language

from PyQt4.QtGui import QApplication

from MainWindow import ExportToolGUI



if __name__ == "__main__":
    Language.LoadQSS()
    app = QApplication([])
    frame = ExportToolGUI()
    frame.show()
    sys.exit(app.exec_())