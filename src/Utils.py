# -*- coding:utf-8 -*-

"""
  通用接口模块
@author： 覃贵锋
@date： 2020-02-17
"""

import re
import os
import subprocess
from xml.dom.minidom import parseString



def fromQString(qstr, encoding='UTF-8'):
    """
    将QString 转 str
    :param qstr:
    :return:
    """
    try:
        return unicode(qstr).encode(encoding)
    except:
        return ""

def ufromQString(qstr,encoding='UTF-8'):
    """
    将QString 转 unicode
    """
    try:
        return fromQString(qstr, encoding).decode(encoding)
    except:
        return u""

def fromUnicode(ustr, encoding='UTF-8'):
    """
    将unicode字符 转 str
    """
    try:
        if isinstance(ustr, unicode):
            return ustr.encode(encoding)
        return str(ustr)
    except:
        return ustr

def file_extension(path, default):
    """
    获取文件的扩展名
    """
    data = os.path.splitext(path)
    if data and len(data) > 1:
        return data[1]
    return default

def get_file_list(path, ext=[".xls",".xlsx"], ignore_dir=[]):
    """
    从指定路径加载Excel列表
    :param path: 指定的路径
    :param ext: 文件后缀
    """
    files = {}
    for root, dirs, filelist in os.walk(path):
        for filename in filelist:
            file_ext = file_extension(filename, u"")
            if file_ext in ext:
                filepath = os.path.join(root, filename)
                relative_path = filepath.replace(path, "")
                if relative_path.startswith(u"/") or relative_path.startswith(u"\\"):
                    relative_path = relative_path[1:]
                files[relative_path] = relative_path
    return files

def get_svn_files(path, ext=[".xls",".xlsx"], ignore_dir=[]):
    """
    加载svn数据
    """
    files = {}
    for root, dirs, filelist in os.walk(path):
        for filename in filelist:
            file_ext = file_extension(filename, u"")
            if file_ext in ext:
                filepath = os.path.join(root, filename)
                relative_path = filepath.replace(path, "")
                if relative_path.startswith(u"/") or relative_path.startswith(u"\\"):
                    relative_path = relative_path[1:]
                fileitem  = {}
                fileitem["filename"] = relative_path
                fileitem['status'] = "normal"
                fileitem["lock"] = ""
                files[relative_path] = fileitem
    # 获取目录的svn文件状态信息
    files_status = get_svn_path_st(path)
    for filestatus in files_status:
        fileitem = files.get(filestatus['path'], None)
        if not fileitem:
            continue
        if "status" in filestatus:
            fileitem["status"] = filestatus["status"]
        if "lock" in filestatus:
            fileitem["lock"] = filestatus["lock"]
    return files

def get_svn_path_st(path):
    """
    获取SVN目录的文件状态
    """
    files_status = []
    # 执行cmd
    xml_data = external_command("svn st -u --xml", path)
    xml_tree = parseString(xml_data)
    root = xml_tree.getElementsByTagName("status")[0]
    for target in root.childNodes:
        for entry in target.childNodes:
            filestatus = {}
            filestatus["path"] = entry.getAttribute("path")
            wc_status = entry.getElementsByTagName("wc-status")
            if wc_status and len(wc_status) > 0:
                props = wc_status[0].getAttribute("props")
                item = wc_status[0].getAttribute("item")
                filestatus["status"] = item
            repos_status = entry.getElementsByTagName("repos-status")
            if not repos_status or len(repos_status) <= 0:
                continue
            locks = repos_status[0].getElementsByTagName("lock")
            if not locks and len(locks) <= 0:
                continue
            owner = locks[0].getElementsByTagName("owner")[0]
            filestatus["lock"] = owner.firstChild.data
            files_status.append(filestatus)
    return files_status

def lock_file(path,filename):
    """
    锁文件，返回锁定的状态和操作人
    ！！！注意：英文环境测试的，不知汉化的会不会有问题
    """
    cmd = u"svn lock {0} -m'aaa' ".format(filename)
    result = external_command(cmd, path)
    if not result or result.find("locked") < 0:
        return False, ""
    match_data = re.findall(r"'\w+'", result)
    if match_data and len(match_data) > 0:
        return True, match_data[0][1:-1]
    return False, ""

def unlock_file(path,filename):
    """
    解锁文件：  
    ！！！注意：英文环境测试的，不知汉化的会不会有问题
    """
    cmd = u"svn unlock {0}".format(filename)
    result = external_command(cmd, path)
    if result.find("unlocked") >=0:
        return True
    return False

# def execute_svn_cmd(cmd,path):
#     """
#     执行SVN命令----
#     ！！！备注:命令行界面可以svn xx 加路径，
#     但是到了py执行，必须cd到目录，执行 svn xx 不能加路径
#     !!!! 发现问题：这个难解，其实是可以加路径的，但是如果遇到了中文路径就凉了，
#     因此还是只能走上面的方法
#     """
#     cur_path = os.getcwd()
#     os.chdir(path) # 这步必须，且cmd里面不可加路径- 这会产生另一个限制svn必须添加环境变量
#     rt = None
#     try:
#         rt = os.popen(cmd).read().replace("\n","")
#     except Exception as e:
#         print("execute_svn_cmd",e)
#     os.chdir(cur_path) # 一定要回去，要不然后续的一些操作会很怪
#     return rt

def external_command(cmd, wd=None,success_code=0, environment={}):
    """
    执行命令
    """
    env = os.environ.copy()
    env.update(environment)
    try:
        if isinstance(cmd , unicode):
            cmd = fromUnicode(cmd, "cp936")
        if isinstance(wd, unicode):
            wd = fromUnicode(wd, "cp936")
        stdout = subprocess.check_output(cmd, cwd=wd, env=env, stderr=subprocess.STDOUT,universal_newlines=True)
    except subprocess.CalledProcessError as cpe:
        stdout = cpe.output
        return_code = cpe.returncode
    else:
        return_code = 0

    if return_code != 0:
        print("return_code:", return_code)
        print(fromUnicode(stdout))

    return stdout.replace('\n',"")


def open_file_dir(root,filename):
    """
    尽支持windows下快速定位到指定的目录
    :param root: 根路径
    :param filename: 文件路径
    """
    abs_path = os.path.dirname(os.path.join(root,filename))
    abs_path = abs_path.replace("/", "\\")
    cmd = fromUnicode(u"explorer " + abs_path, "cp936")
    os.popen(cmd)


if __name__ == '__main__':
    # print(get_svn_path_st(u"D:/Project/GNS/Test/工具开发/ExportToolGUI"))
    # print(unlock_file(u"D:/Project/GNS/Test/工具开发/ExportToolGUI",u"Utils.py"))
    # print(lock_file(u"D:/Project/GNS/Test/工具开发/ExportToolGUI",u"中文文件测试.txt"))
    print(unlock_file(u"D:/Project/GNS/Test/工具开发/ExportToolGUI",u"中文文件测试.txt"))
    # open_file_dir(u"D:/Project/GNS/Test/工具开发/ExportToolGUI","")
    # print external_command("svn status -u" , u"D:/Project/GNS/Test/工具开发/ExportToolGUI")