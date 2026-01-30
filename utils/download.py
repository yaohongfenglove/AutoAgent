import traceback

import requests

from config import PROJECT_ROOT
from utils.logger import logger


def download_images():
    # 读取 urls.txt
    with open(PROJECT_ROOT / 'urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    # 创建 output 文件夹
    output_dir = PROJECT_ROOT / 'output'
    output_dir.mkdir(exist_ok=True)

    # 下载前3张图片
    for index, url in enumerate(iterable=urls[:3], start=0):
        sn = index + 1
        try:
            logger.info(f'正在下载第 {sn} 张图片: {url}')
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # 根据URL确定文件扩展名
            ext = '.jpg' if '.jpg' in url.lower() or '.jpeg' in url.lower() else '.png'

            # 保存图片
            filename = output_dir / f'{sn}{ext}'
            with open(filename, 'wb') as f:
                f.write(response.content)

            logger.info(f'✓ 下载成功: {filename}')

        except Exception as e:
            error_str = traceback.format_exc()
            logger.info(f'✗ 下载失败 {url}: {error_str}')

    logger.info(f'\n完成！图片已保存到 {output_dir} 文件夹')

if __name__ == '__main__':
    download_images()
