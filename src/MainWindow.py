# -*- coding:utf-8 -*-

"""
 导表工具GUI界面
@author： 覃贵锋
@date： 2020-02-17
"""

from PyQt4.Qt import *

import os
import json
import uuid
import time
import random

import Utils
import Language
import BackService

from Config import Config




class ExportToolGUI(QMainWindow):
    """
    GUI 主界面
    """
    def __init__(self):
        """"""
        super(ExportToolGUI, self).__init__()
        # 设置标题
        self.setWindowTitle(Language.TITLE)
        # 设置窗口大小
        self.setMinimumSize(*Language.SIZE_DEFAULT)
        # 加入样式
        self.setStyleSheet(Language.PYQT_QSS)
        # 加载数据
        if self.load_local_config():
            # 初始化布局
            self.init_componets()
        
    def init_componets(self):
        """
        初始化控件
        """
        self.create_sys_menu()
        self.mContent = ExportMainPanel(self)
        self.setCentralWidget(self.mContent)
        # 注册回调事件
        service = BackService.get_service()
        service.callback.connect(self.event_service_callback)

    def load_local_config(self):
        """
        加载本地配置
        """
        if not os.path.exists(Config.LOCAL_PATH):
            QMessageBox.critical(self, Language.MSG_TITLE, Language.MSG_LOCALPATH_MISS)
            return False
        try:
            with open(Config.LOCAL_PATH) as pf:
                config = json.load(pf)
                if not Config.serialize(config):
                    raise ValueError,"config error"
        except Exception as e:
            print(e)
            QMessageBox.critical(self, Language.MSG_TITLE, Language.MSG_LOCALPATH_ERROR)
            return False
        return True


    def create_sys_menu(self):
        """
        创建菜单
        """
        _memuBar = QMenuBar(self)

        # 测试菜单
        toolMenu = _memuBar.addMenu(Language.MENU_TOOL)
        #
        settingAct = QAction(Language.MENU_TOOL_SETTING, self)
        settingAct.triggered.connect(self.event_menu_localsetting)
        toolMenu.addAction(settingAct)

        exitAct = QAction(Language.MENU_EXIT, self)
        exitAct.triggered.connect(self.event_menu_exit)
        toolMenu.addAction(exitAct)

        self.setMenuBar(_memuBar)

    def event_service_callback(self, task):
        """ """
        if task.signal() == "excel_list_files":
            if task.error():
                return QMessageBox.critical(self, Language.MSG_TITLE, Language.MSG_SVNPATH_UPERROR)
            filelist = task.get_result()
            self.mContent.update_file_list(filelist)

    def event_menu_localsetting(self):
        """
        菜单打开配置列表
        """
        # 如果为True表示需要重新刷新数据
        if SettingDialog.show(self):
            self.mContent.async_search_files(True)

    def event_menu_exit(self):
        """
        菜单点击退出
        """
        self.close()

