# Engine 类 API

<cite>
**本文引用的文件**   
- [asmysql/v2/_engine.py](file://asmysql/v2/_engine.py)
- [asmysql/v3dev/_async_engine.py](file://asmysql/v3dev/_async_engine.py)
- [asmysql/v3dev/_sync_engine.py](file://asmysql/v3dev/_sync_engine.py)
- [asmysql/v3dev/_types.py](file://asmysql/v3dev/_types.py)
- [asmysql/v2/_result.py](file://asmysql/v2/_result.py)
- [asmysql/v3dev/_async_result.py](file://asmysql/v3dev/_async_result.py)
- [tests/v2/v2_start.py](file://tests/v2/v2_start.py)
- [tests/v3/test_async.py](file://tests/v3/test_async.py)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构总览](#架构总览)
5. [详细组件分析](#详细组件分析)
6. [依赖关系分析](#依赖关系分析)
7. [性能与连接池调优](#性能与连接池调优)
8. [故障排查指南](#故障排查指南)
9. [结论](#结论)
10. [附录：类型注解与泛型说明](#附录类型注解与泛型说明)

## 简介
本文件为 Engine 类的完整 API 文档，覆盖异步与同步两个实现版本。Engine 负责数据库连接池的创建、生命周期管理以及 SQL 执行入口（execute、execute_many）。其返回对象 Result 封装了游标操作、结果获取、错误信息与资源释放等能力。文档提供方法签名、参数与返回值类型、异常行为、使用示例（含异步上下文管理器）、状态属性说明、连接池配置最佳实践与性能建议，并给出完整的类型注解与泛型使用说明。

## 项目结构
Engine 在 v2 与 v3dev 中分别提供异步与同步实现：
- v2: 基于 aiomysql 的异步 Engine（同时导出 AsyncEngine 别名）
- v3dev: 分离出 _async_engine.py 与 _sync_engine.py，分别对应异步与同步 Engine；_types.py 定义 EngineStatus TypedDict；Result 分别位于 _async_result.py 与 _sync_result.py

```mermaid
graph TB
subgraph "v2"
V2_Engine["v2/_engine.py<br/>Engine(异步)"]
V2_Result["v2/_result.py<br/>Result(异步)"]
end
subgraph "v3dev"
A_Engine["v3dev/_async_engine.py<br/>Engine(异步)"]
S_Engine["v3dev/_sync_engine.py<br/>Engine(同步)"]
A_Result["v3dev/_async_result.py<br/>Result(异步)"]
Types["v3dev/_types.py<br/>EngineStatus(TypedDict)"]
end
TestsV2["tests/v2/v2_start.py"]
TestsV3["tests/v3/test_async.py"]
V2_Engine --> V2_Result
A_Engine --> A_Result
S_Engine --> A_Result
A_Engine --> Types
S_Engine --> Types
TestsV2 --> V2_Engine
TestsV3 --> A_Engine
```

图表来源
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v3dev/_async_result.py:1-273](file://asmysql/v3dev/_async_result.py#L1-L273)
- [tests/v2/v2_start.py:1-107](file://tests/v2/v2_start.py#L1-L107)
- [tests/v3/test_async.py:1-108](file://tests/v3/test_async.py#L1-L108)

章节来源
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v3dev/_async_result.py:1-273](file://asmysql/v3dev/_async_result.py#L1-L273)
- [tests/v2/v2_start.py:1-107](file://tests/v2/v2_start.py#L1-L107)
- [tests/v3/test_async.py:1-108](file://tests/v3/test_async.py#L1-L108)

## 核心组件
- Engine（异步/同步）
  - 负责解析连接 URL 与参数、创建/关闭连接池、暴露 execute/execute_many 作为统一查询入口、提供 status/is_connected/pool 等状态属性。
- Result（异步/同步）
  - 封装一次 SQL 执行的完整生命周期：获取连接、执行语句、提交事务（可选）、错误捕获、结果读取（fetch_one/fetch_many/fetch_all/iterate）、自动或手动关闭游标与连接释放。

章节来源
- [asmysql/v2/_engine.py:37-317](file://asmysql/v2/_engine.py#L37-L317)
- [asmysql/v3dev/_async_engine.py:27-307](file://asmysql/v3dev/_async_engine.py#L27-L307)
- [asmysql/v3dev/_sync_engine.py:26-298](file://asmysql/v3dev/_sync_engine.py#L26-L298)
- [asmysql/v2/_result.py:21-273](file://asmysql/v2/_result.py#L21-L273)
- [asmysql/v3dev/_async_result.py:21-273](file://asmysql/v3dev/_async_result.py#L21-L273)

## 架构总览
Engine 通过 create_pool（异步）或内部 Pool（同步）建立连接池；execute/execute_many 返回 Result 对象，Result 内部从池中申请连接、选择合适 Cursor 类型（普通/字典/流式），执行 SQL 并提供多种结果获取方式。

```mermaid
sequenceDiagram
participant App as "应用代码"
participant Eng as "Engine"
participant Pool as "连接池(aiomysql.Pool/自定义Pool)"
participant Conn as "连接"
participant Cur as "Cursor"
participant Res as "Result"
App->>Eng : "connect()"
Eng->>Pool : "create_pool(...)/初始化"
Pool-->>Eng : "池实例"
Eng-->>App : "self"
App->>Eng : "execute(query, values, ...)"
Eng->>Res : "构造 Result(pool, query, values, ...)"
Res->>Pool : "acquire() 获取连接"
Pool-->>Res : "Conn"
Res->>Conn : "cursor(CursorClass)"
Conn-->>Res : "Cur"
Res->>Cur : "execute/executemany"
Cur-->>Res : "执行完成/错误"
Res-->>App : "Result 对象"
App->>Res : "fetch_one()/fetch_many()/fetch_all()/iterate()"
Res->>Cur : "fetchone/fetchmany/fetchall"
Cur-->>Res : "数据行"
Res-->>App : "数据/None"
App->>Res : "close()/退出上下文"
Res->>Cur : "close()"
Res->>Pool : "release(conn)"
```

图表来源
- [asmysql/v2/_engine.py:131-151](file://asmysql/v2/_engine.py#L131-L151)
- [asmysql/v3dev/_async_engine.py:121-141](file://asmysql/v3dev/_async_engine.py#L121-L141)
- [asmysql/v2/_result.py:101-125](file://asmysql/v2/_result.py#L101-L125)
- [asmysql/v3dev/_async_result.py:101-125](file://asmysql/v3dev/_async_result.py#L101-L125)

## 详细组件分析

### 构造函数与参数
- 支持两种初始化方式：
  - 直接传入关键字参数 host/port/user/password/charset/min_pool_size/max_pool_size/pool_recycle/connect_timeout/auto_commit/echo_sql_log/stream/result_class
  - 传入 url 字符串，格式如 mysql://user:password@host:port/?charset=utf8mb4&min_pool_size=...
- 当 url 存在时，会解析 scheme 必须为 mysql，并从 URL 的 query 参数中覆盖同名配置项（包括布尔值 auto_commit/echo_sql_log 的解析逻辑）。
- 所有参数均为可选，未显式传入时将回退到类默认值。

参数清单与类型
- url: str | None
- host: str | None
- port: int | None
- user: str | None
- password: str | None
- charset: str | None
- min_pool_size: int | None
- max_pool_size: int | None
- pool_recycle: float | None
- connect_timeout: int | None
- auto_commit: bool | None
- echo_sql_log: bool | None
- stream: bool | None
- result_class: type | None

URL 解析规则要点
- scheme 必须为 mysql，否则抛出 ValueError
- 支持从 query 中解析 charset、min_pool_size、max_pool_size、pool_recycle、connect_timeout、auto_commit、echo_sql_log
- 数值型参数若为空字符串会被跳过，避免将 None 传给 int/float

章节来源
- [asmysql/v2/_engine.py:56-113](file://asmysql/v2/_engine.py#L56-L113)
- [asmysql/v3dev/_async_engine.py:46-104](file://asmysql/v3dev/_async_engine.py#L46-L104)
- [asmysql/v3dev/_sync_engine.py:45-103](file://asmysql/v3dev/_sync_engine.py#L45-L103)

### 公共方法与属性

#### connect()
- 作用：建立 TCP 连接并初始化连接池
- 异步版本：async def connect(self) -> self
- 同步版本：def connect(self) -> self
- 异常：底层 MySQLError 被转换为 ConnectionError 并向上抛出
- 幂等：已连接则直接返回 self

章节来源
- [asmysql/v2/_engine.py:131-151](file://asmysql/v2/_engine.py#L131-L151)
- [asmysql/v3dev/_async_engine.py:121-141](file://asmysql/v3dev/_async_engine.py#L121-L141)
- [asmysql/v3dev/_sync_engine.py:120-139](file://asmysql/v3dev/_sync_engine.py#L120-L139)

#### disconnect()
- 作用：等待所有连接释放并正常关闭连接池
- 异步版本：async def disconnect(self) -> None
- 同步版本：def disconnect(self) -> None
- 幂等：重复调用安全

章节来源
- [asmysql/v2/_engine.py:177-182](file://asmysql/v2/_engine.py#L177-L182)
- [asmysql/v3dev/_async_engine.py:167-172](file://asmysql/v3dev/_async_engine.py#L167-L172)
- [asmysql/v3dev/_sync_engine.py:161-164](file://asmysql/v3dev/_sync_engine.py#L161-L164)

#### release_connections()
- 作用：释放连接池中所有空闲连接
- 异步版本：async def release_connections(self) -> None
- 同步版本：无具体实现（空方法）

章节来源
- [asmysql/v2/_engine.py:185-187](file://asmysql/v2/_engine.py#L185-L187)
- [asmysql/v3dev/_async_engine.py:175-177](file://asmysql/v3dev/_async_engine.py#L175-L177)
- [asmysql/v3dev/_sync_engine.py:166-167](file://asmysql/v3dev/_sync_engine.py#L166-L167)

#### status
- 类型：property
- 返回值：EngineStatus TypedDict
  - address: str
  - connected: bool
  - pool_minsize: int | None
  - pool_maxsize: int | None
  - pool_size: int | None
  - pool_free: int | None
  - pool_used: int | None
- 用途：用于监控连接池状态

章节来源
- [asmysql/v2/_engine.py:154-166](file://asmysql/v2/_engine.py#L154-L166)
- [asmysql/v3dev/_async_engine.py:144-156](file://asmysql/v3dev/_async_engine.py#L44-L156)
- [asmysql/v3dev/_sync_engine.py:142-154](file://asmysql/v3dev/_sync_engine.py#L142-L154)
- [asmysql/v3dev/_types.py:4-12](file://asmysql/v3dev/_types.py#L4-L12)

#### is_connected
- 类型：property
- 返回值：bool
- 用途：判断是否已连接（即是否持有连接池实例）

章节来源
- [asmysql/v2/_engine.py:190-193](file://asmysql/v2/_engine.py#L190-L193)
- [asmysql/v3dev/_async_engine.py:180-183](file://asmysql/v3dev/_async_engine.py#L180-L183)
- [asmysql/v3dev/_sync_engine.py:170-173](file://asmysql/v3dev/_sync_engine.py#L170-L173)

#### pool
- 类型：property
- 返回值：连接池实例
- 异常：未连接时抛出 ConnectionError，提示先调用 connect()

章节来源
- [asmysql/v2/_engine.py:196-202](file://asmysql/v2/_engine.py#L196-L202)
- [asmysql/v3dev/_async_engine.py:186-192](file://asmysql/v3dev/_async_engine.py#L186-L192)
- [asmysql/v3dev/_sync_engine.py:176-182](file://asmysql/v3dev/_sync_engine.py#L176-L182)

#### execute(...)
- 作用：执行单条 SQL 并返回 Result 对象
- 签名（异步/同步一致，仅返回类型不同）：
  - execute(query: str, values: Sequence | dict | None = None, *, stream: bool | None = None, result_class: type[T] | None = None, commit: bool | None = None) -> Union[Awaitable[Result[T]], AsyncContextManager[Result[T]], AsyncGenerator[T, None]]（异步）
  - execute(query: str, values: Sequence | dict | None = None, *, stream: bool | None = None, result_class: type[T] | None = None, commit: bool | None = None) -> Union[Result[T], ContextManager[Result[T]], Generator[T, None, None]]（同步）
- 参数说明：
  - query: SQL 语句
  - values: 参数，可为序列或字典
  - stream: 是否使用流式结果（影响 Cursor 类型与 row_count 可用性）
  - result_class: 结果类型，tuple/dict 或自定义可构造类（以 **data 形式构造）
  - commit: 是否提交事务（True/False/None 表示跟随引擎默认）
- 返回值：
  - 可直接 await 得到 Result[T]
  - 可作为异步上下文管理器使用 async with execute(...) as result
  - 也可直接作为异步迭代器使用 async for item in execute(...)
- 异常：
  - 执行阶段由 Result 内部捕获 MySQLError 并记录于 result.error，不会在此处抛出
  - 若未连接而访问 pool 属性会抛 ConnectionError

章节来源
- [asmysql/v2/_engine.py:204-259](file://asmysql/v2/_engine.py#L204-L259)
- [asmysql/v3dev/_async_engine.py:194-249](file://asmysql/v3dev/_async_engine.py#L194-L249)
- [asmysql/v3dev/_sync_engine.py:184-239](file://asmysql/v3dev/_sync_engine.py#L184-L239)
- [asmysql/v2/_result.py:101-125](file://asmysql/v2/_result.py#L101-L125)
- [asmysql/v3dev/_async_result.py:101-125](file://asmysql/v3dev/_async_result.py#L101-L125)

#### execute_many(...)
- 作用：批量执行同一 SQL 的多组参数，返回 Result 对象
- 签名（异步/同步一致，仅返回类型不同）：
  - execute_many(query: str, values: Sequence[Sequence | dict], *, stream: bool | None = None, result_class: type[T] | None = None, commit: bool | None = None) -> Union[...]
- 参数与返回值语义同 execute，区别在于内部使用 executemany 执行
- 异常：同 execute

章节来源
- [asmysql/v2/_engine.py:261-316](file://asmysql/v2/_engine.py#L261-L316)
- [asmysql/v3dev/_async_engine.py:251-306](file://asmysql/v3dev/_async_engine.py#L251-L306)
- [asmysql/v3dev/_sync_engine.py:241-297](file://asmysql/v3dev/_sync_engine.py#L241-L297)

### 异步上下文管理器与可调用协议
- 异步上下文管理器：__aenter__/__aexit__ 委托至 connect/disconnect
- 可等待对象：__await__ 委托至 connect
- 可调用对象：__call__ 返回 connect 的结果
- 同步版本提供 __enter__/__exit__ 与 __call__

章节来源
- [asmysql/v2/_engine.py:124-128](file://asmysql/v2/_engine.py#L124-L128)
- [asmysql/v2/_engine.py:169-174](file://asmysql/v2/_engine.py#L169-L174)
- [asmysql/v3dev/_async_engine.py:114-118](file://asmysql/v3dev/_async_engine.py#L114-L118)
- [asmysql/v3dev/_async_engine.py:159-164](file://asmysql/v3dev/_async_engine.py#L159-L164)
- [asmysql/v3dev/_sync_engine.py:113-117](file://asmysql/v3dev/_sync_engine.py#L113-L117)
- [asmysql/v3dev/_sync_engine.py:157-158](file://asmysql/v3dev/_sync_engine.py#L157-L158)

### 使用示例（来自测试用例）
- 基本连接与断开
  - 参考路径：[tests/v2/v2_start.py:90-106](file://tests/v2/v2_start.py#L90-L106)、[tests/v3/test_async.py:91-107](file://tests/v3/test_async.py#L91-L107)
- 使用 execute 并逐行获取
  - 参考路径：[tests/v2/v2_start.py:13-25](file://tests/v2/v2_start.py#L13-L25)、[tests/v3/test_async.py:14-25](file://tests/v3/test_async.py#L14-L25)
- 使用 fetch_many/fetch_all
  - 参考路径：[tests/v2/v2_start.py:26-46](file://tests/v2/v2_start.py#L26-L46)、[tests/v3/test_async.py:27-47](file://tests/v3/test_async.py#L27-L47)
- 使用 iterate 异步生成器遍历
  - 参考路径：[tests/v2/v2_start.py:48-59](file://tests/v2/v2_start.py#L48-L59)、[tests/v3/test_async.py:49-59](file://tests/v3/test_async.py#L49-L59)
- 使用 async for 直接迭代 execute 返回的 Result
  - 参考路径：[tests/v2/v2_start.py:60-69](file://tests/v2/v2_start.py#L60-L69)、[tests/v3/test_async.py:61-70](file://tests/v3/test_async.py#L61-L70)
- 使用 async with 上下文管理 Result
  - 参考路径：[tests/v2/v2_start.py:71-82](file://tests/v2/v2_start.py#L71-L82)、[tests/v3/test_async.py:72-82](file://tests/v3/test_async.py#L72-L82)

章节来源
- [tests/v2/v2_start.py:1-107](file://tests/v2/v2_start.py#L1-L107)
- [tests/v3/test_async.py:1-108](file://tests/v3/test_async.py#L1-L108)

## 依赖关系分析
- Engine 依赖：
  - 异步：aiomysql.Pool/create_pool、pymysql.err.MySQLError、Result（异步）
  - 同步：自定义 Pool（_sync_pool）、pymysql.err.MySQLError、Result（同步）
- Result 依赖：
  - aiomysql.Cursor/DictCursor/SSCursor/SSDictCursor（异步）
  - pymysql.err.MySQLError
- 类型：
  - EngineStatus TypedDict 定义于 _types.py

```mermaid
classDiagram
class Engine {
+str url
+bool is_connected
+status : EngineStatus
+connect()
+disconnect()
+release_connections()
+execute(...)
+execute_many(...)
}
class Result {
+error
+row_count
+last_rowid
+row_number
+fetch_one()
+fetch_many()
+fetch_all()
+iterate()
+close()
}
class EngineStatus {
+address : str
+connected : bool
+pool_minsize : int?
+pool_maxsize : int?
+pool_size : int?
+pool_free : int?
+pool_used : int?
}
Engine --> Result : "返回"
Engine --> EngineStatus : "status 返回"
```

图表来源
- [asmysql/v2/_engine.py:37-317](file://asmysql/v2/_engine.py#L37-L317)
- [asmysql/v3dev/_async_engine.py:27-307](file://asmysql/v3dev/_async_engine.py#L27-L307)
- [asmysql/v3dev/_sync_engine.py:26-298](file://asmysql/v3dev/_sync_engine.py#L26-L298)
- [asmysql/v3dev/_types.py:4-12](file://asmysql/v3dev/_types.py#L4-L12)
- [asmysql/v2/_result.py:21-273](file://asmysql/v2/_result.py#L21-L273)
- [asmysql/v3dev/_async_result.py:21-273](file://asmysql/v3dev/_async_result.py#L21-L273)

章节来源
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v3dev/_async_result.py:1-273](file://asmysql/v3dev/_async_result.py#L1-L273)

## 性能与连接池调优
- 连接池大小
  - min_pool_size：初始最小连接数，适合冷启动后快速响应请求
  - max_pool_size：最大并发连接上限，需结合业务 QPS、DB 承载能力与网络延迟综合评估
- 连接回收
  - pool_recycle：空闲连接存活时间（秒），负值通常表示不回收；合理设置可避免长连接被远端主动关闭导致的异常
- 超时控制
  - connect_timeout：连接建立超时，防止阻塞；建议根据网络环境设置合理阈值
- 自动提交
  - auto_commit：默认 True；如需事务控制，可在 Result 层通过 commit 参数或上层事务管理进行覆盖
- 日志输出
  - echo_sql_log：打印 SQL 日志，便于调试；生产环境建议关闭以降低 I/O 开销
- 流式结果
  - stream：对大结果集建议使用流式模式，降低内存占用；注意此时 row_count 不可用
- 结果类型
  - result_class：tuple 性能更高；dict 可读性好；自定义类可通过 **data 构造，适合强类型建模

章节来源
- [asmysql/v2/_engine.py:41-53](file://asmysql/v2/_engine.py#L41-L53)
- [asmysql/v3dev/_async_engine.py:31-43](file://asmysql/v3dev/_async_engine.py#L31-L43)
- [asmysql/v3dev/_sync_engine.py:30-42](file://asmysql/v3dev/_sync_engine.py#L30-L42)
- [asmysql/v2/_result.py:153-165](file://asmysql/v2/_result.py#L153-L165)
- [asmysql/v3dev/_async_result.py:153-165](file://asmysql/v3dev/_async_result.py#L153-L165)

## 故障排查指南
- 连接失败
  - 现象：connect() 抛出 ConnectionError
  - 原因：底层 MySQLError 被转换；检查主机、端口、用户名、密码、网络连通性
  - 参考：[asmysql/v2/_engine.py:149-150](file://asmysql/v2/_engine.py#L149-L150)、[asmysql/v3dev/_async_engine.py:139-140](file://asmysql/v3dev/_async_engine.py#L139-L140)
- 未连接访问 pool
  - 现象：访问 engine.pool 抛出 ConnectionError
  - 处理：先调用 connect()
  - 参考：[asmysql/v2/_engine.py:198-201](file://asmysql/v2/_engine.py#L198-L201)、[asmysql/v3dev/_async_engine.py:188-191](file://asmysql/v3dev/_async_engine.py#L188-L191)
- SQL 执行错误
  - 现象：Result.error 非空，error_no/error_msg 可用
  - 处理：检查 SQL 语法、参数绑定、权限与表结构
  - 参考：[asmysql/v2/_result.py:119-124](file://asmysql/v2/_result.py#L119-L124)、[asmysql/v3dev/_async_result.py:119-124](file://asmysql/v3dev/_async_result.py#L119-L124)
- 资源泄漏
  - 现象：长时间运行后连接数增长
  - 处理：确保使用 async with / close() 或使用 Result 的自动关闭逻辑；必要时调用 release_connections()
  - 参考：[asmysql/v2/_result.py:65-79](file://asmysql/v2/_result.py#L65-L79)、[asmysql/v3dev/_async_result.py:65-79](file://asmysql/v3dev/_async_result.py#L65-L79)

章节来源
- [asmysql/v2/_engine.py:149-150](file://asmysql/v2/_engine.py#L149-L150)
- [asmysql/v3dev/_async_engine.py:139-140](file://asmysql/v3dev/_async_engine.py#L139-L140)
- [asmysql/v2/_engine.py:198-201](file://asmysql/v2/_engine.py#L198-L201)
- [asmysql/v3dev/_async_engine.py:188-191](file://asmysql/v3dev/_async_engine.py#L188-L191)
- [asmysql/v2/_result.py:119-124](file://asmysql/v2/_result.py#L119-L124)
- [asmysql/v3dev/_async_result.py:119-124](file://asmysql/v3dev/_async_result.py#L119-L124)
- [asmysql/v2/_result.py:65-79](file://asmysql/v2/_result.py#L65-L79)
- [asmysql/v3dev/_async_result.py:65-79](file://asmysql/v3dev/_async_result.py#L65-L79)

## 结论
Engine 提供了统一的数据库连接管理与 SQL 执行入口，配合 Result 实现了灵活的异步/同步编程模型、流式结果与强类型结果映射。通过合理的连接池参数与上下文管理，可获得稳定且高性能的数据访问体验。

## 附录：类型注解与泛型说明
- TypeVar T：用于 Result 泛型化，使 fetch_one/fetch_many/fetch_all/iterate 的返回类型与 result_class 保持一致
- overload：为 execute/execute_many 提供 tuple 与自定义类型的重载签名，提升静态类型推断体验
- TypedDict EngineStatus：结构化描述连接池状态字段，便于监控与诊断

章节来源
- [asmysql/v2/_engine.py:2-14](file://asmysql/v2/_engine.py#L2-L14)
- [asmysql/v3dev/_async_engine.py:2-13](file://asmysql/v3dev/_async_engine.py#L2-L13)
- [asmysql/v3dev/_sync_engine.py:2-12](file://asmysql/v3dev/_sync_engine.py#L2-L12)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)
- [asmysql/v2/_result.py:1-7](file://asmysql/v2/_result.py#L1-L7)
- [asmysql/v3dev/_async_result.py:1-7](file://asmysql/v3dev/_async_result.py#L1-L7)