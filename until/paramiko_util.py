
import os
import re
import sys
import time
import traceback

from paramiko import SFTPClient
import paramiko

from until import logger


class LinuxClient():
    """
    paramiko实现的文件夹上传
    """

    def __init__(self,
                 host,
                 port,
                 user,
                 password,
                 local_dir: str,
                 remote_dir: str,
                 path_exclude=('/.git/', '/.idea/',),
                 suffix_exclude=('.pyc', '.log', '.gz'),
                 last_modify_time=3650 * 24 * 60 * 60,
                 size_limit=1000 * 1000
                 ):
        self.host = host
        self.port = port
        self._user = user
        self._password = password

        self._local_dir = str(local_dir).replace('\\', '/')
        if not self._local_dir.endswith('/'):
            self._local_dir += '/'
        self._remote_dir = str(remote_dir).replace('\\', '/')
        if not self._remote_dir.endswith('/'):
            self._remote_dir += '/'
        self.path_exclude = path_exclude
        self.suffix_exclude = suffix_exclude
        self.last_modify_time = last_modify_time
        self.size_limit = size_limit
        self.upload_file_count = 0
        self.filter_file_count = 0
        self.upload_file_size = 0
        self.filter_file_size = 0
        self.ssh=None
        self.sftp=None
        self._connect()

    def _connect(self):
        # 创建SSHClient实例对象

        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.host, port=self.port, username=self._user, password=self._password, compress=True)
            self.ssh = ssh
            self.sftp = SFTPClient.from_transport(self.ssh.get_transport())
        except Exception as e:
            logger.error("connect error")
            raise e

    def exec_cmd(self, cmds: str) -> str:
        logger.info("[ETL] [LinuxCMDClient]  exec cmd=%s" % cmds)
        stdin, stdout, stderr = self.ssh.exec_command(cmds)
        return "%s\n%s" % ( stdout.read().decode("utf-8").strip(), stderr.read().decode("utf-8").strip())

    def __del__(self):
        if self.sftp:
            logger.info("sftp close")
            self.sftp.close()
        if self.ssh:
            logger.info("ssh close")
            self.ssh.close()

    def _file_filter(self, file_path: str):
        # 文件后缀名(包含.)
        file_suffix = os.path.splitext(file_path)[1]
        if file_suffix in self.suffix_exclude:
            return True
        for p_e in self.path_exclude:
            if re.search(p_e, file_path):
                return True
        # 文件修改时间(单位s)
        st_mtime = os.stat(file_path).st_mtime
        # 文件大小(单位bit 比特)
        file_size = os.path.getsize(file_path)
        if time.time() - st_mtime > self.last_modify_time:
            return True
        if file_size > self.size_limit:
            return True
        return False

    def _make_dir(self, dirc, final_dir):
        """
        sftp.mkdir 不能直接越级创建深层级文件夹。
        :param dirc:
        :param final_dir:
        :desc 如果调用为：_make_dir('/a/b/c','/a/b/c')
            第一次递归创建 /a
            第一次递归创建 /a/b
            第一次递归创建 /a/b/c
        :return:
        """
        # print(dir,final_dir)
        try:
            self.sftp.mkdir(dirc)
            if dirc != final_dir:
                self._make_dir(final_dir, final_dir)
        except FileNotFoundError as e:
            parent_dir = os.path.dirname(dirc)
            self._make_dir(parent_dir, final_dir)

    def upload(self):
        for parent, dirnames, filenames in os.walk(self._local_dir):
            for filename in filenames:
                # 获取window文件 全路径
                local_file_path = os.path.join(parent, filename).replace('\\', '/')
                # 获取文件大小
                volume = os.path.getsize(local_file_path)
                if not self._file_filter(local_file_path):
                    # 根据本地文件路径  生成linux文件路径
                    # 从file_full_name找出_local_dir前缀替换为_remote_dir
                    remote_file_path = re.sub(f'^{self._local_dir}', self._remote_dir, local_file_path)
                    try:
                        # window到linux上传文件
                        self.sftp.put(local_file_path, remote_file_path)
                        logger.info("upload success local：%s -> remote：%s" % (local_file_path, remote_file_path))

                        self.upload_file_count += 1
                        self.upload_file_size += volume
                    except Exception as e:
                        if isinstance(e, FileNotFoundError):
                            self._make_dir(os.path.split(remote_file_path)[0], os.path.split(remote_file_path)[0])
                            self.sftp.put(local_file_path, remote_file_path)
                        else:
                            logger.error("upload error=%s" % traceback.format_exc())
                else:
                    logger.info('filter exclude %s' % local_file_path)
                    self.filter_file_count += 1
                    self.filter_file_size += volume
        logger.info(
            "\033[35m upload_count: {up_count} 个 , upload_size:  {up_size}M , file_filter_size:  {filter_count}个  ,  file_filter_size: {filter_size}M\033[0m"
            .format(up_count=self.upload_file_count,
                    up_size=round(self.upload_file_size / (1024 * 1024), 4),
                    filter_count=self.filter_file_count,
                    filter_size=self.filter_file_size / (1024 * 1024))
            )


if __name__ == '__main__':
    client = LinuxClient(host='ip',
                                      port=22,
                                      user='root',
                                      password='game123(*&',
                                      local_dir=sys.path[1],  # 表示当前代码文件所在的顶层model,在此model下的所有文件都会被上传到/home/pemggan 下
                                      remote_dir='/home/penggan/')
    client.upload()

