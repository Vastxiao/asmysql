# asmysql v2 Changelog

This document records all changes in asmysql v2 version.

## [v2.1.0](changelog/v2.1.0.md)

### New Features

- **Connection Init SQL (`init_sql`)**: Added `init_sql` parameter to automatically execute preset SQL on each new TCP connection's first use. Ideal for ClickHouse async insert configuration, MySQL session variable setup, and similar scenarios. Uses `WeakKeyDictionary` to track initialized connections. Fully backward compatible.

### Breaking Changes

- **Auto-Commit Mechanism Refactored**: Removed `auto_commit` Engine parameter and `commit` execute/Result parameter, replaced with SQL first-keyword-based auto-commit mechanism (`_should_commit()`). Write operations auto-COMMIT, read operations do not commit, stream mode does not commit
- **Removed Engine `stream` Parameter**: `stream` is no longer an Engine class attribute, only available at `execute()` method level
- **Removed Engine `result_class` Parameter**: `result_class` is no longer an Engine class attribute or constructor parameter, only available at the `execute()` / `execute_many()` method level, defaulting to `tuple`

### Bug Fixes

- Fixed 6 connection leak issues: `fetch_all()` custom type leak, double release after error, `async for` + `break` leak, non-MySQLError exception leak, `__del__` crash, DDL/DML statements not releasing connections
- Fixed 5 logic errors: `echo_sql_log` URL parsing, `or` operator overriding falsy values, concurrent race conditions, pool null passing, generic parameter semantic error
- Fixed 5 medium/low-severity issues: `release_connections()` null check, `@lru_cache` memory leak, `error_msg` formatting, `iterate()` check inconsistency, property access crashes

### Documentation

- Fixed non-existent API usage in homepage examples
- Added `init_sql` documentation across `connection.md`, `api.md`, and `examples.md` (both Chinese and English versions)
- Rewrote transaction control documentation to describe SQL statement type-based auto-commit mechanism
- Fixed API documentation signatures: removed non-existent `close`/`commit` parameters

### Testing

- Added `test_engine_init_sql.py` covering `init_sql` core functionality and edge cases
- Rewrote integration test `engine` fixture to auto-select test database via `init_sql=USE <test_db>`
- Removed Engine `result_class` related test cases from `test_mock_engine.py`

## [v2.0.0](changelog/v2.0.0.md)

### Breaking Changes

v2.0.0 is a completely refactored version that is incompatible with v1. Main changes include:

- **Architecture Refactoring**: Separated `Engine` and `AsMysql` classes, added independent `Engine` class to handle MySQL connections and execute statements
- **Result Class Changes**: `Result.err` attribute renamed to `Result.error`
- **API Changes**: Connection method changed from auto-connect to explicitly creating `Engine` and calling `connect()`

### New Features

- **Engine Class**: Brand new connection engine class with URL connection string support, connection status monitoring, and flexible connection management
- **Result Class Enhancements**: Support for error information access (`error_no`, `error_msg`), streaming queries, context managers, async iterators, and custom result types
- **Execution Method Enhancements**: `execute()` method supports `stream`, `result_class` parameters and multiple calling methods
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
