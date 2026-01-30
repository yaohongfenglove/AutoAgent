# -*- coding: utf-8 -*-
import json
import os
import traceback
from typing import Dict

from dotenv import load_dotenv
from langfuse.openai import OpenAI

from utils.constants import CLOTHING_ATTRIBUTES
from utils.logger import logger

# 加载环境变量
load_dotenv(override=True)


def analyze_clothing_image(image_url: str) -> Dict[str, bool]:
    """
    使用 OpenAI 分析衣服图片，判断多个特征

    Args:
        image_url: 图片url

    Returns: 衣服特征字典

    """

    # 构建分析提示词（动态渲染）
    questions_text = "\n".join([
        f"{i+1}. {attr['key']}: {attr['description']}"
        for i, attr in enumerate(CLOTHING_ATTRIBUTES)
    ])

    example_json = {
        attr['key']: attr['default'] if attr['key'] != 'is_long_sleeve' else True
        for attr in CLOTHING_ATTRIBUTES
    }
    # 修改示例值使其更有意义
    example_json["is_dark_black"] = True
    example_json["is_long_sleeve"] = True
    example_json["has_both_sides_pattern"] = True

    prompt = f"""请分析这张衣服图片，并回答以下问题。请以JSON格式返回结果，包含以下字段：

{questions_text}

每个字段都应该是布尔值（true/false）。

请只返回JSON，不要有其他说明文字。返回格式示例：
{json.dumps(example_json, indent=4, ensure_ascii=False)}"""

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL_NAME"),  # 使用支持视觉的模型
            messages=[  # type: ignore
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            },
                            "detail": "low"
                        },
                    ],
                }
            ],
            max_tokens=500,
        )

        result_text = response.choices[0].message.content.strip()

        # 移除可能的 markdown 代码块标记
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()

        result = json.loads(result_text)

        # 动态构建返回结果
        return {
            attr['key']: result.get(attr['key'], attr['default'])
            for attr in CLOTHING_ATTRIBUTES
        }

    except Exception as e:
        error_log = traceback.format_exc()
        logger.error(f"分析图片时出错: {error_log}")
        raise ValueError(error_log)


def main():
    image_url = "https://img.kwcdn.com/product/fmket/148f3c7d0775cd6f5bc4978a9583b02d.jpg"

    result = analyze_clothing_image(image_url)
    logger.info(f"分析结果：{image_url}: {result}")
    logger.info(f"大模型日志查看：{os.getenv('LANGFUSE_CLOUD_LOG')}")


if __name__ == "__main__":
    main()
