import os,sys,re
import time

from remote import remote_config
from until import logger
from until.paramiko_util import LinuxClient
local_dir = remote_config.MODEL_DIR.replace('\\', '/')
logger.info("\033[35m model path=%s \033[0m" % local_dir)

if not local_dir.endswith('/'):
    local_dir += '/'

model_name = local_dir.split('/')[-2]
logger.info("\033[35m model_dir_name=%s\033[0m" % model_name)

if remote_config.USER == 'root':  # 文件夹会被自动创建，无需用户创建。
    remote_dir = '/pycodes/%s/' % model_name
else:
    remote_dir = '/home/%s/pycodes/%s/' % (remote_config.USER, model_name)


class RemoteRunner(object):
    def __init__(self, pty=False):
        self.pty = pty
        self.client = None

    def _init_model_dir(self):
        logger.info("start init_model_dir.............................................")
        self.client = LinuxClient(host=remote_config.HOST,
                                  port=remote_config.PORT,
                                  user=remote_config.USER,
                                  password=remote_config.PASSWORD,
                                  local_dir=local_dir,
                                  remote_dir=remote_dir,
                                  path_exclude=remote_config.PATH_EXCLUDE,
                                  suffix_exclude=remote_config.SUFFIX_EXCLUDE,
                                  last_modify_time=remote_config.LAST_MODIFY_TIME,
                                  size_limit=remote_config.SIZE_LIMIT)
        # logger.info()

        self.client.upload()
        logger.info("init_model_dir success.")

    def run(self):
        if os.name == 'posix':
            """
            此处十分重要
            当在idea运行的时候，会进行两个步骤1. upload代码到linux 2. ssh远程到linux并执行代码，并获取执行日志。
            当os.name=posix的时候表示此时运行在linux则跳过以下代码，此时执行的是脚本本身的代码
            """
            return
        self._init_model_dir()
        # 获取栈定调用链的 文件, 也就是我们运行的文件名
        local_script_name = sys._getframe(1).f_code.co_filename.replace('\\', '/')  # noqa
        remote_script_name = re.sub(f'^{local_dir}', remote_dir, local_script_name)
        process_mark = f'auto_remote_run_mark__{remote_script_name.replace("/", "__")[:-3]}'
        kill_cmd = f'''ps -aux|grep {process_mark}|grep -v grep|awk '{{print $2}}' |xargs kill -9'''
        logger.info('%s kill %s 标识的进程' % (kill_cmd, process_mark))
        logger.info("\033[33m kill_cmd=%s\033[0m" % kill_cmd)
        self.client.exec_cmd(kill_cmd)
        run_cmd = f'''export PYTHONPATH=%s:$PYTHONPATH;%s %s %s''' % (remote_dir, remote_config.PYTHON_INTERPRETER, remote_script_name, process_mark)
        logger.info("\033[33m run_cmd=%s \033 [0m" % run_cmd)
        run_log = self.client.exec_cmd(run_cmd)
        time.sleep(4)
        logger.info("\033[32m 远程日志=%s \033[0m" % run_log)
        logger.info("\033[32m 远程日志打印结束\033[0m")
        # 以下语句可避免window执行
        sys.exit(0)