class SettingDialog(QDialog):
    """
    配置设置界面
    """
    def __init__(self, parent=None):
        """ """
        super(SettingDialog, self).__init__(parent)
        self.setWindowTitle(Language.TITLE_LOCAL_SETTING)
        self.setMinimumSize(*Language.SIZE_SETTING_DIALOG)
        self.setStyleSheet(Language.PYQT_QSS)
        self.mIsChange = False
        self.init_componets()

    def init_componets(self):
        """
        初始化GUI界面布局
        """
        # 总体布局分上下层
        vLayout = QGridLayout()
        # 第一行：数据表路径
        vLayout.addWidget(QLabel(Language.LABEL_EXCEL_PATH), 0, 0)
        # 输入路径
        self.mExcelPathInput = QLineEdit()
        self.mExcelPathInput.setText(Config.InConfig['path'])
        vLayout.addWidget(self.mExcelPathInput,0,1,1,5)
        # 预览目录选择按钮
        excelPathPreviewButton = QPushButton(Language.BTN_PREVIEW)
        excelPathPreviewButton.clicked.connect(self.event_btn_excel_path)
        vLayout.addWidget(excelPathPreviewButton,0,6)
        # 第二行：数据表路径的属性配置
        vLayout.addWidget(QLabel(Language.LABEL_FILE_FILTER), 1, 0)
        # 过滤方法
        self.mFileFilterInput = QLineEdit()
        self.mFileFilterInput.setText(u",".join(Config.InConfig['filter']))
        self.mFileFilterInput.setPlaceholderText(Language.MSG_FILEFILTER_HOLD)
        vLayout.addWidget(self.mFileFilterInput,1, 1, 1, 3)
        # svn相关设置
        self.mUsingSVN = QCheckBox(Language.LABEL_USING_SVN)
        self.mUsingSVN.setChecked(Config.InConfig['svn'])
        vLayout.addWidget(self.mUsingSVN, 1, 4)
        vLayout.addWidget(QLabel(Language.LABEL_SVN_ACCOUNT), 1, 5)
        self.mSVNAccountInput = QLineEdit()
        self.mSVNAccountInput.setText(Config.InConfig['svn_account'])
        vLayout.addWidget(self.mSVNAccountInput, 1, 6, 1, 1)
        # 最好一行保存
        save_config_button = QPushButton(Language.BTN_SAVESETTING)
        save_config_button.clicked.connect(self.event_btn_save)
        vLayout.addWidget(save_config_button, 2, 6)
        #导出路径设置
        self.setLayout(vLayout)

    def event_btn_excel_path(self):
        """
        选择excel路径
        """
        dirPath = QFileDialog.getExistingDirectory(self, Language.LABEL_EXCEL_PATH, "./")
        self.mExcelPathInput.setText(dirPath)

    def event_btn_save(self):
        """
        保存配置
        """
        path = Utils.ufromQString(self.mExcelPathInput.text())
        if not path or len(path) <= 0:
            return 
        # 检查路径是否合法
        if not os.path.exists(path) or not os.path.isdir(path):
            return 
        Config.InConfig['path'] = path
        Config.InConfig['filter'] = Utils.ufromQString(self.mFileFilterInput.text()).split(",")
        Config.InConfig['svn'] = self.mUsingSVN.isChecked()
        Config.InConfig['svn_account'] = Utils.ufromQString(self.mSVNAccountInput.text())
        Config.save_to_file()
        self.mIsChange = True
        self.close()

    @staticmethod
    def show(parent):
        """
        静态方法打开设置界面
        """
        settingDialog = SettingDialog(parent)
        settingDialog.exec_()
        return settingDialog.mIsChange

