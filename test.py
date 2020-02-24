# -*- coding:utf-8 -*-
import os, re, traceback
import Utils
import subprocess
from subprocess import PIPE
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')
 
def getSvnInfo(path):
    try:
        # cur_path = os.getcwd()
        # os.chdir(path)
        # # 使用如下接口很方便的去获取SVN INFO相关信息
        # rt = os.popen('svn help').read()
        # os.chdir(cur_path)
        cmd = u"svn status -u {0} ".format(path)
        rt = os.popen(Utils.fromUnicode(cmd)).read()
    except Exception as e:
        print('str(Exception):', str(Exception))
        print('repr(e):', repr(e))
        print('traceback.format_exc(): %s' % traceback.format_exc())
 
    return rt

def external_command(cmd, success_code=0, do_combine=False,
                         return_binary=False, environment={}, wd=None):

        env = os.environ.copy()
        env.update(environment)
        decode_text = return_binary is False

        try:
            stdout = \
                subprocess.check_output(
                    cmd,
                    cwd=wd,
                    env=env,
                    stderr=subprocess.STDOUT,
                    universal_newlines=decode_text)
        except subprocess.CalledProcessError as cpe:
            stdout = cpe.output
            return_code = cpe.returncode
        else:
            return_code = 0

        if return_code != 0:
            print("return_code:", return_code)
            print(Utils.fromUnicode(stdout))

        if return_binary is True or do_combine is True:
            return stdout

        return stdout.strip('\n').split('\n')
 
 
if __name__ == '__main__':
    # b = getSvnInfo(u'D:/Project/GNS/Test/工具开发/ExportToolGUI')
    path = u'D:/Project/GNS/Test/工具开发/ExportToolGUI'
    print("",path.encode("utf8"))
    cmd = u"svn status {0} ".format(path)
    b = external_command(Utils.fromUnicode(cmd, "cp936"))
    print(type(b),b)
