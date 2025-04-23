import logging
import logging.config
import os
from logging.handlers import TimedRotatingFileHandler

def init_logger():
    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 日志配置字典
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{asctime} - {name}:{funcName}:{lineno} - {levelname} - {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_dir, 'app.log'),  # 日志文件保存在 logs 目录下
                'when': 'midnight',  # 按天轮换日志
                'interval': 1,  # 每天轮换
                'backupCount': 7,  # 最多保留 7 天的日志
                'formatter': 'verbose',
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }

    # 配置日志系统
    logging.config.dictConfig(log_config)

    # 获取日志记录器
    logger = logging.getLogger(__name__)
    logger.info("====== 日志模块初始化完成 =======")

init_logger()