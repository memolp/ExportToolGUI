# -*- coding:utf-8 -*-

"""
  通用语言存放处，方便修改
@author： 覃贵锋
@date： 2020-02-17
"""

TITLE = u"导表工具"
TITLE_INPUT_SELECTED = u"输入名称"
TITLE_LOCAL_SETTING = u"配置设置"

SIZE_DEFAULT = (800,600)
SIZE_INPUT_DIALOG = (150, 50)
SIZE_SETTING_DIALOG = (400, 100)

MENU_TOOL = u"工具(&T)"
MENU_TOOL_SETTING = u"本地配置(&L)"
MENU_EXIT = u"退出(&E)"

MSG_TITLE = u"提示"
MSG_LOCALPATH_MISS = u"配置文件丢失"
MSG_LOCALPATH_ERROR = u"配置文件解析失败"
MSG_SVNPATH_UPERROR = u"目录更新失败"
MSG_SELECTED_HOLD = u"输入快速选择保存的名称" 
MSG_INPUT_INVALID = u"输入无效"
MSG_FILEFILTER_HOLD = u"文件后缀(如: .xls,.xlsx)"

LABEL_FILTER = u"筛选关键字:"
LABEL_EXCEL_LIST = u"Excel文件列表:"
LABEL_EXCEL_PATH = u"配置表路径:"
LABEL_SELECT_ALL = u"全选"
LABEL_SAVESELECTED = u"快速选择列表:"
LABEL_FILE_FILTER = u"文件过滤规则:"
LABEL_USING_SVN = u"是否为SVN目录"
LABEL_SVN_ACCOUNT = u"输入SVN账号:"

BTN_EXPORT_EXCEL = u"开始导表"
BTN_LOCK = u"锁表"
BTN_LOCK_BY = u"已被{0}锁定"
BTN_UNLOCK = u"解锁"
BTN_EXPLORER = u"打开目录"
BTN_SAVEFILTER = u"保存为筛选"
BTN_SAVESELECTED = u"保存为快速选择"
BTN_PREVIEW = u"预览"
BTN_CONFIRM = u"确定"
BTN_REFRESH = u"刷新"
BTN_SAVESETTING = u"保存配置"
BTN_SVN_SUPPORT = u"仅SVN支持"

PYQT_QSS = ""
def LoadQSS(path="style.qss"):
    """ """
    global PYQT_QSS
    with open(path, "r") as pf:
        PYQT_QSS = pf.read()
