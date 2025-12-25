# asmysql Documentation

[![PyPI](https://img.shields.io/pypi/v/asmysql.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Python](https://img.shields.io/pypi/pyversions/asmysql.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Licence](https://img.shields.io/github/license/Vastxiao/asmysql.svg)](https://github.com/Vastxiao/asmysql/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/asmysql)](https://pepy.tech/project/asmysql)

* PyPI: https://pypi.org/project/asmysql/
* GitHub: https://github.com/vastxiao/asmysql
* Gitee: https://gitee.com/vastxiao/asmysql

## Introduction

`asmysql` is a library for using the MySQL asynchronous client, which is a wrapper for `aiomysql`. It provides a simple and powerful API for async MySQL operations in Python.

## Quick Navigation

### Latest Version (v2)
- [Getting Started](v2/zh-cn/readme.md) - Quick start guide
- [API Reference](v2/zh-cn/api.md) - Complete API documentation
- [Examples](v2/zh-cn/examples.md) - Code examples and use cases
- [Changelog](v2/zh-cn/changelog.md) - Version history

### Version 1 (Legacy)
- [Documentation](v1/en-us/README.md) - v1 documentation
- [Changelog](v1/en-us/CHANGELOG.md) - v1 changelog

## Features

* Code supports type annotations
* Very easy to use, simply inherit the AsMysql class for logical development
* Supports automatic management of the MySQL connection pool and reconnection mechanism
* Automatically captures and handles MysqlError errors globally
* Separates MySQL connection engine and development logic class
* Separates statement execution from data retrieval
* Supports uncached data stream acquisition for large data result sets (without occupying memory)

## Installation

```bash
pip install asmysql
```

## Quick Start

### Using Engine class for MySQL connection:

```python
import asyncio
from asmysql import Engine

# Create MySQL connection engine
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

async def main():
    # Connect to MySQL
    await engine.connect()
    # Execute SQL statement
    async with engine.execute("select user,host from mysql.user") as result:
        async for item in result.iterate():
            print(item)
    # Disconnect MySQL connection
    await engine.disconnect()

asyncio.run(main())
```

### Using AsMysql class for logical development:

```python
import asyncio
from asmysql import Engine
from asmysql import AsMysql

# Write logical development class
class TestAsMysql(AsMysql):
    async def print_users(self):
        result = await self.client.execute('select user,host from mysql.user')
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            async for item in result.iterate():
                print(item)

async def main():
    # Create MySQL connection engine
    engine = Engine(host='192.168.1.192', port=3306)
    # Connect to MySQL
    await engine.connect()
    # Create logical development class instance
    test_mysql = TestAsMysql(engine)
    # Execute logic
    await test_mysql.print_users()
    # Disconnect MySQL connection
    await engine.disconnect()

asyncio.run(main())
```

## Documentation

For detailed documentation, please refer to:
- [Latest Version (v2) Documentation](v2/zh-cn/readme.md)
- [Version 1 Documentation](v1/en-us/README.md)
