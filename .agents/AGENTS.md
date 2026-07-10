# AGENTS.md

## 项目简介

**asmysql** 是基于 `aiomysql` 封装的 Python 异步 MySQL 客户端库，提供连接池管理、异步查询执行、事务支持和流式结果集，支持 Python 3.9+。

- PyPI 包名：`asmysql`
- 核心依赖：`aiomysql[rsa]>=0.3.2`
- 构建后端：`uv_build`（通过 `uv`）
- 代码检查：`ruff`（配置在 `pyproject.toml`）

## 常用命令

```bash
# 初始化开发环境（默认使用阿里云镜像源）
uv sync

# 运行全部 Mock 测试（无需真实 MySQL）
uv run pytest

# 运行全部测试（包括集成测试，需要 MySQL）
uv run pytest -m ""

# 仅运行集成测试
uv run pytest -m integration

# 运行指定测试文件
uv run pytest autopytest/v2/test_asmysql_mock.py -v

# 运行单个测试函数
uv run pytest autopytest/v2/test_asmysql_mock.py::test_asmysql_creation -v

# 代码检查
uv run ruff check asmysql/

# 构建软件包（输出到 dist/）
uv build

# 发布到 PyPI
uv publish --username __token__

# 发布到 TestPyPI
uv publish --index testpypi --username __token__
```

## 架构

### 多版本并行设计

项目在 `asmysql/` 下同时维护多个 API 版本：

- **v1**（`asmysql/v1/`）：旧版兼容。单一 `AsMysql` 类同时承担连接管理与业务逻辑，通过 `CursorClient` 执行 SQL。导入方式：`from asmysql.v1 import AsMysql`。
- **v2**（`asmysql/v2/`）：**当前生产版本**（顶层 `asmysql` 包的导出目标）。将职责分离为 `Engine`（连接池 + 执行）和 `AsMysql`（业务逻辑封装）。导入方式：`from asmysql import Engine, AsMysql`。
- **v3dev**（`asmysql/v3dev/`）：**开发中，已从构建排除**（`pyproject.toml` 中 `source-exclude`）。在异步基础上新增同步支持，基于 `pymysql` 实现自定义连接池（`_sync_pool.py`）。导入别名为 `AsyncEngine` / `SyncEngine`。

### v2 核心设计模式

**Engine**（`_engine.py`）是核心类：
- 管理 `aiomysql.Pool` 生命周期（`connect()` / `disconnect()`）
- 支持 MySQL URL 格式：`mysql://user:pass@host:port/?charset=utf8mb4&param=value`
- `execute()` 和 `execute_many()` 返回 `Result` 对象（非直接协程）
- Engine 本身支持 `async with` 上下文管理器和 `await` 简写连接

**AsMysql**（`_asmysql.py`）是薄封装类：
- 构造时接收 `Engine` 实例，通过 `self.client` 属性暴露
- 业务逻辑通过继承此类实现；`__init__` 被 `@final` 标记，禁止重写

**Result**（`_result.py`）是多态异步结果对象：
- 支持 3 种使用方式：`await execute(...)`、`async with execute(...) as result:`、`async for item in result:`
- 额外提供 `iterate()` 异步生成器及 `fetch_one / fetch_many / fetch_all`
- 泛型参数 `T`：`tuple`（默认，使用 `Cursor` / `SSCursor`）、`dict`（使用 `DictCursor` / `SSDictCursor`）、或任意支持 `**kwargs` 构造的类（如 Pydantic `BaseModel`）
- 游标类型根据 `result_class` 和 `stream` 标志自动选择
- 数据耗尽或显式调用 `close()` 后自动释放连接回连接池

### v3dev 同步引擎

v3dev 新增 v2 API 的同步镜像：
- `_sync_pool.py`：基于 `pymysql` 的线程安全自定义连接池（仿照 `aiomysql.Pool` API）
- `_sync_engine.py`：使用自定义连接池的同步 `Engine`；`execute()` 返回同步 `Result`
- `_sync_result.py`：使用 `with` / `for` 替代 `async with` / `async for` 的同步版本
- `_asmysql.py`：泛型支持 `EngineType`（同步或异步引擎）

## 测试

测试位于 `autopytest/` 目录（`tests/` 目录存放的是独立开发实验脚本，非正式测试）：

- `autopytest/v2/`：v2 的 pytest 测试，Mock 测试 + 集成测试
- `autopytest/v3/`：v3dev 的测试（同步 + 异步），暂未迁移至 pytest
- 测试框架：`pytest` + `pytest-asyncio`（`asyncio_mode = "auto"`）
- 共享 fixtures 定义在 `autopytest/v2/conftest.py`
- 集成测试使用 `@pytest.mark.integration` 标记，默认跳过
- Mock 测试无需真实 MySQL 连接
- 集成测试（如 `autopytest/v2/test_asmysql.py`）需要可用的 MySQL 数据库

新增测试时，参照 `test_asmysql_mock.py` 的 Mock 模式编写，使用 pytest fixtures 和 `assert` 语句。

## 文档

- 双语文档：中文（`zh/`）和英文（`en/`），位于 `mkdocs/v2/docs/`
- 翻译工作流定义在 `ai_prompts/document_translation.md`，要求保持格式、行数、结构与源文档完全一致
- 使用 MkDocs Material 主题，配合 `mkdocs-static-i18n` 插件
- `README_zh.md` 为中文说明；`README.md` 为英文说明

## 关键约定

- `@final` 装饰器用于禁止重写的方法（尤其是 `Engine.__init__`、`connect`、`disconnect`、`execute` 等）
- `@lru_cache` 应用于 `__repr__` 和 `__str__` 以提升性能
- 源码中统一使用中文 docstring
- `typing.Final` 用于标注 `__init__` 中赋值的实例属性
- `Engine` 所有配置属性均有类级别默认值，也可通过 URL 查询参数传入
