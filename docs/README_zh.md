# asmysql 文档

[![PyPI](https://img.shields.io/pypi/v/asmysql.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Python](https://img.shields.io/pypi/pyversions/asmysql.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Licence](https://img.shields.io/github/license/Vastxiao/asmysql.svg)](https://github.com/Vastxiao/asmysql/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/asmysql)](https://pepy.tech/project/asmysql)

* PyPI: https://pypi.org/project/asmysql/
* GitHub: https://github.com/vastxiao/asmysql
* Gitee: https://gitee.com/vastxiao/asmysql

## 简介

`asmysql` 是封装 `aiomysql` 的 MySQL 异步客户端使用库，为 Python 异步编程提供简单而强大的 API。

## 快速导航

### 最新版本 (v2)
- [快速开始](v2/zh-cn/readme.md) - 快速入门指南
- [API 参考](v2/zh-cn/api.md) - 完整 API 文档
- [使用示例](v2/zh-cn/examples.md) - 代码示例和使用场景
- [更新日志](v2/zh-cn/changelog.md) - 版本历史

### 版本 1 (旧版)
- [文档](v1/zh-cn/README.md) - v1 文档
- [更新日志](v1/zh-cn/CHANGELOG.md) - v1 更新日志

## 特性

* 代码支持类型注释
* 使用极为简单，直接继承 AsMysql 类进行逻辑开发
* 支持自动管理 MySQL 连接池和重连机制
* 全局自动捕获处理 MysqlError 错误
* 分离 MySQL 连接引擎和开发逻辑类
* 分离执行语句和数据获取
* 支持无缓存数据流获取用于大数据结果集获取（不占用内存）

## 安装

```bash
pip install asmysql
```

## 快速开始

### 使用 Engine 类进行 MySQL 连接：

```python
import asyncio
from asmysql import Engine

# 创建 MySQL 连接引擎
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

async def main():
    # 连接 MySQL
    await engine.connect()
    # 执行 SQL 语句
    async with engine.execute("select user,host from mysql.user") as result:
        async for item in result.iterate():
            print(item)
    # 断开 MySQL 连接
    await engine.disconnect()

asyncio.run(main())
```

### 使用 AsMysql 类进行逻辑开发：

```python
import asyncio
from asmysql import Engine
from asmysql import AsMysql

# 编写逻辑开发类
class TestAsMysql(AsMysql):
    async def print_users(self):
        result = await self.client.execute('select user,host from mysql.user')
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            async for item in result.iterate():
                print(item)

async def main():
    # 创建 MySQL 连接引擎
    engine = Engine(host='192.168.1.192', port=3306)
    # 连接 MySQL
    await engine.connect()
    # 创建逻辑开发类实例
    test_mysql = TestAsMysql(engine)
    # 执行逻辑
    await test_mysql.print_users()
    # 断开 MySQL 连接
    await engine.disconnect()

asyncio.run(main())
```

## 文档

详细文档请参考：
- [最新版本 (v2) 文档](v2/zh-cn/readme.md)
- [版本 1 文档](v1/zh-cn/README.md)
