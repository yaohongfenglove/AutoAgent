"""
常量定义模块
定义项目中使用的所有常量
"""


# 衣服属性定义：所有属性在此集中管理，修改时只需更新此处
CLOTHING_ATTRIBUTES = [
    {
        "key": "is_dark_black",
        "description": "衣服颜色是否为深黑色（纯黑或接近黑色）",
        "default": False
    },
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
