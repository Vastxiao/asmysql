# asmysql v2 Technical Documentation

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

## Introduction

`asmysql` is an asynchronous MySQL client library based on `aiomysql`, designed for Python asynchronous programming. The v2 version has completely refactored the architecture, providing a clearer and more flexible API design, supporting type hints, connection pool management, error handling, and other enterprise-level features.

### Main Advantages

- **Simple and Easy to Use**: Intuitive API design with low learning curve
- **Type Safe**: Complete type hint support for better development experience
- **High Performance**: Asynchronous operations based on connection pool, supporting high concurrency
- **Flexible Extension**: Separated engine and business logic for better architecture design
- **Memory Friendly**: Supports streaming queries, handling large datasets without memory consumption

## Features

### Core Features of v2 Version

1. **Separated Architecture**
   - `Engine` class: Independent MySQL connection engine, can be used standalone
   - `AsMysql` class: Business logic development base class, ready to use by inheritance
   - `Result` class: Result processing class, supporting multiple data retrieval methods

2. **Connection Management**
   - Automatic MySQL connection pool management
   - Support for connection pool configuration (min/max connections)
   - Automatic reconnection mechanism
   - Connection status monitoring

3. **Flexible Query Methods**
   - Support for regular queries and streaming queries
   - Support for single and batch execution
   - Support for transaction control

4. **Multiple Result Types**
   - `tuple`: Default tuple type
   - `dict`: Dictionary type
   - Custom models: Support for Pydantic and other model classes

5. **Data Retrieval Methods**
   - `fetch_one()`: Get a single record
   - `fetch_many()`: Get multiple records
   - `fetch_all()`: Get all records
   - `iterate()`: Async iterator, get records row by row
   - Direct iteration: `async for item in result`

6. **Error Handling**
   - Global automatic capture of `MysqlError`
   - Error code and error message access
   - Elegant error handling mechanism

7. **Context Management**
   - Support for `async with` syntax
   - Automatic resource cleanup
   - Support for async iterator protocol

8. **URL Connection String**
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

## Quick Navigation

- [Installation Guide](installation.md) - Installation and dependency requirements
- [Quick Start](quickstart.md) - Quick start examples
- [Connection Management](connection.md) - Connection configuration and management
- [Query Operations](query.md) - Execute SQL statements
- [Result Processing](result.md) - Retrieve and process query results
- [Transaction Control](transaction.md) - Transaction management
- [Business Logic](business-logic.md) - Business logic development
- [Best Practices](best-practices.md) - Recommended usage patterns
- [FAQ](faq.md) - FAQ
- [API Reference](api.md) - Complete API documentation
- [Usage Examples](examples.md) - Detailed usage examples
- [Changelog](changelog.md) - Version update records

