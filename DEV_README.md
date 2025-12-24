# 环境配置帮助文档

## 环境依赖

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or
pip install uv
```

## 开发环境搭建

```bash
# 初始化开发环境
uv sync

# 查看包依赖
#uv tree
# 查看已安装的依赖
#uv pip list
# 在当前shell激活python环境
#. .venv/bin/activate
```

## 运行pytest测试功能

```bash
uv run python run_pytest.py
```

## 构建软件包

```bash
[ -f dist ] && rm -rvf dist
uv build
# 打包文件在dist目录下
```

## 发布软件包

```bash
# test:
uv publish --username __token__

# pypi:
uv publish --index testpypi --username __token__
```