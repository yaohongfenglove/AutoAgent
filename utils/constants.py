"""
常量定义模块
定义项目中使用的所有常量
"""
from os import getenv


# ================================
# 颜色检测配置
# ================================

# 从环境变量读取要检测的颜色（单个）
FILTER_COLOR = getenv("FILTER_COLOR", "").strip()

# 颜色描述映射
COLOR_DESCRIPTIONS = {
    "dark_black": "衣服颜色是否为深黑色（纯黑或接近黑色）",
    "deep_red": "衣服颜色是否为深红色",
    "deep_blue": "衣服颜色是否为深蓝色",
    "light_green": "衣服颜色是否为浅绿色",
    "light_gray": "衣服颜色是否为浅灰色",
    "white": "衣服颜色是否为白色",
    "beige": "衣服颜色是否为米色"
}


# ================================
# 动态生成颜色属性
# ================================

def _generate_color_attribute():
    """
    根据 FILTER_COLOR 环境变量动态生成颜色属性

    Returns:
        颜色属性列表（0 或 1 个元素）
    """
    if not FILTER_COLOR:
        return []

    # 获取颜色描述，如果没有定义则使用默认描述
    description = COLOR_DESCRIPTIONS.get(
        FILTER_COLOR,
        f"衣服颜色是否为{FILTER_COLOR}"
    )

    return [{
        "key": f"is_{FILTER_COLOR}",
        "description": description,
        "default": False
    }]


# ================================
# 衣服属性定义
# ================================

# 基础属性（非颜色属性）
BASE_CLOTHING_ATTRIBUTES = [
    {
        "key": "has_cotton_text",
        "description": "图片上是否含有\"cotton\", \"cot\"字眼的单词",
        "default": False
    },
    {
        "key": "is_long_sleeve",
        "description": "是否为长袖（袖子长度到手腕或接近手腕）",
        "default": False
    },
    {
        "key": "is_round_neck",
        "description": "领口是圆领（而不是V领、翻领、立领等）",
        "default": False
    },
    {
        "key": "pattern_covered",
        "description": "衣服上的图案是否被遮盖（无法完整看到，比如被手、头发遮挡）",
        "default": False
    },
    {
        "key": "has_both_sides_pattern",
        "description": "衣服正面和背面是否都有图案（如果只能看到一面，判定为False）",
        "default": False
    },
]

# 最终属性列表：颜色属性 + 基础属性
CLOTHING_ATTRIBUTES = _generate_color_attribute() + BASE_CLOTHING_ATTRIBUTES
