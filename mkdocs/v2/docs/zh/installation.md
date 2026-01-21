# 安装指南

## 从 PyPI 安装

```bash
pip install asmysql
```

## 从源码安装

```bash
git clone https://github.com/vastxiao/asmysql.git
cd asmysql
pip install .
```

## 依赖要求

- Python >= 3.9
- aiomysql[rsa] >= 0.3.2

## 验证安装

安装完成后，可以通尝试导入主要类验证安装成功：

```python
from asmysql import Engine, AsMysql
print("安装成功！")
```
