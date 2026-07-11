# asmysql 开发与验证流程规范

当用户要求开发新功能、修复 Bug 或重构代码时，严格按照以下流程执行。

## 流程总览

```
分析 → 设计 → 实现 → 验证 → 文档 → 发布检查
```

## Phase 1: 分析（Analyze）

1. **理解需求**：阅读用户的完整需求描述，确认理解无误
2. **探索代码**：使用 Explore 代理或 Read 工具探索相关源文件
   - 核心文件：`asmysql/v2/_engine.py`、`_result.py`、`_asmysql.py`、`_error.py`
   - 测试文件：`autopytest/v2/`
   - 文档文件：`mkdocs/v2/docs/{zh,en}/`
3. **识别影响范围**：列出需要修改的所有文件
4. **检查已有实现**：搜索是否已有类似功能可复用，避免重复代码

## Phase 2: 设计（Design）

1. **进入计划模式**：使用 EnterPlanMode 设计实现方案
2. **列出方案选项**：如有多种实现路径，分析优劣并推荐最佳方案
3. **评估风险**：识别可能的破坏性变更和向后兼容性问题
4. **获取用户确认**：通过 ExitPlanMode 让用户审批方案后再动手

## Phase 3: 实现（Implement）

### 代码编写规范

- **语言**：源码中使用中文 docstring
- **类型标注**：所有公开方法和属性必须有完整的类型提示
- **`@final`**：Engine 和 AsMysql 的核心方法使用 `@final` 禁止重写
- **`Final`**：`__init__` 中赋值的不可变属性使用 `typing.Final` 标注
- **参数默认值**：使用 `x if x is not None else default` 而非 `x or default`
- **异常处理**：
  - 使用自定义异常类（`AsMysqlError`、`ConnectionError`、`QueryError`）
  - `except` 分支必须确保资源释放（连接归还连接池）
  - 使用 `try/finally` 保护资源清理代码
- **并发安全**：共享状态操作使用 `asyncio.Lock` 保护
- **缓存装饰器**：实例方法不使用 `@lru_cache`（会阻止 GC），改用 `@cached_property`
- **连接管理**：所有获取连接的路径必须确保在异常/提前退出时释放连接

### 文件修改顺序

1. `_error.py`（异常定义）
2. `_result.py`（Result 类）
3. `_engine.py`（Engine 类）
4. `_asmysql.py`（AsMysql 包装类）
5. `__init__.py`（导出更新）

## Phase 4: 验证（Verify）— 最关键步骤

### 4.1 单元测试（必选，每次修改后必须执行）

```bash
# 运行全部 Mock 测试
uv run pytest autopytest/v2/ -v

# 运行指定测试文件
uv run pytest autopytest/v2/test_asmysql_mock.py -v
uv run pytest autopytest/v2/test_bugfixes.py -v
uv run pytest autopytest/v2/test_engine_init_sql.py -v
```

**通过标准**：所有测试 PASSED，零 FAILED

### 4.2 代码检查（必选）

```bash
uv run ruff check asmysql/
```

**通过标准**：零错误

### 4.3 集成测试（可选，需要 MySQL 实例）

```bash
uv run pytest -m integration -v
```

### 4.4 构建验证（发布前必选）

```bash
uv build
```

**通过标准**：构建成功，输出 dist/ 目录

### 4.5 回归检查清单

每次修改后，逐一确认：

- [ ] 所有现有 Mock 测试通过
- [ ] ruff 检查通过
- [ ] 新增功能有对应测试覆盖
- [ ] 修改的公开 API 向后兼容（或有破坏性变更说明）
- [ ] 连接泄漏风险已评估（所有 acquire 路径都有对应 release）
- [ ] 并发安全已评估（共享状态是否有 Lock 保护）

## Phase 5: 文档（Document）

### 5.1 变更日志（必选）

修改以下 4 个文件：
- `mkdocs/v2/docs/zh/changelog/vX.Y.Z.md`（中文详细记录）
- `mkdocs/v2/docs/en/changelog/vX.Y.Z.md`（英文详细记录）
- `mkdocs/v2/docs/zh/changelog.md`（中文索引摘要）
- `mkdocs/v2/docs/en/changelog.md`（英文索引摘要）

**格式规范**：
- 详细页面按分类：`### 新功能`、`### 缺陷修复`、`### 文档`、`### 测试`
- 每条以 **粗体简短标题** 开头，后接冒号和详细说明
- 中文页面使用双语标题：`### 中文 (English)`
- 索引页面使用精简的 bullet point 摘要

### 5.2 API 文档（如涉及公开 API 变更）

更新 `mkdocs/v2/docs/{zh,en}/api.md` 中的相关 API 描述。

### 5.3 翻译一致性

中英文文档必须保持：
- 相同的结构和行数
- 相同的代码块
- 相同的技术术语

## Phase 6: 发布检查（Release Check）

发布前最终检查：

```bash
# 1. 全部测试
uv run pytest -v

# 2. 代码检查
uv run ruff check asmysql/

# 3. 构建
uv build

# 4. 检查导出
python -c "from asmysql import Engine, Result, AsMysql, EngineStatus, AsMysqlError, ConnectionError, QueryError; print('All exports OK')"
```

## 常见问题防护

### 连接泄漏检查模式

```python
# 正确：try/finally 确保释放
conn = None
try:
    conn = await self.pool.acquire()
    # ... 使用 conn ...
except Exception:
    if conn is not None:
        self.pool.release(conn)
    raise
```

### 参数解析安全模式

```python
# 错误：or 运算符会覆盖 falsy 值
self.port = port or self.port  # port=0 被覆盖

# 正确：显式 None 检查
self.port = port if port is not None else self.port
```

### 布尔 URL 参数解析

```python
# 错误：非空字符串都是 truthy
auto_commit = True if query_params.get("auto_commit")[0] else auto_commit

# 正确：解析布尔字符串
val = query_params.get("auto_commit", [None])[0]
if val is not None:
    auto_commit = val.lower() in ("true", "1", "yes")
```
