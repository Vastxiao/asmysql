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
  <h2 style="font-size: 2.5rem; margin-bottom: 2rem; font-weight: 600;">Asynchronous MySQL Client Library</h2>
  <div style="max-width: 800px; margin: 0 auto; text-align: left; display: inline-block;">
    <ul style="list-style: none; padding: 0; margin: 0;">
      <li style="font-size: 1.2rem; color: var(--md-default-fg-color--light); line-height: 1.8; margin-bottom: 1rem; padding-left: 1.5rem; position: relative;">
        <span style="position: absolute; left: 0; color: var(--md-primary-fg-color);">•</span>
        asmysql is an asynchronous MySQL client library based on aiomysql, designed for Python asynchronous programming.
      </li>
      <li style="font-size: 1.2rem; color: var(--md-default-fg-color--light); line-height: 1.8; padding-left: 1.5rem; position: relative;">
        <span style="position: absolute; left: 0; color: var(--md-primary-fg-color);">•</span>
        The v2 version has completely refactored the architecture, providing a clearer and more flexible API design, supporting type hints, connection pool management, error handling, and other enterprise-level features.
      </li>
    </ul>
  </div>
</div>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin: 3rem 0; max-width: 1200px; margin-left: auto; margin-right: auto;">
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">🚀 Simple & Easy</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">Intuitive API design with low learning curve, quick to get started</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">⚡ High Performance</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">Asynchronous operations based on connection pool, supporting high concurrency</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">🔧 Type Safe</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">Complete type hint support for better development experience</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s;">
    <h3 style="margin-top: 0;">💾 Memory Friendly</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">Supports streaming queries, handling large datasets without memory consumption</p>
  </div>
  <div style="padding: 1.5rem; border-radius: 8px; background: var(--md-code-bg-color); border: 1px solid var(--md-default-fg-color--lightest); transition: transform 0.2s; grid-column: 2;">
    <h3 style="margin-top: 0;">🔌 Flexible Extension</h3>
    <p style="margin-bottom: 0; color: var(--md-default-fg-color--light);">Separated engine and business logic for better architecture design</p>
  </div>
</div>

## Quick Start

### Installation

```bash
pip install asmysql
```

### Quick Example

```python
import asyncio
from asmysql import Engine

async def main():
    # Create engine
    engine = Engine(
        host='localhost',
        port=3306,
        user='root',
        password='password',
        db='test'
    )

    # Connect to database
    await engine.connect()

    # Execute query
    result = await engine.query("SELECT * FROM users WHERE id = %s", (1,))
    user = await result.fetch_one(as_dict=True)
    print(user)

    # Close connection
    await engine.close()

asyncio.run(main())
```

## Core Features

### Core Features of v2 Version

#### 1. Separated Architecture
- **`Engine` class**: Independent MySQL connection engine, can be used standalone
- **`AsMysql` class**: Business logic development base class, ready to use by inheritance
- **`Result` class**: Result processing class, supporting multiple data retrieval methods

#### 2. Connection Management
- Automatic MySQL connection pool management
- Support for connection pool configuration (min/max connections)
- Automatic reconnection mechanism
- Connection status monitoring

#### 3. Flexible Query Methods
- Support for regular queries and streaming queries
- Support for single and batch execution
- Support for transaction control

#### 4. Multiple Result Types
- `tuple`: Default tuple type
- `dict`: Dictionary type
- Custom models: Support for Pydantic and other model classes

#### 5. Data Retrieval Methods
- `fetch_one()`: Get a single record
- `fetch_many()`: Get multiple records
- `fetch_all()`: Get all records
- `iterate()`: Async iterator, get records row by row
- Direct iteration: `async for item in result`

#### 6. Error Handling
- Global automatic capture of `MysqlError`
- Error code and error message access
- Elegant error handling mechanism

#### 7. Context Management
- Support for `async with` syntax
- Automatic resource cleanup
- Support for async iterator protocol

#### 8. URL Connection String
- Support for MySQL URL format connection
- Format: `mysql://user:password@host:port/?charset=utf8mb4`

## Core Concepts

### Engine

`Engine` is the core class for MySQL connections, responsible for:

- Managing connection pool
- Executing SQL statements
- Handling connection lifecycle

### AsMysql (Business Logic Class)

`AsMysql` is the base class for business logic development, providing:

- `client` attribute: Access to `Engine` instance
- Business method encapsulation
- Code organization capability

### Result

`Result` is the encapsulation class for SQL execution results, providing:

- Data retrieval methods
- Error information access
- Execution statistics
- Async iteration support

## Related Links

- **PyPI**: [pypi.org/project/asmysql](https://pypi.org/project/asmysql/)
- **GitHub**: [github.com/vastxiao/asmysql](https://github.com/vastxiao/asmysql)
- **Gitee**: [gitee.com/vastxiao/asmysql](https://gitee.com/vastxiao/asmysql)
- **Documentation**: [vastxiao.github.io/asmysql](https://vastxiao.github.io/asmysql/)
