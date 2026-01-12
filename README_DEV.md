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

## 本地预览mkdocs文档

```bash
cd mkdocs
uv run mkdocs serve
# 访问 http://127.0.0.1:8000/
```

## GitHub Pages(GitHub配置mkdocs文档)

```bash
# 在 GitHub 仓库 Settings → Pages 中：
# Source: 选择 GitHub Actions
# 推送代码后，GitHub Actions 会自动构建并部署到:
# https://vastxiao.github.io/asmysql/
```