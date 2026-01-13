# asmysql v2 Changelog

This document records all changes in asmysql v2 version.

## [v2.0.0](changelog/v2-0-0.md)

### Breaking Changes

v2.0.0 is a completely refactored version that is incompatible with v1. Main changes include:

- **Architecture Refactoring**: Separated `Engine` and `AsMysql` classes, added independent `Engine` class to handle MySQL connections and execute statements
- **Result Class Changes**: `Result.err` attribute renamed to `Result.error`
- **API Changes**: Connection method changed from auto-connect to explicitly creating `Engine` and calling `connect()`

### New Features

- **Engine Class**: Brand new connection engine class with URL connection string support, connection status monitoring, and flexible connection management
- **Result Class Enhancements**: Support for error information access (`error_no`, `error_msg`), streaming queries, context managers, async iterators, and custom result types
- **Execution Method Enhancements**: `execute()` method supports `stream`, `result_class`, `commit` parameters and multiple calling methods
- **Type Hints**: Complete type hint support with generic types (`Result[T]`)
- **Testing**: New pytest test suite covering main functional scenarios

### Updates

- **Package Management Tool**: Using `uv` as package management tool
- **Code Quality**: Improved code structure, error handling, and docstrings

### Core Features

v2 version retains the core features of v1:

1. **Easy to Use**: asmysql is an easy-to-use library that wraps aiomysql
2. **Connection Pool Management**: Automatic MySQL connection pool management with reconnection mechanism
3. **Error Handling**: Global automatic capture of `MysqlError` errors
4. **Separation of Execution and Retrieval**: Separation of SQL statement execution and result retrieval
5. **Type Hints**: Complete Python type hint support
6. **Business Logic Development**: Directly inherit `AsMysql` class for logic development

### Migration Guide

For detailed migration guide, please refer to [Migration Guide](migration.md).
