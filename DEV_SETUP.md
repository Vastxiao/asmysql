# 环境配置帮助文档

## 环境依赖

```bash
pip install poetry
```

## 开发环境搭建（poetry）

```bash
# 初始化开发环境
poetry install --all-extras
poetry show -t

# 在当前shell激活python环境
#poetry shell
```

## 构建软件包

```bash
[ -f dist ] && rm -rvf dist
poetry build
# 打包文件在dist目录下
```

## 发布软件包

```bash
# test:
# poetry config pypi-token.testpypi <my-token>
poetry publish -r testpypi --build

# pypi:
# poetry config pypi-token.pypi <my-token>
poetry publish --build
```