class ConfirmDialog(QDialog):
    """
    输入确认框，用于提供输入内容，并获取输入的内容
    ConfirmDialog.show(parent, title, "提示内容", "默认输入内容")
    返回值为 输入的内容
    """
    def __init__(self, title,parent=None, **kwargs):
        """ """
        super(ConfirmDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(*Language.SIZE_INPUT_DIALOG)
        self.setStyleSheet(Language.PYQT_QSS)
        hLayout = QGridLayout()
        self.mInput = QLineEdit()
        self.mInput.setText(kwargs.get("dtext", u""))
        self.mInput.setPlaceholderText(kwargs.get("placehold", u""))
        hLayout.addWidget(self.mInput,0, 0, 1, 3)
        comfirm_button = QPushButton(Language.BTN_CONFIRM)
        comfirm_button.clicked.connect(self.event_btn_confirm)
        hLayout.addWidget(comfirm_button, 0, 3)
        self.setLayout(hLayout)
        self.mInputText = u""

    def event_btn_confirm(self):
        """点击确认按钮"""
        self.mInputText = Utils.fromQString(self.mInput.text())
        self.close()

    def get_input_value(self):
        """获取输入的数据"""
        return self.mInputText

    @staticmethod
    def show(parent, title, placehold=u"", default=u""):
        """
        显示输入提示框
        """
        dialog = ConfirmDialog(title, parent, placehold=placehold, dtext=default)
        dialog.exec_()
        return dialog.get_input_value()

class ExportMainPanel(QWidget):
    """
    导表主界面
    """
    list_update = pyqtSignal(str)
    def __init__(self, parent=None):
        """ """
        super(ExportMainPanel, self).__init__(parent)
        self.mExcelData = []
        self.mLastRefreshTime = 0
        self.init_componets()
        self.init_data()
        self.mTimer = QTimer()
        self.mTimer.setInterval(10000)
        self.mTimer.timeout.connect(self.event_time_update)
        self.mTimer.start()

    def init_componets(self):
        """
        初始化GUI界面布局
        """
        self.mVLayout = QVBoxLayout()

        # 搜索筛选界面
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(Language.LABEL_FILTER))
        
        self.mFilterInput = QLineEdit()
        self.mFilterInput.textChanged.connect(self.event_input_filter)
        filter_layout.addWidget(self.mFilterInput)

        self.mVLayout.addLayout(filter_layout)
        # 保存缓存界面
        cache_layout = QHBoxLayout()
        cache_layout.addWidget(QLabel(Language.LABEL_SAVESELECTED))

        self.mFiletrCombox = QComboBox()
        cache_layout.addWidget(self.mFiletrCombox)
        select_keys = Config.LocalData.keys()
        select_keys.insert(0, u"无")
        self.mFiletrCombox.addItems(select_keys)
        self.mFiletrCombox.currentIndexChanged.connect(self.event_cbox_selectupdate)

        self.mSaveFilterButton = QPushButton(Language.BTN_SAVESELECTED)
        self.mSaveFilterButton.clicked.connect(self.event_btn_savefilter)
        cache_layout.addWidget(self.mSaveFilterButton)
        cache_layout.insertStretch(2)
        self.mRefreshButton = QPushButton(Language.BTN_REFRESH)
        self.mRefreshButton.clicked.connect(self.event_btn_refresh)
        cache_layout.addWidget(self.mRefreshButton)
        self.mVLayout.addLayout(cache_layout)

        # Excel列表展示界面
        excel_list_layout = QVBoxLayout()
        excel_list_layout.addWidget(QLabel(Language.LABEL_EXCEL_LIST))
        self.mExcelList = QListWidget()
        excel_list_layout.addWidget(self.mExcelList)
        self.mVLayout.addLayout(excel_list_layout)
        # 导表按钮区域
        operator_layout = QHBoxLayout()
        self.mSelectAllCheck = QCheckBox(Language.LABEL_SELECT_ALL)
        self.mSelectAllCheck.clicked.connect(self.event_cbox_selectall)
        operator_layout.addWidget(self.mSelectAllCheck)
        operator_layout.insertStretch(3)
        for export_btn_config in Config.OutConfig:
            export_btn = QPushButton(export_btn_config["export_btn"])
            export_btn.clicked.connect(self.event_btn_export)
            operator_layout.addWidget(export_btn)
        self.mVLayout.addLayout(operator_layout)

        self.setLayout(self.mVLayout)


    def init_data(self):
        """
        初始化数据
        """
        self.mExcelList.clear()
        self.event_time_update()

    def event_time_update(self):
        """
        定时更新文件信息
        """
        self.async_search_files()

    def async_search_files(self, isReset=False):
        """
        异步获取文件列表
        """
        if isReset:
            self.mExcelData = []
            self.mExcelList.clear()
        # 加个定时限制
        if not isReset and time.time() - self.mLastRefreshTime < 5:
            return
        self.mLastRefreshTime = time.time()

        service = BackService.get_service()
        # 异步调用获取文件列表
        if Config.InConfig["svn"]:
            service.exec_async(Utils.get_svn_files,"excel_list_files", Config.InConfig["path"], Config.InConfig["filter"])
        else:
            print("asdasdasdsadsa")
            service.exec_async(Utils.get_file_list,"excel_list_files", Config.InConfig["path"], Config.InConfig["filter"])

    def update_file_list(self, filelist):
        """
        更新文件数据
        """
        # 先更新数据
        for item in self.mExcelData:
            key = item.get_name()
            if key in filelist:
                item.init_item_data(filelist[key])
                del filelist[key]
        # 再添加数据 原理:如果mExcelData已经有数据，说明是后续的更新，那么只需要更新filelist里面的状态即可，否则有新增就添加
        for filepath, info in filelist.items():
            item = ExcelItemData(info)
            self.mExcelData.append(item)
        self.show_all_excel()

    def sort_excel_data(self):
        """
        """
        new_list = []
        # 写while循环就只需要一次就搞定
        for item in self.mExcelData:
            if item.is_checked():
                new_list.append(item)

        for item in self.mExcelData:
            if not item.is_checked():
                new_list.append(item)
        self.mExcelData = new_list

    def get_list_item(self, item_data):
        """
        获取item控件
        """
        item = QWidget()
        item.setObjectName(item_data.get_id())
        grid_layout = QGridLayout()

        excel_name = QCheckBox(item_data.get_name())
        excel_name.setObjectName("checkbox")
        excel_name.clicked.connect(self.event_cbox_change)
        excel_name.setChecked(item_data.is_checked())
        excel_state = QLabel(item_data.get_state())

        if Config.InConfig['svn']:
            if not item_data.is_locked():
                excel_lock_btn = QPushButton(Language.BTN_LOCK)
            else:
                lock_account = item_data.lock_account()
                if lock_account == Config.InConfig["svn_account"]:
                    excel_lock_btn = QPushButton(Language.BTN_UNLOCK)
                else:
                    excel_lock_btn = QPushButton(Language.BTN_LOCK_BY.format(lock_account))
                    excel_lock_btn.setEnabled(False)
        else:
            excel_lock_btn = QPushButton(Language.BTN_SVN_SUPPORT)
            excel_lock_btn.setEnabled(False)

        excel_lock_btn.setObjectName("btn_lock")
        excel_explorer_btn = QPushButton(Language.BTN_EXPLORER)
        excel_explorer_btn.setObjectName("btn_explorer")
        # 事件用同一个监听，根据self.sender() 判断是谁
        excel_lock_btn.clicked.connect(self.event_list_btn_event)

        excel_explorer_btn.clicked.connect(self.event_list_btn_event)
        grid_layout.addWidget(excel_name, 0, 0, 1, 3)
        grid_layout.addWidget(excel_state, 0, 4, 1, 2)
        grid_layout.addWidget(excel_lock_btn, 0, 6)
        grid_layout.addWidget(excel_explorer_btn, 0, 7)

        item.setLayout(grid_layout)
        return item

    def event_cbox_change(self, *event):
        """
        checkbox 点击事件
        """
        # 遍历整个列表，重新刷新全部的选中状态，然后绘画整个列表
        # 另外可以使用self.sender()获取是哪个checkbox响应了，可通过objname进行数据交换
        for i in range(self.mExcelList.count()):
            item = self.mExcelList.item(i)
            widgets = self.mExcelList.itemWidget(item)
            checkbox = widgets.findChild(QCheckBox, "checkbox")
            for item_data in self.mExcelData:
                if item_data.is_this_item(Utils.fromQString(checkbox.text())):
                    item_data.set_checked(checkbox.isChecked())
        self.event_input_filter()

    def event_cbox_selectall(self, checked):
        """
        全选 
        """
        for i in range(self.mExcelList.count()):
            item = self.mExcelList.item(i)
            widgets = self.mExcelList.itemWidget(item)
            checkbox = widgets.findChild(QCheckBox, "checkbox")
            checkbox.setChecked(checked)
            uid = Utils.fromQString(widgets.objectName())
            for item_data in self.mExcelData:
                if item_data.is_this_id(uid):
                    item_data.set_checked(checked)

    def event_cbox_selectupdate(self, event):
        """
        快速选择列表更改
        """
        # 没有数据更改列表没有用
        if not self.mExcelData or self.mExcelList.count() <= 0:
            return
        if self.mFiletrCombox.currentIndex() == 0:
            self.show_all_excel()
        else:
            select_text = Utils.ufromQString(self.mFiletrCombox.currentText())
            data = Config.LocalData.get(select_text, None)
            if not data or not isinstance(data, list):
                return
            # 快速更新原始数据
            for item_data in self.mExcelData:
                if item_data.get_name() in data:
                    item_data.set_checked(True)
                else:
                    item_data.set_checked(False)
            self.show_all_excel()

    def event_list_btn_event(self, sender):
        """
        按钮响应事件（包括锁表和打开目录）
        """
        btn_obj = self.sender()
        objectName = Utils.fromQString(btn_obj.objectName())
        itemWidget = btn_obj.parentWidget()
        uid = Utils.fromQString(itemWidget.objectName())
        item_data = None
        for item in self.mExcelData:
            if item.is_this_id(uid):
                item_data = item
                break
        if not item_data:
            return
        update_flag = False
        if objectName == "btn_lock":
            label = Utils.ufromQString(btn_obj.text())
            if label == Language.BTN_LOCK:
                res, account = Utils.lock_file(Config.InConfig["path"],item.get_name())
                if res:
                    item.set_locked(account)
                    update_flag = True
            elif label == Language.BTN_UNLOCK:
                res = Utils.unlock_file(Config.InConfig["path"],item.get_name())
                if res:
                    item.set_locked("")
                    update_flag = True
            if update_flag:
                self.event_input_filter()
        elif objectName == "btn_explorer":
            Utils.open_file_dir(Config.InConfig["path"], item_data.get_name())

    def event_input_filter(self):
        """
        捕获输入消息
        """
        keywords = Utils.fromQString(self.mFilterInput.text())
        keywords_lst = keywords.strip().split(",")
        if keywords == "" or not keywords_lst:
            self.show_all_excel()
            return
        # 搜索部分
        self.show_part_excel(keywords_lst)

    def show_all_excel(self):
        """
        显示全部excel
        """
        #是否需要过滤
        need_filter = self.mFiletrCombox.currentIndex() != 0
        self.mExcelList.clear()
        # 优先排
        self.sort_excel_data()
        for item_data in self.mExcelData:
            if need_filter and not item_data.is_checked():
                continue
            item = QListWidgetItem()
            item_w = self.get_list_item(item_data)
            item.setSizeHint(item_w.sizeHint())
            self.mExcelList.addItem(item)
            self.mExcelList.setItemWidget(item, item_w)

    def show_part_excel(self, keywords_lst):
        """
        显示部分匹配关键字的excel
        """
        self.mExcelList.clear()
        self.sort_excel_data()
        for item_data in self.mExcelData:
            if item_data.is_checked() or item_data.contain_keys(keywords_lst):
                item = QListWidgetItem()
                item_w = self.get_list_item(item_data)
                item.setSizeHint(item_w.sizeHint())
                self.mExcelList.addItem(item)
                self.mExcelList.setItemWidget(item, item_w)

    def event_btn_export(self):
        """
        导表按钮-开始导表
        """
        btn_obj = self.sender()
        for i in range(self.mExcelList.count()):
            item = self.mExcelList.item(i)
            widgets = self.mExcelList.itemWidget(item)
            checkbox = widgets.findChild(QCheckBox, "checkbox")
            uid = Utils.fromQString(widgets.objectName())
            for item_data in self.mExcelData:
                if item_data.is_this_id(uid) and item_data.is_checked():
                    print(item_data)

    def event_btn_savefilter(self):
        """
        选择保存
        """
        text = ConfirmDialog.show(self, Language.TITLE_INPUT_SELECTED, Language.MSG_SELECTED_HOLD)
        if not text or len(text) <= 0:
            return 
        save_file_list = []
        for i in range(self.mExcelList.count()):
            item = self.mExcelList.item(i)
            widgets = self.mExcelList.itemWidget(item)
            checkbox = widgets.findChild(QCheckBox, "checkbox")
            uid = Utils.fromQString(widgets.objectName())
            for item_data in self.mExcelData:
                if item_data.is_this_id(uid) and item_data.is_checked():
                    save_file_list.append(item_data.get_name())
        Config.LocalData[text] = save_file_list
        Config.save_to_file()

    def event_btn_refresh(self):
        """ 刷新 """
        self.event_time_update()

