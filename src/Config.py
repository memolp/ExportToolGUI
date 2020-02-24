# -*- coding:utf-8 -*-

"""
  相关配置存放处，包括导表路径相关
@author： 覃贵锋
@date： 2020-02-17
"""

import os
import json

class Config:
    """
    配置文件类，用于解析生成配置
    """
    LOCAL_PATH = "config.json"
    InConfig = {}
    OutConfig = []
    LocalData = {}
    @staticmethod
    def serialize(config):
        """ 序列化数据 """
        if not isinstance(config, dict):
            print("serialize config format error!!!")
            return False
        if not Config.serialize_in(config.get("in", None)):
            print("serialize_in config error !!!")
            return False
        if not Config.serialize_out(config.get("export", None)):
            print("serialize_out config error !!!")
            return False
        if not Config.serialize_local(config.get("local", None)):
            print("serialize_local config error !!!")
            return False
        return True

    @staticmethod
    def serialize_in(config):
        """ 检查输入配置 """
        if not isinstance(config, dict):
            return False
        Config.InConfig = {}
        path = config.get("path","")
        # #　检查路径是否配置
        # if not path or path == "":
        #     return False
        # # 检查路径是否合法
        # if not os.path.exists(path) or not os.path.isdir(path):
        #     return False
        Config.InConfig["path"] = path
        Config.InConfig["svn"] = config.get("svn", False)
        Config.InConfig["svn_account"] = config.get("svn_account", "")
        # 文件过滤配置
        filter_data = config.get("filter",None)
        if not isinstance(filter_data, list):
            return False
        Config.InConfig["filter"] = filter_data
        return True

    @staticmethod
    def serialize_out(config):
        """检查输出配置 """
        #　安全检查
        if not isinstance(config, list):
            return False
        Config.OutConfig = []
        # 遍历配置
        for conf in config:
            if not isinstance(conf, dict):
                continue
            export_btn_name = conf.get("export_btn",None)
            if not export_btn_name or export_btn_name == "":
                continue
            export_data = conf.get("export_data", None)
            if export_data is None:
                continue
            Config.OutConfig.append({"export_btn":export_btn_name,"export_data":export_data})
        if len(Config.OutConfig) <= 0:
            return False
        return True

    @staticmethod
    def serialize_local(config):
        """ 检查本地存储 """
        if not isinstance(config, dict):
            return False
        Config.LocalData = config
        return True

    @staticmethod
    def save_to_file():
        """ """
        save_data = {}
        save_data["in"] = Config.InConfig
        save_data["export"] = Config.OutConfig
        save_data["local"] = Config.LocalData
        with open(Config.LOCAL_PATH, "w") as pf:
            json.dump(save_data, pf, indent=4)
        print("save_to_file end")