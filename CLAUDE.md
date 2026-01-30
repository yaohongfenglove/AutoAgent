## 编码规范

### Windows 控制台兼容性
Windows CMD 默认 GBK 编码，不支持 Unicode 特殊字符（✓ ✗ ★ 等）。使用 ASCII 安全字符替代：

| 不推荐 | 推荐 |
|--------|------|
| ✓ | [OK] |
| ✗ | [X] |
| → | -> |
| ★ | [!] |

```python
# 正确写法
print(f"[OK] 下载成功 -> {path}")
print(f"[X] 下载失败")
```

### 常量管理
所有常量必须定义在 `utils/constants.py` 中

### 命名规范
- 类名：大驼峰 `BaseModel`
- 函数/变量：小写+下划线 `download_urls`
- 常量：全大写+下划线 `CLOTHING_ATTRIBUTES`