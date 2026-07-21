# asmysql v2 变更日志

本文档记录 asmysql v2 版本的所有变更。

## [v2.1.0](changelog/v2.1.0.md)

### 新功能 (New Features)

- **连接初始化 SQL（`init_sql`）**：新增 `init_sql` 参数，支持在每条新 TCP 连接首次使用时自动执行预设 SQL，适用于 ClickHouse 异步插入配置、MySQL Session 变量设置等场景。使用 `WeakKeyDictionary` 追踪已初始化连接，完全向后兼容。

### 重大变更 (Breaking Changes)

- **自动提交机制重构**：移除 `auto_commit` Engine 参数和 `commit` execute/Result 参数，改为基于 SQL 语句首关键词的自动提交机制（`_should_commit()`）。写操作自动 COMMIT，读操作不提交，stream 模式不提交
- **移除 Engine `stream` 参数**：`stream` 不再是 Engine 类属性，仅在 `execute()` 方法级别使用
- **移除 Engine `result_class` 参数**：`result_class` 不再是 Engine 类属性或构造参数，仅在 `execute()` / `execute_many()` 方法级别使用，默认值为 `tuple`

### 缺陷修复 (Bug Fixes)

- 修复 6 个连接泄漏问题：`fetch_all()` 自定义类型泄漏、错误后双重释放、`async for` + `break` 泄漏、非 MySQLError 异常泄漏、`__del__` 崩溃、DDL/DML 语句未释放连接
- 修复 5 个逻辑错误：`echo_sql_log` URL 解析、`or` 运算符覆盖 falsy 值、并发竞态条件、pool 空值传递、泛型参数语义错误
- 修复 5 个中低危问题：`release_connections()` 空值检查、`@lru_cache` 内存泄漏、`error_msg` 格式化、`iterate()` 检查不一致、属性访问崩溃

### 文档 (Documentation)

- 修正首页示例代码中不存在的 API
- 在 `connection.md`、`api.md`、`examples.md` 中同步添加 `init_sql` 文档（中英文版本）
- 重写事务控制文档，描述基于 SQL 语句类型的自动提交机制
- 修正 API 文档签名：移除不存在的 `close`/`commit` 参数

### 测试 (Testing)

- 新增 `test_engine_init_sql.py`，覆盖 `init_sql` 核心功能与边界场景
- 重写集成测试 `engine` fixture，通过 `init_sql=USE <test_db>` 自动选择测试数据库
- 移除 `test_mock_engine.py` 中与 Engine `result_class` 相关的测试用例

## [v2.0.0](changelog/v2.0.0.md)

### 重大变更 (Breaking Changes)

v2.0.0 是一个完全重构的版本，与 v1 版本不兼容。主要变更包括：

- **架构重构**：分离 `Engine` 和 `AsMysql` 类，新增独立的 `Engine` 类处理 MySQL 连接和执行语句
- **Result 类变更**：`Result.err` 属性重命名为 `Result.error`
- **API 变更**：连接方式从自动连接改为显式创建 `Engine` 并调用 `connect()`

### 新功能 (New Features)

- **Engine 类**：全新的连接引擎类，支持 URL 连接字符串、连接状态监控、灵活的连接管理
- **Result 类增强**：支持错误信息访问（`error_no`、`error_msg`）、流式查询、上下文管理器、异步迭代器、自定义结果类型
- **执行方法增强**：`execute()` 方法支持 `stream`、`result_class` 等参数，支持多种调用方式
- **类型提示**：完整的类型提示支持，支持泛型类型（`Result[T]`）
- **测试**：新增 pytest 测试套件，覆盖主要功能场景

### 更新 (Updates)

- **包管理工具**：使用 `uv` 作为包管理工具
- **代码质量**：改进代码结构、错误处理和文档字符串

### 核心特性 (Features)

v2 版本保留了 v1 版本的核心特性：

1. **简易使用**：asmysql 是对 aiomysql 封装的简易使用库
2. **连接池管理**：自动管理 MySQL 连接池，支持重连机制
3. **错误处理**：全局自动捕获 `MysqlError` 错误
4. **执行与获取分离**：执行 SQL 语句和获取结果分离
5. **类型提示**：完整的 Python 类型提示支持
6. **业务逻辑开发**：直接继承 `AsMysql` 类进行逻辑开发

### 迁移指南

详细的迁移指南请参考 [迁移指南](migration.md)。
