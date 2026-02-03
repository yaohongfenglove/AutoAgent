# -*- coding: utf-8 -*-
import csv
import json
import os
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict

from dotenv import load_dotenv
from langfuse.openai import OpenAI

from config import PROJECT_ROOT
from utils.color_detector import ColorDetector
from utils.constants import CLOTHING_ATTRIBUTES, FILTER_COLOR
from utils.logger import logger


# 加载环境变量
load_dotenv(override=True)


def analyze_clothing_image(image_url: str) -> Dict[str, str]:
    """
    使用 OpenAI 分析衣服图片，判断多个特征
    颜色检测根据配置选择方法（OpenCV 或大模型），其他属性使用 GPT-4o

    Args:
        image_url: 图片url

    Returns: 包含图片URL和分析结果的字典

    """
    # 读取颜色检测方式
    color_detection_method = os.getenv("COLOR_DETECTION_METHOD", "opencv").strip().lower()

    # Step 1: 颜色检测
    color_results = {}
    if FILTER_COLOR:
        if color_detection_method == "opencv":
            # 使用传统图像处理
            detector = ColorDetector()
            is_match = detector.detect_color(image_url, FILTER_COLOR)
            color_results[f"is_{FILTER_COLOR}"] = is_match
        else:
            # 使用大模型判断，放到 Step 2 中处理
            pass

    # Step 2: 其他属性（GPT-4o 大模型）
    # 根据检测方式决定哪些属性用大模型判断
    if FILTER_COLOR and color_detection_method == "opencv":
        # 如果配置了颜色筛选且使用 OpenCV，排除该颜色属性
        non_color_attrs = [
            attr for attr in CLOTHING_ATTRIBUTES
            if attr['key'] != f"is_{FILTER_COLOR}"
        ]
    else:
        # 其他情况：使用大模型判断所有属性（包括颜色）
        non_color_attrs = CLOTHING_ATTRIBUTES

    # 如果没有非颜色属性需要判断，直接返回颜色结果
    if not non_color_attrs:
        return {
            "image_url": image_url,
            "analysis": color_results
        }

    # 构建分析提示词（只包含非颜色属性）
    questions_text = "\n".join([
        f"{i+1}. {attr['key']}: {attr['description']}"
        for i, attr in enumerate(non_color_attrs)
    ])

    example_json = {
        attr['key']: attr['default'] if attr['key'] != 'is_long_sleeve' else True
        for attr in non_color_attrs
    }
    # 修改示例值使其更有意义
    if "is_long_sleeve" in example_json:
        example_json["is_long_sleeve"] = True
    if "has_both_sides_pattern" in example_json:
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

        # 动态构建返回结果（只包含非颜色属性）
        ai_result = {
            attr['key']: result.get(attr['key'], attr['default'])
            for attr in non_color_attrs
        }

        # Step 3: 合并颜色检测结果和 AI 分析结果
        analysis_result = {
            **color_results,
            **ai_result
        }
        return {
            "image_url": image_url,
            "analysis": analysis_result
        }

    except Exception as e:
        error_log = traceback.format_exc()
        logger.error(f"分析图片时出错: {error_log}")
        raise ValueError(error_log)


def process_single_image(image_url: str, index: int) -> Dict:
    """
    处理单个图片

    Args:
        image_url: 图片URL
        index: 索引编号

    Returns: 处理结果字典
    """
    try:
        logger.info(f"[{index}] 开始分析: {image_url}")
        result = analyze_clothing_image(image_url)
        logger.info(f"[{index}] 分析完成: {image_url}")
        return {
            "index": index,
            **result
        }
    except Exception as e:
        logger.error(f"[{index}] 分析失败 {image_url}: {str(e)}")
        return {
            "index": index,
            "image_url": image_url,
            "error": str(e),
            "analysis": None
        }


def jsonl_to_csv(jsonl_file: str, csv_file: str) -> None:
    """
    将 JSONL 文件转换为 CSV 文件，展开 analysis 字段

    Args:
        jsonl_file: JSONL 文件路径
        csv_file: 输出的 CSV 文件路径
    """
    results = []

    # 读取 JSONL 文件
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)

                # 构建展开后的行数据
                # image_view字段作用是直接在excel软件预览图片，操作方式见https://blog.wangjunfeng.com/post/excel-url-to-image/
                index = data.get("index")
                row = {
                    "index": index,
                    "image_url": data.get("image_url"),
                    "image_view": f'="<table><img src="&B{index + 1}&" height=100 width=100></table>"',
                }

                # 如果有错误信息
                if data.get("error"):
                    row["error"] = data.get("error")

                # 展开 analysis 字段
                analysis = data.get("analysis", {})
                if analysis:
                    for attr in CLOTHING_ATTRIBUTES:
                        key = attr['key']
                        row[key] = analysis.get(key, attr['default'])

                results.append(row)

    # 获取所有列名
    if not results:
        logger.warning("没有数据需要写入 CSV")
        return

    # 构建 CSV 列名：基础字段 + 所有 analysis 字段
    fieldnames = list(row.keys())

    # 写入 CSV 文件
    with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    logger.info(f"CSV 文件已保存: {csv_file}")


def main():
    # 读取 URLs
    urls_file = PROJECT_ROOT / "urls.txt"
    if not os.path.exists(urls_file):
        logger.error(f"文件不存在: {urls_file}")
        return

    with open(urls_file, "r", encoding="utf-8") as f:
        image_urls = [line.strip() for line in f if line.strip()]

    # image_urls = image_urls[0:500]

    if not image_urls:
        logger.warning("urls.txt 中没有找到任何 URL")
        return

    max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    logger.info(f"共找到 {len(image_urls)} 个图片 URL，并发数{max_concurrent_requests}，开始并发处理...")

    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # 并发处理
    max_workers = max_concurrent_requests
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_index = {
            executor.submit(process_single_image, url, i + 1): (i + 1, url)
            for i, url in enumerate(image_urls)
        }

        # 收集结果
        for future in as_completed(future_to_index):
            index, url = future_to_index[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"[{index}] 处理异常 {url}: {str(e)}")
                results.append({
                    "index": index,
                    "image_url": url,
                    "error": str(e),
                    "analysis": None
                })

    # 保存结果为 JSONL
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_file = os.path.join(output_dir, f"analysis_result_{timestamp}.jsonl")

    with open(jsonl_file, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    logger.info(f"JSONL 文件已保存: {jsonl_file}")

    # 转换为 CSV
    csv_file = os.path.join(output_dir, f"analysis_result_{timestamp}.csv")
    jsonl_to_csv(jsonl_file, csv_file)

    # 统计结果
    success_count = sum(1 for r in results if r.get("analysis") is not None)
    error_count = len(results) - success_count
    logger.info(f"统计: 成功 {success_count}, 失败 {error_count}")

    # 只在配置了 Langfuse 时输出日志链接
    if os.getenv("LANGFUSE_SECRET_KEY") and os.getenv("LANGFUSE_CLOUD_LOG"):
        logger.info(f"大模型日志查看：{os.getenv('LANGFUSE_CLOUD_LOG')}")

if __name__ == "__main__":
    main()
