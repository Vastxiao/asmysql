---
hide:
  - navigation
  - toc
---

# asmysql

<div style="text-align: center; margin: 2rem 0;">
  <img src="https://img.shields.io/pypi/v/asmysql.svg?logo=pypi&logoColor=FFE873" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/asmysql.svg?logo=python&logoColor=FFE873" alt="Python">
  <img src="https://img.shields.io/github/license/Vastxiao/asmysql.svg" alt="License">
  <img src="https://static.pepy.tech/badge/asmysql" alt="Downloads">
</div>

<div style="text-align: center; margin: 3rem 0;">
  <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">异步 MySQL 客户端库</h2>
  <p style="font-size: 1.2rem; color: var(--md-default-fg-color--light);">
    基于 aiomysql 封装，为 Python 异步编程提供简单而强大的 MySQL 操作 API
  </p>
</div>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin: 2rem 0;">
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color);">
    <h3>🚀 简单易用</h3>
    <p>直观的 API 设计，学习成本低，快速上手</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color);">
    <h3>⚡ 高性能</h3>
    <p>基于连接池的异步操作，支持高并发场景</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color);">
    <h3>🔧 类型安全</h3>
    <p>完整的类型提示支持，提升开发体验</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color);">
    <h3>💾 内存友好</h3>
    <p>支持流式查询，处理大数据集不占用内存</p>
  </div>
</div>

## 快速安装

```bash
pip install asmysql
```

## 快速示例

```python
import asyncio
from asmysql import Engine

async def main():
    # 创建引擎
    engine = Engine(
        host='localhost',
        port=3306,
        user='root',
        password='password',
        db='test'
    )

    # 连接数据库
    await engine.connect()

    # 执行查询
    result = await engine.query("SELECT * FROM users WHERE id = %s", (1,))
    user = await result.fetch_one(as_dict=True)
    print(user)

    # 关闭连接
    await engine.close()

asyncio.run(main())
```

## 文档版本

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0;">
  <a href="zh/v2/" style="display: block; padding: 1.5rem; border-radius: 8px; background: var(--md-primary-fg-color); color: white; text-decoration: none; text-align: center;">
    <strong style="font-size: 1.2rem;">V2 中文文档</strong>
    <br><span style="opacity: 0.9;">最新版本 (推荐)</span>
  </a>
  <a href="en/v2/" style="display: block; padding: 1.5rem; border-radius: 8px; background: var(--md-primary-fg-color); color: white; text-decoration: none; text-align: center;">
    <strong style="font-size: 1.2rem;">V2 English Docs</strong>
    <br><span style="opacity: 0.9;">Latest (Recommended)</span>
  </a>
  <a href="zh/v1/" style="display: block; padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); text-decoration: none; text-align: center;">
    <strong style="font-size: 1.2rem;">V1 中文文档</strong>
    <br><span style="opacity: 0.7;">旧版本</span>
  </a>
  <a href="en/v1/" style="display: block; padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); text-decoration: none; text-align: center;">
    <strong style="font-size: 1.2rem;">V1 English Docs</strong>
    <br><span style="opacity: 0.7;">Legacy</span>
  </a>
</div>

## 链接

- **PyPI**: [pypi.org/project/asmysql](https://pypi.org/project/asmysql/)
- **GitHub**: [github.com/vastxiao/asmysql](https://github.com/vastxiao/asmysql)
- **Gitee**: [gitee.com/vastxiao/asmysql](https://gitee.com/vastxiao/asmysql)
