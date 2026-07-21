# Django 集成

<cite>
**本文引用的文件**
- [README.md](file://README.md)
- [pyproject.toml](file://pyproject.toml)
- [asmysql/__init__.py](file://asmysql/__init__.py)
- [asmysql/v2/__init__.py](file://asmysql/v2/__init__.py)
- [asmysql/v2/_asmysql.py](file://asmysql/v2/_asmysql.py)
- [asmysql/v2/_engine.py](file://asmysql/v2/_engine.py)
- [asmysql/v2/_result.py](file://asmysql/v2/_result.py)
- [asmysql/v3dev/_async_engine.py](file://asmysql/v3dev/_async_engine.py)
- [asmysql/v3dev/_sync_engine.py](file://asmysql/v3dev/_sync_engine.py)
- [tests/v2/v2_start.py](file://tests/v2/v2_start.py)
- [mkdocs/v2/docs/zh/examples.md](file://mkdocs/v2/docs/zh/examples.md)
- [mkdocs/v2/docs/zh/transaction.md](file://mkdocs/v2/docs/zh/transaction.md)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构总览](#架构总览)
5. [详细组件分析](#详细组件分析)
6. [依赖分析](#依赖分析)
7. [性能考虑](#性能考虑)
8. [故障排查指南](#故障排查指南)
9. [结论](#结论)
10. [附录](#附录)

## 简介
本指南面向在 Django 项目中集成 asmysql 的开发者，覆盖以下目标：
- 如何在 Django settings 中配置 asmysql（含 URL 与连接池参数）
- 如何编写自定义数据库后端以支持异步查询（可选）
- 中间件开发要点（事务、连接生命周期、错误处理）
- 在视图函数中使用 asmysql（FBV 与 CBV 两种模式）
- 同步与异步混合场景的处理方案
- 事务处理、连接池调优、查询优化等企业级实践
- 从 Django ORM 渐进迁移到 asmysql 的路径

## 项目结构
asmysql 提供 v2 稳定版与 v3dev 实验版。v2 基于 aiomysql 实现异步引擎与结果集封装；v3dev 同时提供异步与同步两套 Engine 实现，便于在 Django 中按需选择。

```mermaid
graph TB
subgraph "asmysql 包"
A["asmysql/__init__.py"] --> B["asmysql/v2/__init__.py"]
B --> C["asmysql/v2/_asmysql.py"]
B --> D["asmysql/v2/_engine.py"]
B --> E["asmysql/v2/_result.py"]
A --> F["asmysql/v3dev/_async_engine.py"]
A --> G["asmysql/v3dev/_sync_engine.py"]
end
subgraph "文档与测试"
H["mkdocs/v2/docs/zh/examples.md"]
I["mkdocs/v2/docs/zh/transaction.md"]
J["tests/v2/v2_start.py"]
end
K["README.md"] --> H
L["pyproject.toml"] --> D
```

图表来源
- [asmysql/__init__.py:1-16](file://asmysql/__init__.py#L1-L16)
- [asmysql/v2/__init__.py:1-15](file://asmysql/v2/__init__.py#L1-L15)
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [mkdocs/v2/docs/zh/examples.md:1-800](file://mkdocs/v2/docs/zh/examples.md#L1-L800)
- [mkdocs/v2/docs/zh/transaction.md:1-44](file://mkdocs/v2/docs/zh/transaction.md#L1-L44)
- [tests/v2/v2_start.py:1-107](file://tests/v2/v2_start.py#L1-L107)
- [README.md:1-135](file://README.md#L1-L135)
- [pyproject.toml:1-80](file://pyproject.toml#L1-L80)

章节来源
- [README.md:1-135](file://README.md#L1-L135)
- [pyproject.toml:1-80](file://pyproject.toml#L1-L80)

## 核心组件
- Engine（异步）：封装 aiomysql 连接池，提供 connect/disconnect、execute/execute_many、状态查询等能力。支持 URL 初始化与多种连接池参数。
- Result：封装游标执行、自动提交控制、错误信息、流式迭代、批量获取等。
- AsMysql（业务基类）：持有 Engine 引用，暴露 client 属性用于执行 SQL，便于将数据库逻辑按业务域组织。
- v3dev 同步/异步双引擎：为 Django 同步路径或需要纯同步访问的场景提供替代实现。

章节来源
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)

## 架构总览
Django 作为 WSGI/ASGI 应用，通常运行在事件循环之外（WSGI）或在 ASGI 事件循环内（ASGI）。asmysql 的异步引擎需要在事件循环上下文中使用。下图展示在 Django 中通过中间件管理 Engine 生命周期并在视图中调用 asmysql 的基本流程。

```mermaid
sequenceDiagram
participant Client as "客户端"
participant Django as "Django 应用"
participant MW as "DB中间件"
participant Eng as "Engine(异步)"
participant DB as "MySQL"
Client->>Django : HTTP 请求
Django->>MW : 进入中间件
MW->>Eng : connect()
Eng-->>MW : 已连接
MW->>Django : 继续处理请求
Django->>MW : 返回响应前
MW->>Eng : disconnect()
Eng-->>MW : 已断开
MW-->>Django : 完成
Django-->>Client : 响应
```

图表来源
- [asmysql/v2/_engine.py:120-183](file://asmysql/v2/_engine.py#L120-L183)

章节来源
- [asmysql/v2/_engine.py:120-183](file://asmysql/v2/_engine.py#L120-L183)

## 详细组件分析

### 组件一：Engine（异步）
- 职责：创建与管理 aiomysql 连接池；提供 execute/execute_many；暴露 status/is_connected/pool 等元数据。
- 关键特性：
  - URL 初始化：支持 mysql://user:pass@host:port/?charset=... 及 min_pool_size/max_pool_size/pool_recycle/connect_timeout/auto_commit/echo_sql_log/stream/result_class 等参数解析。
  - 上下文管理器：支持 async with engine: 自动 connect/disconnect。
  - 可调用对象：await engine(...) 等价于 connect。
  - 执行器：execute/execute_many 返回 Result，支持 commit 参数控制单条语句提交策略。
- 复杂度与性能：
  - 连接池复用，避免频繁建连开销。
  - stream=True 时采用 SSCursor/SSDictCursor，降低大结果集内存占用。
  - echo_sql_log 开启后可辅助定位慢查询。

```mermaid
classDiagram
class Engine {
+str host
+int port
+str user
+str password
+str charset
+int min_pool_size
+int max_pool_size
+float pool_recycle
+int connect_timeout
+bool auto_commit
+bool echo_sql_log
+bool stream
+type result_class
+url str
+connect() awaitable
+disconnect() awaitable
+status dict
+is_connected bool
+pool Pool
+execute(query, values, stream, result_class, commit) Result
+execute_many(query, values, stream, result_class, commit) Result
}
```

图表来源
- [asmysql/v2/_engine.py:37-317](file://asmysql/v2/_engine.py#L37-L317)

章节来源
- [asmysql/v2/_engine.py:37-317](file://asmysql/v2/_engine.py#L37-L317)

### 组件二：Result
- 职责：封装游标执行、错误捕获、结果获取（fetch_one/fetch_many/fetch_all）、异步迭代（iterate/async for）、自动关闭与连接释放。
- 关键特性：
  - 支持 tuple/dict/自定义类（如 Pydantic）作为 result_class，自动构造对象。
  - error/error_no/error_msg 统一错误信息。
  - row_count/last_rowid/row_number 等元信息。
  - __aiter__/__anext__ 支持 async for item in result。
  - 自动提交：默认 commit=True，可通过 execute(..., commit=False) 配合手动提交。

```mermaid
classDiagram
class Result~T~ {
+Pool pool
+str query
+Union[Sequence,dict] values
+bool stream
+bool commit
+error MySQLError?
+error_no int
+error_msg str
+row_count int?
+last_rowid int?
+row_number int?
+fetch_one(close) T?
+fetch_many(size, close) list[T]
+fetch_all() list[T]
+iterate() AsyncGenerator[T]
+close() awaitable
}
```

图表来源
- [asmysql/v2/_result.py:21-273](file://asmysql/v2/_result.py#L21-L273)

章节来源
- [asmysql/v2/_result.py:21-273](file://asmysql/v2/_result.py#L21-L273)

### 组件三：AsMysql（业务基类）
- 职责：持有 Engine 引用，对外暴露 client 属性，便于按业务域组织方法。
- 适用场景：在 Django 服务层（Service/Repository）中封装 SQL 操作，提高复用性与可测试性。

```mermaid
classDiagram
class AsMysql {
-Engine __engine
+client Engine
+__repr__() str
+__str__() str
}
AsMysql --> Engine : "持有引用"
```

图表来源
- [asmysql/v2/_asmysql.py:7-26](file://asmysql/v2/_asmysql.py#L7-L26)

章节来源
- [asmysql/v2/_asmysql.py:7-26](file://asmysql/v2/_asmysql.py#L7-L26)

### 组件四：v3dev 同步/异步双引擎
- 异步引擎：与 v2 类似，面向 ASGI 环境。
- 同步引擎：面向 WSGI 或需要同步访问 MySQL 的场景，内部使用同步连接池。
- 建议：在 Django 中优先使用异步引擎（ASGI），若必须同步访问则使用同步引擎。

章节来源
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)

### 在 Django 中的集成方案

#### 1) Settings 配置
- 使用 URL 方式集中配置连接参数，包括字符集、连接池大小、回收时间、超时、是否自动提交、SQL 日志开关等。
- 示例键值参考（仅字段说明，不含代码内容）：
  - DATABASES.ASMYSQL_URL：形如 mysql://user:pass@host:port/?charset=utf8mb4&min_pool_size=5&max_pool_size=50&pool_recycle=3600&connect_timeout=10&auto_commit=True&echo_sql_log=False
  - 其他可选：stream、result_class（字符串形式，如 "dict" 或自定义模型名）

章节来源
- [asmysql/v2/_engine.py:56-112](file://asmysql/v2/_engine.py#L56-L112)
- [asmysql/v3dev/_async_engine.py:45-101](file://asmysql/v3dev/_async_engine.py#L45-L101)
- [asmysql/v3dev/_sync_engine.py:44-101](file://asmysql/v3dev/_sync_engine.py#L44-L101)

#### 2) 自定义数据库后端（可选）
- 目标：让 Django ORM 仍可使用，同时在特定路由或服务层切换到 asmysql 进行高性能异步查询。
- 思路：
  - 保留现有 DATABASES 配置不变。
  - 在应用启动时根据 settings 构建 Engine 实例并缓存。
  - 在需要异步读写的服务层直接调用 Engine.execute/execute_many。
  - 如需完全替换 ORM 驱动，可参考 Django 自定义后端接口，但需自行实现连接、事务、游标等协议（工作量较大，建议渐进迁移）。

章节来源
- [asmysql/v2/_engine.py:120-183](file://asmysql/v2/_engine.py#L120-L183)

#### 3) 中间件开发（推荐）
- 职责：
  - 在请求进入时确保 Engine 已连接（或复用全局 Engine）。
  - 在请求结束时安全断开连接或归还连接池。
  - 统一错误处理与日志记录。
- 关键点：
  - 使用 async with engine: 或显式 connect/disconnect。
  - 对异常进行捕获并转换为合适的 HTTP 响应。
  - 在 ASGI 模式下确保所有 await 调用处于事件循环中。

章节来源
- [asmysql/v2/_engine.py:120-183](file://asmysql/v2/_engine.py#L120-L183)

#### 4) 视图函数中使用 asmysql
- FBV（函数式视图）：
  - 在视图内通过全局或注入的 Engine 执行查询。
  - 注意在 ASGI 下使用 await。
- CBV（类视图）：
  - 在 dispatch/get/post 等方法中调用 Engine。
  - 建议使用继承自 asmysql.AsMysql 的服务类封装业务逻辑，视图只负责编排与响应。

章节来源
- [tests/v2/v2_start.py:1-107](file://tests/v2/v2_start.py#L1-L107)
- [mkdocs/v2/docs/zh/examples.md:1-800](file://mkdocs/v2/docs/zh/examples.md#L1-L800)

#### 5) 同步与异步混合场景
- 场景：Django 主框架为 ASGI，但某些第三方库或遗留模块需要同步访问 MySQL。
- 方案：
  - 使用 v3dev 的同步引擎（SyncEngine）进行同步访问。
  - 或将同步调用放入线程池执行，避免阻塞事件循环。
  - 注意区分不同 Engine 实例的连接池，避免混用导致资源竞争。

章节来源
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)

#### 6) 事务处理
- 自动提交（默认）：execute(..., commit=True) 每条语句自动提交。
- 手动提交：设置 auto_commit=False，并通过 execute(..., commit=False) 组合，最后由连接层提交。
- 注意事项：
  - v2 版本的事务管理需要手动控制连接，建议在 Service 层封装事务边界。
  - 发生异常时应回滚或抛出异常，确保一致性。

章节来源
- [mkdocs/v2/docs/zh/transaction.md:1-44](file://mkdocs/v2/docs/zh/transaction.md#L1-L44)
- [asmysql/v2/_result.py:101-125](file://asmysql/v2/_result.py#L101-L125)

#### 7) 连接池调优
- 关键参数：
  - min_pool_size：最小空闲连接数，预热连接减少冷启动延迟。
  - max_pool_size：最大连接数，结合并发量与数据库承载能力评估。
  - pool_recycle：空闲连接回收时间，避免长连接被服务端回收。
  - connect_timeout：连接超时，防止雪崩。
- 监控：
  - 使用 engine.status 观察 pool_size/pool_free/pool_used 等指标。
  - 结合日志与告警，动态调整参数。

章节来源
- [asmysql/v2/_engine.py:37-112](file://asmysql/v2/_engine.py#L37-L112)
- [asmysql/v2/_engine.py:154-166](file://asmysql/v2/_engine.py#L154-L166)

#### 8) 查询优化
- 流式查询：对大数据集启用 stream=True，使用 iterate()/async for 逐行处理，避免内存溢出。
- 结果类型：使用 result_class=dict 或自定义模型（如 Pydantic）提升可读性与校验能力。
- 批量操作：使用 execute_many 减少往返次数。
- SQL 日志：开启 echo_sql_log 辅助定位慢查询。

章节来源
- [asmysql/v2/_result.py:251-273](file://asmysql/v2/_result.py#L251-L273)
- [mkdocs/v2/docs/zh/examples.md:406-469](file://mkdocs/v2/docs/zh/examples.md#L406-L469)

#### 9) 从 Django ORM 渐进迁移到 asmysql
- 阶段一：并行读写
  - 保持 ORM 不变，新增 asmysql 服务层用于热点读路径。
- 阶段二：写路径拆分
  - 将部分写入逻辑迁移至 asmysql，利用 execute_many 与事务控制提升吞吐。
- 阶段三：全面替换（可选）
  - 逐步替换 ORM 调用，最终完全使用 asmysql。
- 风险控制：
  - 灰度发布与流量切分。
  - 对比数据一致性与性能指标。
  - 完善单元测试与回归测试。

章节来源
- [mkdocs/v2/docs/zh/examples.md:1-800](file://mkdocs/v2/docs/zh/examples.md#L1-L800)

## 依赖分析
- 运行时依赖：aiomysql[rsa]>=0.3.2，pymysql.err.MySQLError 用于错误处理。
- 包导出：顶层 asmysql.__init__ 暴露 v2 的 AsMysql/Engine/Result 以及 AsyncEngine/AsyncResult 别名。
- 耦合关系：
  - Engine 依赖 aiomysql.Pool/create_pool。
  - Result 依赖 aiomysql.Cursor/DictCursor/SSCursor/SSDictCursor。
  - AsMysql 仅依赖 Engine，低耦合高内聚。

```mermaid
graph LR
Django["Django 应用"] --> MW["中间件"]
MW --> Eng["Engine(v2/_engine.py)"]
Eng --> Pool["aiomysql.Pool"]
Eng --> Res["Result(v2/_result.py)"]
Res --> Cursor["aiomysql.Cursor*"]
AsM["AsMysql(v2/_asmysql.py)"] --> Eng
```

图表来源
- [asmysql/__init__.py:1-16](file://asmysql/__init__.py#L1-L16)
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)

章节来源
- [pyproject.toml:31-34](file://pyproject.toml#L31-L34)
- [asmysql/__init__.py:1-16](file://asmysql/__init__.py#L1-L16)

## 性能考虑
- 连接池：合理设置 min_pool_size/max_pool_size，避免过大导致数据库压力或过小造成等待。
- 流式读取：大数据集务必使用 stream=True 与 iterate()/async for。
- 批量写入：使用 execute_many 减少网络往返。
- SQL 日志：生产环境谨慎开启 echo_sql_log，仅在问题定位时临时启用。
- 监控与告警：基于 engine.status 输出关键指标，结合 Prometheus/Grafana 可视化。

## 故障排查指南
- 常见错误：
  - 未连接即使用 pool：会抛出 ConnectionError。
  - 事务未提交：检查 auto_commit 与 execute(..., commit=...) 的组合。
  - 大结果集内存溢出：确认是否启用 stream=True 并使用迭代器。
- 诊断步骤：
  - 打印 engine.status 查看连接池状态。
  - 检查 result.error/error_no/error_msg 定位具体错误。
  - 开启 echo_sql_log 抓取 SQL 文本，结合数据库慢查询日志分析。

章节来源
- [asmysql/v2/_engine.py:185-202](file://asmysql/v2/_engine.py#L185-L202)
- [asmysql/v2/_result.py:133-151](file://asmysql/v2/_result.py#L133-L151)
- [mkdocs/v2/docs/zh/transaction.md:1-44](file://mkdocs/v2/docs/zh/transaction.md#L1-L44)

## 结论
通过合理的中间件管理与 Engine 生命周期控制，asmysql 可在 Django 中高效地提供异步数据库访问能力。结合流式查询、批量操作与连接池调优，能够显著提升吞吐与稳定性。对于从 ORM 迁移的场景，建议采用渐进式策略，先并行后替换，确保平滑过渡与风险可控。

## 附录
- 快速上手参考：
  - 基础用法与示例见文档与测试用例。
  - 事务控制与最佳实践参见相关文档。

章节来源
- [README.md:1-135](file://README.md#L1-L135)
- [mkdocs/v2/docs/zh/examples.md:1-800](file://mkdocs/v2/docs/zh/examples.md#L1-L800)
- [mkdocs/v2/docs/zh/transaction.md:1-44](file://mkdocs/v2/docs/zh/transaction.md#L1-L44)
- [tests/v2/v2_start.py:1-107](file://tests/v2/v2_start.py#L1-L107)