---
hide:
  - navigation
  - toc
---

<div style="text-align: center; margin: 2rem 0;">
  <h1 style="margin-bottom: 0;">AsMysql</h1>
</div>

<div style="text-align: center; margin: 2rem 0;">
  <img src="https://img.shields.io/pypi/v/asmysql.svg?logo=pypi&logoColor=FFE873" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/asmysql.svg?logo=python&logoColor=FFE873" alt="Python">
  <img src="https://img.shields.io/github/license/Vastxiao/asmysql.svg" alt="License">
  <img src="https://static.pepy.tech/badge/asmysql" alt="Downloads">
  <img src="https://static.pepy.tech/badge/asmysql/month" alt="Monthly Downloads">
  <img src="https://static.pepy.tech/badge/asmysql/week" alt="Weekly Downloads">
</div>

<div style="text-align: center; margin: 3rem 0;">
  <h2 style="font-size: 2.5rem; margin-bottom: 2rem; font-weight: 600;">异步 MySQL 客户端库</h2>
  <div style="max-width: 800px; margin: 0 auto; text-align: left; display: inline-block;">
    <ul style="list-style: none; padding: 0; margin: 0;">
      <li style="font-size: 1.2rem; color: var(--md-default-fg-color--light); line-height: 1.8; margin-bottom: 1rem; padding-left: 1.5rem; position: relative;">
        <span style="position: absolute; left: 0; color: var(--md-primary-fg-color);">•</span>
        asmysql 是一个基于 aiomysql 封装的异步 MySQL 客户端库，专为 Python 异步编程设计。
      </li>
      <li style="font-size: 1.2rem; color: var(--md-default-fg-color--light); line-height: 1.8; padding-left: 1.5rem; position: relative;">
        <span style="position: absolute; left: 0; color: var(--md-primary-fg-color);">•</span>
        v2 版本完全重构了架构，提供了更清晰、更灵活的 API 设计，支持类型提示、连接池管理、错误处理等企业级特性。
      </li>
    </ul>
  </div>
</div>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin: 3rem 0; max-width: 1200px; margin-left: auto; margin-right: auto;">
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">🚀 简单易用</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">直观的 API 设计，学习成本低，快速上手</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">⚡ 高性能</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">基于连接池的异步操作，支持高并发场景</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">🔧 类型安全</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">完整的类型提示支持，提升开发体验</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">💾 内存友好</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">支持流式查询，处理大数据集不占用内存</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">🔌 灵活扩展</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">分离引擎和业务逻辑，便于架构设计</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">🪶 超轻量级</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">极小的代码体积，无冗余依赖，部署简单</p>
  </div>
</div>

## 快速开始

### 安装

```bash
pip install asmysql
```

### 快速示例

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

## 核心特性

### v2 版本核心特性

#### 1. 分离式架构
- **`Engine` 类**：独立的 MySQL 连接引擎，可单独使用
- **`AsMysql` 类**：业务逻辑开发基类，继承即可使用
- **`Result` 类**：结果处理类，支持多种数据获取方式

#### 2. 连接管理
- 自动管理 MySQL 连接池
- 支持连接池配置（最小/最大连接数）
- 自动重连机制
- 连接状态监控

#### 3. 灵活的查询方式
- 支持普通查询和流式查询
- 支持单条和批量执行
- 支持事务控制

#### 4. 多种结果类型
- `tuple`：默认元组类型
- `dict`：字典类型
- 自定义模型：支持 Pydantic 等模型类

#### 5. 数据获取方式
- `fetch_one()`：获取单条记录
- `fetch_many()`：获取多条记录
- `fetch_all()`：获取所有记录
- `iterate()`：异步迭代器，逐行获取
- 直接迭代：`async for item in result`

#### 6. 错误处理
- 全局自动捕获 `MysqlError`
- 错误码和错误信息访问
- 优雅的错误处理机制

#### 7. 上下文管理
- 支持 `async with` 语法
- 自动资源清理
- 支持异步迭代器协议

#### 8. URL 连接字符串
- 支持 MySQL URL 格式连接
- 格式：`mysql://user:password@host:port/?charset=utf8mb4`

## 核心概念

### Engine（引擎）

`Engine` 是 MySQL 连接的核心类，负责：

- 管理连接池
- 执行 SQL 语句
- 处理连接生命周期

### AsMysql（业务逻辑类）

`AsMysql` 是业务逻辑开发的基类，提供：

- `client` 属性：访问 `Engine` 实例
- 业务方法封装
- 代码组织能力

### Result（结果类）

`Result` 是 SQL 执行结果的封装类，提供：

- 数据获取方法
- 错误信息访问
- 执行统计信息
- 异步迭代支持

## 相关链接

- **PyPI**: [pypi.org/project/asmysql](https://pypi.org/project/asmysql/)
- **GitHub**: [github.com/vastxiao/asmysql](https://github.com/vastxiao/asmysql)
- **Gitee**: [gitee.com/vastxiao/asmysql](https://gitee.com/vastxiao/asmysql)
- **文档**: [vastxiao.github.io/asmysql](https://vastxiao.github.io/asmysql/)
