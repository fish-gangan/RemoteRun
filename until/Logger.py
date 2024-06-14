# coding:utf-8
import os
import logging
import re
from logging.handlers import TimedRotatingFileHandler
import colorlog


DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(DIR, "../" "logs")
# 如果不存在日志文件夹，则新建一个
if not os.path.exists(LOG_PATH):
    print("LOG_PATH=%s" % LOG_PATH)
    os.mkdir(LOG_PATH)


class Logger:
    # 控制台输出不同级别日志颜色设置
    def __init__(self, logger_name=None, file_extra=None):
        """
        :param logger_name:logger 名称
        :param file_extra: 目录后缀
        :param over_write: 是否覆盖, 默认否
        日志格式为: 2023-08-01 21:22:34,343 [BokeApi] -  [CRITICAL]  output output output (Logger.py:110)
        """
        self.log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'black',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
        self.nocolor_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s ')
        self.color_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s: %(message)s', log_colors=self.log_colors_config)
        self.logger = logging.getLogger(logger_name)
        self.logger.handlers = []
        self.logger.setLevel(logging.DEBUG)  # 设置默认级别，必须设置，否则会导致info日志及其以下无法获取
        if file_extra:
            self.real_dir = os.path.join(LOG_PATH, file_extra)
        else:
            self.real_dir = LOG_PATH
        if not os.path.exists(self.real_dir):
            os.mkdir(self.real_dir)
        common_file_name = os.path.join(self.real_dir, 'info.log')
        error_file_name = os.path.join(self.real_dir, 'error.log')
        # 按天滚动, 最多保留三个月
        common_handler = TimedRotatingFileHandler(filename=common_file_name, when='D', interval=1, backupCount=90,
                                                  encoding="UTF-8")
        error_handler = TimedRotatingFileHandler(filename=error_file_name, when='D', interval=1, backupCount=90,
                                                 encoding="UTF-8")
        std_handler = logging.StreamHandler()
        # 设置文件日志后缀 用于日志自动侦测删除
        common_handler.suffix = "%Y-%m-%d.log"
        error_handler.suffix = "%Y-%m-%d.log"
        common_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        error_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        # 设置日志输出格式

        common_handler.setFormatter(self.nocolor_formatter)
        error_handler.setFormatter(self.nocolor_formatter)
        std_handler.setFormatter(self.color_formatter)
        # 设置日志级别【DEBUG < INFO < WARNING < ERROR < CRITICAL】

        common_handler.setLevel(logging.DEBUG)
        error_handler.setLevel(logging.ERROR)
        std_handler.setLevel(logging.DEBUG)
        # 为当前logger添加 日志处理器handler
        self.logger.addHandler(common_handler)
        self.logger.addHandler(std_handler)
        self.logger.addHandler(error_handler)

    def info(self, msg, *args, **kwargs):

        return self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self.logger.error(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        return self.logger.debug(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        return self.logger.critical(msg, *args, **kwargs)


class RemoteLogger:
    """
    对应一个app model, 注意修改file_extra, 这是子目录名称, 会拼接在基础目录中
    记录python alg核心代码的  日志类
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        单例意义: 每个Django 模块理论上只需要一个模块日志对象,
        """
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, name=None, file_extra=None):
        """
        判断是为了保证每一个app model 对象当且仅当拥有一个日志对象
        """
        if hasattr(self, 'logger') is False:
            self.logger = Logger(logger_name=name, file_extra=file_extra)

    def info(self, msg, *args, **kwargs):

        return self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self.logger.error(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        return self.logger.debug(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        return self.logger.critical(msg, *args, **kwargs)


if __name__ == '__main__':
    logger = RemoteLogger("[RemoteRun]", "remote")
    logger.info("cccc")
    # CoreLogger().logger.debug("debug debug debug debug debug")
    # CoreLogger().logger.info("info info info info info")
    # CoreLogger().logger.warning("warning warning warning")
    # CoreLogger().logger.error("error error error")
    # CoreLogger().logger.critical("error error error")