class ExcelItemData(QWidget):
    """
    Excel 每行数据的Item界面
    包含：
       1、表名
       2、状态
       3、操作按钮
    """
    
    def __init__(self, fileitem):
        """ """
        super(ExcelItemData, self).__init__()
        #保存一个转换编码的文件列表
        self.mStates  = u""
        self.mLocked = u""
        self.mFileName = ""
        self.mRawFileName = u""
        self.mChecked = False
        self.mID = str(uuid.uuid4())
        self.init_item_data(fileitem)

    def init_item_data(self, fileitem):
        """
        """
        if isinstance(fileitem, unicode):
            self.mFileName = Utils.fromUnicode(fileitem)
            self.mRawFileName = fileitem
        elif isinstance(fileitem, dict):
            self.mFileName = Utils.fromUnicode(fileitem["filename"])
            self.mRawFileName = fileitem["filename"]
            self.mStates  = fileitem["status"]
            self.mLocked = fileitem["lock"]

    def get_id(self):
        """
        """
        return self.mID

    def is_this_id(self, uid):
        """ """
        return self.mID == uid

    def get_name(self):
        """
        """
        return self.mRawFileName

    def get_state(self):
        """
        """
        return self.mStates

    def is_locked(self):
        """
        """
        return len(self.mLocked) > 0

    def lock_account(self):
        """
        """
        return self.mLocked

    def set_checked(self, b):
        """
        """
        self.mChecked = b

    def set_locked(self, account):
        """ """
        self.mLocked = account

    def is_this_item(self, filename):
        """
        """
        return self.mFileName == filename

    def contain_key(self, keyword):
        """
        判断filename是否包含指定的关键字
        """
        if self.mFileName.find(keyword)>=0:
            return True
        return False

    def contain_keys(self, keywords):
        """
        判断filename是否在关键字列表中
        """
        for keyword in keywords:
            if keyword != '' and self.contain_key(keyword):
                return True
        return False

    def is_checked(self):
        """
        判断是否已经选中-- 选中的文件不参与筛选，始终显示在最前面
        """
        return self.mChecked

    def event_cbox_change(self):
        """
        勾选事件触发
        """
        self.mChecked = self.mExcelName.isChecked()
        #ExportMainPanel.list_update.emit(self.mFileName)