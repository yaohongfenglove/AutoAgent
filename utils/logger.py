"""
日志组件 - 基于 loguru
"""

import os
import sys

from dotenv import load_dotenv
from loguru import logger

from config import PROJECT_ROOT


# 加载环境变量
load_dotenv(override=True)


def setup_logger():
    """
    配置并初始化日志记录器
    """
    # 移除默认的处理器
    logger.remove()

    # 从环境变量获取日志配置
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_retention = os.getenv("LOG_RETENTION", "31 days")
    env = os.getenv("DEPLOY_ENV", "dev").lower()

    # 创建日志目录
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    # 控制台输出 - 仅在开发环境启用
    if env == "dev":
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # noqa: E501
            level=log_level,
            colorize=True,
        )

    # 文件输出 - 所有日志（按日分割）
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="00:00",  # 每天午夜分割
        retention=log_retention,
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )

    # 文件输出 - 错误日志（按日分割）
    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00",  # 每天午夜分割
        retention=log_retention,
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )

    return logger


# 初始化日志记录器
setup_logger()


__all__ = ["logger"]
