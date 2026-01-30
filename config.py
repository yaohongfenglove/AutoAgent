"""
项目配置模块
集中管理项目路径和配置
"""

from pathlib import Path


# 项目根目录
PROJECT_ROOT: Path = Path(__file__).parent


__all__ = ["PROJECT_ROOT"]
