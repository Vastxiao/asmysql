# asmysql v2 变更日志

本文档记录 asmysql v2 版本的所有变更。

## [v2.0.0](changelog/v2.0.0.md)

### 重大变更 (Breaking Changes)

v2.0.0 是一个完全重构的版本，与 v1 版本不兼容。主要变更包括：

- **架构重构**：分离 `Engine` 和 `AsMysql` 类，新增独立的 `Engine` 类处理 MySQL 连接和执行语句
- **Result 类变更**：`Result.err` 属性重命名为 `Result.error`
- **API 变更**：连接方式从自动连接改为显式创建 `Engine` 并调用 `connect()`

### 新功能 (New Features)

- **Engine 类**：全新的连接引擎类，支持 URL 连接字符串、连接状态监控、灵活的连接管理
- **Result 类增强**：支持错误信息访问（`error_no`、`error_msg`）、流式查询、上下文管理器、异步迭代器、自定义结果类型
- **执行方法增强**：`execute()` 方法支持 `stream`、`result_class`、`commit` 等参数，支持多种调用方式
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
