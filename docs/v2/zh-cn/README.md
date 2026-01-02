# asmysql v2 技术文档

[![PyPI](https://img.shields.io/pypi/v/asmysql.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Python](https://img.shields.io/pypi/pyversions/asmysql.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Licence](https://img.shields.io/github/license/Vastxiao/asmysql.svg)](https://github.com/Vastxiao/asmysql/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/asmysql)](https://pepy.tech/project/asmysql)
[![Downloads](https://static.pepy.tech/badge/asmysql/month)](https://pepy.tech/project/asmysql)
[![Downloads](https://static.pepy.tech/badge/asmysql/week)](https://pepy.tech/project/asmysql)

* PyPI: https://pypi.org/project/asmysql/
* GitHub: https://github.com/vastxiao/asmysql
* Gitee: https://gitee.com/vastxiao/asmysql
* Docs: https://vastxiao.github.io/asmysql

## 简介

`asmysql` 是一个基于 `aiomysql` 封装的异步 MySQL 客户端库，专为 Python 异步编程设计。v2 版本完全重构了架构，提供了更清晰、更灵活的 API 设计，支持类型提示、连接池管理、错误处理等企业级特性。

### 主要优势

- **简单易用**：直观的 API 设计，学习成本低
- **类型安全**：完整的类型提示支持，提升开发体验
- **高性能**：基于连接池的异步操作，支持高并发
- **灵活扩展**：分离引擎和业务逻辑，便于架构设计
- **内存友好**：支持流式查询，处理大数据集不占用内存

## 特性

### v2 版本核心特性

1. **分离式架构**
   - `Engine` 类：独立的 MySQL 连接引擎，可单独使用
   - `AsMysql` 类：业务逻辑开发基类，继承即可使用
   - `Result` 类：结果处理类，支持多种数据获取方式

2. **连接管理**
   - 自动管理 MySQL 连接池
   - 支持连接池配置（最小/最大连接数）
   - 自动重连机制
   - 连接状态监控

3. **灵活的查询方式**
   - 支持普通查询和流式查询
   - 支持单条和批量执行
   - 支持事务控制

4. **多种结果类型**
   - `tuple`：默认元组类型
   - `dict`：字典类型
   - 自定义模型：支持 Pydantic 等模型类

5. **数据获取方式**
   - `fetch_one()`：获取单条记录
   - `fetch_many()`：获取多条记录
   - `fetch_all()`：获取所有记录
   - `iterate()`：异步迭代器，逐行获取
   - 直接迭代：`async for item in result`

6. **错误处理**
   - 全局自动捕获 `MysqlError`
   - 错误码和错误信息访问
   - 优雅的错误处理机制

7. **上下文管理**
   - 支持 `async with` 语法
   - 自动资源清理
   - 支持异步迭代器协议

8. **URL 连接字符串**
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

## 快速导航

- [安装指南](installation.md) - 安装和依赖要求
- [快速开始](quickstart.md) - 快速上手示例
- [连接管理](connection.md) - 连接配置和管理
- [查询操作](query.md) - 执行 SQL 语句
- [结果处理](result.md) - 获取和处理查询结果
- [事务控制](transaction.md) - 事务管理
- [业务逻辑](business-logic.md) - 业务逻辑开发
- [最佳实践](best-practices.md) - 推荐的使用方式
- [常见问题](faq.md) - FAQ
- [API 参考](api.md) - 完整的 API 文档
- [使用示例](examples.md) - 详细的使用示例
- [变更日志](changelog.md) - 版本更新记录
