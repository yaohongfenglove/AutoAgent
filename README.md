# 服装图片特征分析工具

基于 OpenAI 视觉模型的批量服装图片特征分析工具，支持并发处理，自动输出 JSONL 和 CSV 双格式结果。

## 功能特点

- 批量分析服装图片的多个特征属性
- 并发处理提升效率
- 双格式输出（JSONL + CSV）
- CSV 支持 Excel 图片预览公式
- 详细的日志记录
- 可选的 Langfuse 大模型调用追踪

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入配置
```

**必填配置：**
- `OPENAI_API_KEY`: OpenAI API 密钥

**可选配置：**
- `LANGFUSE_SECRET_KEY` / `LANGFUSE_PUBLIC_KEY`: Langfuse 日志追踪（不配置不影响主功能）
- `MAX_CONCURRENT_REQUESTS`: 并发请求数

### 3. 准备图片 URL

创建 `urls.txt` 文件，每行一个图片 URL：

```
https://example.com/image1.jpg
https://example.com/image2.jpg
...
```

或复制示例文件：
```bash
cp urls.txt.example urls.txt
```

### 4. 运行分析

```bash
python main.py
```


### 5. 查看结果

分析结果保存在 `output/` 目录：
- `analysis_result_时间戳.jsonl` - JSONL 格式原始数据
- `analysis_result_时间戳.csv` - CSV 格式（Excel 友好）

## CSV 图片预览

打开 CSV 文件后，`image_view` 列包含 Excel 公式，可在 Excel 中预览图片：

1. 打开 CSV 文件
2. 选中 `image_view` 列
3. 复制并粘贴到记事本再复制回来（触发公式计算）
4. 或参考 [Excel URL 转图片教程](https://blog.wangjunfeng.com/post/excel-url-to-image/)

## 项目结构

```
AutoAgent/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── requirements.txt     # 依赖列表
├── .env.example         # 环境变量模板
├── urls.txt.example     # URL输入示例
├── utils/               # 工具模块
│   ├── constants.py     # 常量定义
│   ├── logger.py        # 日志配置
│   └── ...
├── output/              # 分析结果输出目录
└── logs/                # 运行日志目录
```

## 常见问题

**Q: 如何调整并发数量？**
A: 修改 `.env` 文件中的 `MAX_CONCURRENT_REQUESTS` 值。

**Q: 支持哪些图片格式？**
A: 支持可通过 URL 访问的常见图片格式（JPG、PNG、WEBP 等）。

**Q: API 调用失败怎么办？**
A: 检查网络连接、API 密钥是否正确、API 地址是否可访问。

**Q: 如何查看详细日志？**
A: 日志文件保存在 `logs/` 目录。如需查看大模型调用追踪，需配置 Langfuse 密钥。

## 许可证

MIT License
