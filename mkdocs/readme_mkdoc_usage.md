# mkdocs的使用说明

## 结构

1. 按版本目录管理文档。
2. 发布使用mike创建不同版本的文档发布到github的git-pages分支。

## 文档预览

本地预览单独版本的mkdocs文档页面

```bash
cd mkdocs/v1
uv run mkdocs serve
# 访问 http://127.0.0.1:8000/asmysql/
```
如果要预览文档的所有版本，就像在生产服务器上看到的那样，
可以通过以下方式在本地提供这些版本：

```bash
cd mkdocs
uv run mike serve
# 这将直接提供当前仓库中提交到 gh-pages 分支的文档。
# 默认情况下，它会在 http://localhost:8000 提供文档，
# 但可以使用 -a/--dev-addr 更改此设置。
# 直接访问 http://127.0.0.1:8000/asmysql/
```

## GitHub Pages(GitHub配置mkdocs文档)

```bash
# 在 GitHub 仓库 Settings → Pages 中：
# Source: 选择 GitHub Actions
# 推送代码后，GitHub Actions 会自动构建并部署到:
# https://vastxiao.github.io/asmysql/
```