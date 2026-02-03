# -*- coding: utf-8 -*-
"""
颜色检测模块
基于 OpenCV + HSV 颜色空间的传统图像处理方法
"""
import os
import tempfile
from typing import List, Dict

import cv2
import numpy as np
import requests
from PIL import Image

from utils.logger import logger


# 颜色阈值常量（HSV 颜色空间）
# H (Hue 色调): 0-180, S (Saturation 饱和度): 0-255, V (Value 明度): 0-255
COLOR_THRESHOLDS = {
    "dark_black": {
        "hsv_ranges": [{"h": (0, 180), "s": (0, 35), "v": (0, 45)}],
        "min_pixel_ratio": 0.60,
        "description": "深黑色"
    },
    "deep_red": {
        "hsv_ranges": [
            {"h": (0, 10), "s": (127, 255), "v": (76, 204)},
            {"h": (170, 180), "s": (127, 255), "v": (76, 204)}
        ],
        "min_pixel_ratio": 0.25,
        "description": "深红色"
    },
    "deep_blue": {
        "hsv_ranges": [
            {"h": (100, 130), "s": (127, 255), "v": (76, 204)}
        ],
        "min_pixel_ratio": 0.25,
        "description": "深蓝色"
    },
    "light_green": {
        "hsv_ranges": [
            {"h": (35, 85), "s": (50, 200), "v": (150, 255)}
        ],
        "min_pixel_ratio": 0.25,
        "description": "浅绿色"
    },
    "light_gray": {
        "hsv_ranges": [
            {"h": (0, 180), "s": (0, 50), "v": (150, 220)}
        ],
        "min_pixel_ratio": 0.30,
        "description": "浅灰色"
    },
    "white": {
        "hsv_ranges": [
            {"h": (0, 180), "s": (0, 30), "v": (220, 255)}
        ],
        "min_pixel_ratio": 0.40,
        "description": "白色"
    },
    "beige": {
        "hsv_ranges": [
            {"h": (10, 30), "s": (30, 120), "v": (180, 255)}
        ],
        "min_pixel_ratio": 0.30,
        "description": "米色"
    },
}


class ColorDetector:
    """基于 HSV 颜色空间的颜色检测器"""

    def __init__(self, crop_ratio: float = None):
        """
        初始化颜色检测器

        Args:
            crop_ratio: 边缘裁剪比例，None 则从环境变量读取（默认 0.2）
        """
        self.color_thresholds = COLOR_THRESHOLDS
        if crop_ratio is None:
            crop_ratio = float(os.getenv("COLOR_CROP_RATIO", "0.2"))
        self.crop_ratio = crop_ratio

    def download_image(self, image_url: str) -> str:
        """
        下载图片到临时文件

        Args:
            image_url: 图片 URL

        Returns:
            临时文件路径
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(response.content)
            temp_file.close()

            return temp_file.name
        except Exception as e:
            logger.error(f"[X] 下载图片失败 {image_url}: {str(e)}")
            raise ValueError(f"下载图片失败: {str(e)}")

    def detect_color(self, image_url: str, color_name: str, crop_ratio: float = None) -> bool:
        """
        检测图片中是否包含指定颜色

        Args:
            image_url: 图片 URL
            color_name: 颜色名称（需要在 COLOR_THRESHOLDS 中定义）
            crop_ratio: 边缘裁剪比例，None 则使用初始化时的值

        Returns:
            是否匹配该颜色
        """
        # 检查颜色是否在支持列表中
        if color_name not in self.color_thresholds:
            logger.warning(f"[!] 不支持的颜色: {color_name}")
            return False

        color_config = self.color_thresholds[color_name]
        hsv_ranges = color_config["hsv_ranges"]
        min_pixel_ratio = color_config["min_pixel_ratio"]

        # 使用传入的 crop_ratio 或默认值
        if crop_ratio is None:
            crop_ratio = self.crop_ratio

        try:
            # 下载图片
            temp_path = self.download_image(image_url)

            # 读取图片
            image = cv2.imread(temp_path)
            if image is None:
                logger.error(f"[X] 读取图片失败: {temp_path}")
                return False

            # 边缘裁剪（去除边框影响）
            if crop_ratio > 0:
                h, w = image.shape[:2]
                crop_h = int(h * crop_ratio)
                crop_w = int(w * crop_ratio)
                image = image[crop_h:h-crop_h, crop_w:w-crop_w]

            # 转换为 HSV 颜色空间
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # 创建掩码（多个 HSV 范围的并集）
            mask = np.zeros((hsv_image.shape[0], hsv_image.shape[1]), dtype=np.uint8)
            for hsv_range in hsv_ranges:
                h_range = hsv_range["h"]
                s_range = hsv_range["s"]
                v_range = hsv_range["v"]

                # 创建当前范围的掩码
                range_mask = cv2.inRange(
                    hsv_image,
                    np.array([h_range[0], s_range[0], v_range[0]]),
                    np.array([h_range[1], s_range[1], v_range[1]])
                )
                # 合并到总掩码
                mask = cv2.bitwise_or(mask, range_mask)

            # 计算匹配像素比例
            total_pixels = mask.shape[0] * mask.shape[1]
            matched_pixels = cv2.countNonZero(mask)
            pixel_ratio = matched_pixels / total_pixels

            # 判断是否达到阈值
            is_match = pixel_ratio >= min_pixel_ratio

            # 删除临时文件
            import os
            os.unlink(temp_path)

            if is_match:
                logger.info(f"[OK] 颜色检测 {color_name}: 匹配 (比例: {pixel_ratio:.2%}) {image_url}")
            else:
                logger.info(f"[OK] 颜色检测 {color_name}: 不匹配 (比例: {pixel_ratio:.2%}, 需要至少 {min_pixel_ratio:.2%}) {image_url}")

            return is_match

        except Exception as e:
            logger.error(f"[X] 颜色检测失败 {color_name}: {str(e)} {image_url}")
            return False

    def get_supported_colors(self) -> List[str]:
        """
        获取支持的颜色列表

        Returns:
            颜色名称列表
        """
        return list(self.color_thresholds.keys())

    def get_color_description(self, color_name: str) -> str:
        """
        获取颜色描述

        Args:
            color_name: 颜色名称

        Returns:
            颜色描述
        """
        if color_name in self.color_thresholds:
            return self.color_thresholds[color_name]["description"]
        return ""
