# Engine 引擎类

<cite>
**本文引用的文件**   
- [asmysql/v2/_engine.py](file://asmysql/v2/_engine.py)
- [asmysql/v2/_result.py](file://asmysql/v2/_result.py)
- [asmysql/v2/__init__.py](file://asmysql/v2/__init__.py)
- [asmysql/v3dev/_async_engine.py](file://asmysql/v3dev/_async_engine.py)
- [asmysql/v3dev/_sync_engine.py](file://asmysql/v3dev/_sync_engine.py)
- [asmysql/v3dev/_async_result.py](file://asmysql/v3dev/_async_result.py)
- [asmysql/v3dev/_sync_result.py](file://asmysql/v3dev/_sync_result.py)
- [asmysql/v3dev/_types.py](file://asmysql/v3dev/_types.py)
- [asmysql/v2/_error.py](file://asmysql/v2/_error.py)
- [mkdocs/v2/docs/zh/connection.md](file://mkdocs/v2/docs/zh/connection.md)
- [mkdocs/v2/docs/zh/query.md](file://mkdocs/v2/docs/zh/query.md)
- [tests/v3/test_async.py](file://tests/v3/test_async.py)
- [tests/v3/test_sync.py](file://tests/v3/test_sync.py)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构总览](#架构总览)
5. [详细组件分析](#详细组件分析)
6. [依赖关系分析](#依赖关系分析)
7. [性能考量](#性能考量)
8. [故障排查指南](#故障排查指南)
9. [结论](#结论)
10. [附录：使用示例与最佳实践](#附录使用示例与最佳实践)

## 简介
本文件面向有一定经验的开发者，深入解析 asmysql 中 Engine 引擎类的核心功能与实现细节。重点覆盖：
- 连接池管理机制（创建、复用、释放、生命周期）
- URL 连接字符串解析与配置参数处理
- 异步上下文管理器模式（__aenter__/__aexit__）
- execute() 与 execute_many() 的执行流程、参数处理与结果返回机制
- 流式查询与大结果集处理策略
- 连接状态监控、错误处理与性能优化技巧
- 完整使用场景示例（基本连接、批量操作、事务管理等）

## 项目结构
仓库包含 v2 与 v3dev 两套实现：
- v2：基于 aiomysql 的异步封装，Engine 与 Result 位于同一模块
- v3dev：进一步拆分异步与同步版本，分别提供 AsyncEngine/SyncEngine 与对应 Result 类型

```mermaid
graph TB
subgraph "v2"
V2_Engine["Engine(异步)"]
V2_Result["Result(异步)"]
V2_Init["v2.__init__"]
end
subgraph "v3dev"
V3_AE["AsyncEngine(异步)"]
V3_SE["SyncEngine(同步)"]
V3_AR["AsyncResult(异步)"]
V3_SR["SyncResult(同步)"]
V3_Types["EngineStatus 类型定义"]
end
V2_Init --> V2_Engine
V2_Engine --> V2_Result
V3_AE --> V3_AR
V3_SE --> V3_SR
V3_AR --> V3_Types
V3_SR --> V3_Types
```

图示来源
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v2/__init__.py:1-15](file://asmysql/v2/__init__.py#L1-L15)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v3dev/_async_result.py:1-273](file://asmysql/v3dev/_async_result.py#L1-L273)
- [asmysql/v3dev/_sync_result.py:1-268](file://asmysql/v3dev/_sync_result.py#L1-L268)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)

章节来源
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v2/__init__.py:1-15](file://asmysql/v2/__init__.py#L1-L15)

## 核心组件
- Engine（异步/同步）：负责连接池管理、URL 解析、执行入口（execute/execute_many）、状态监控与资源清理
- Result（异步/同步）：封装游标生命周期、SQL 执行、结果获取（fetch_one/many/all/iterate）、自动关闭与错误记录
- 类型与错误工具：EngineStatus TypedDict、err_msg 统一错误信息格式化

章节来源
- [asmysql/v2/_engine.py:37-317](file://asmysql/v2/_engine.py#L37-L317)
- [asmysql/v2/_result.py:21-273](file://asmysql/v2/_result.py#L21-L273)
- [asmysql/v3dev/_async_engine.py:27-307](file://asmysql/v3dev/_async_engine.py#L27-L307)
- [asmysql/v3dev/_sync_engine.py:26-298](file://asmysql/v3dev/_sync_engine.py#L26-L298)
- [asmysql/v3dev/_async_result.py:21-273](file://asmysql/v3dev/_async_result.py#L21-L273)
- [asmysql/v3dev/_sync_result.py:23-268](file://asmysql/v3dev/_sync_result.py#L23-L268)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)
- [asmysql/v2/_error.py:1-7](file://asmysql/v2/_error.py#L1-L7)

## 架构总览
Engine 作为门面，将底层连接池与游标执行逻辑抽象为统一的 API；Result 负责单次 SQL 的生命周期管理与结果消费。

```mermaid
classDiagram
class Engine {
+host : str
+port : int
+user : str
+password : str
+charset : str
+min_pool_size : int
+max_pool_size : int
+pool_recycle : float
+connect_timeout : int
+auto_commit : bool
+echo_sql_log : bool
+stream : bool
+result_class : type
+url : str
+connect()
+disconnect()
+release_connections()
+status
+is_connected
+execute(query, values, stream, result_class, commit)
+execute_many(query, values, stream, result_class, commit)
}
class Result {
+query : str
+values
+stream : bool
+commit : bool
+_result_class : type
+close()
+fetch_one(close)
+fetch_many(size, close)
+fetch_all()
+iterate()
+error_no
+error_msg
+row_count
+last_rowid
+row_number
}
Engine --> Result : "创建并返回"
```

图示来源
- [asmysql/v2/_engine.py:37-317](file://asmysql/v2/_engine.py#L37-L317)
- [asmysql/v2/_result.py:21-273](file://asmysql/v2/_result.py#L21-L273)
- [asmysql/v3dev/_async_engine.py:27-307](file://asmysql/v3dev/_async_engine.py#L27-L307)
- [asmysql/v3dev/_async_result.py:21-273](file://asmysql/v3dev/_async_result.py#L21-L273)

## 详细组件分析

### 连接池管理机制
- 连接创建
  - connect() 在首次调用时通过 create_pool 初始化连接池，传入 host/port/user/password/charset/minsize/maxsize/pool_recycle/connect_timeout/autocommit/echo 等参数
  - 捕获底层 MySQLError 并包装为 ConnectionError，便于上层统一处理
- 连接复用
  - Result 在执行时从 pool.acquire() 获取连接，创建游标执行 SQL，结束后 release 归还连接
- 连接释放与生命周期
  - disconnect() 安全关闭连接池并等待所有连接回收
  - release_connections() 清空空闲连接
  - __del__/close() 兜底释放连接，避免泄漏
- 状态监控
  - status 属性返回 address/connected/pool_minsize/pool_maxsize/pool_size/pool_free/pool_used 等指标

```mermaid
sequenceDiagram
participant App as "应用"
participant Eng as "Engine"
participant Pool as "aiomysql.Pool"
participant Conn as "Connection"
participant Cur as "Cursor"
participant DB as "MySQL"
App->>Eng : "connect()"
Eng->>Pool : "create_pool(...)"
Pool-->>Eng : "Pool实例"
App->>Eng : "execute(query, values, ...)"
Eng-->>App : "Result对象"
App->>Result : "__call__() / await"
Result->>Pool : "acquire()"
Pool-->>Result : "Conn"
Result->>Conn : "cursor(CursorClass)"
Result->>Cur : "execute/executemany"
Cur->>DB : "发送SQL"
DB-->>Cur : "返回结果/影响行数"
alt "需要提交"
Result->>Conn : "commit()"
end
Result->>Cur : "close()"
Result->>Pool : "release(Conn)"
App->>Eng : "disconnect()"
Eng->>Pool : "close()/wait_closed()"
```

图示来源
- [asmysql/v2/_engine.py:131-183](file://asmysql/v2/_engine.py#L131-L183)
- [asmysql/v2/_result.py:101-125](file://asmysql/v2/_result.py#L101-L125)
- [asmysql/v3dev/_async_engine.py:121-177](file://asmysql/v3dev/_async_engine.py#L121-L177)
- [asmysql/v3dev/_async_result.py:101-125](file://asmysql/v3dev/_async_result.py#L101-L125)

章节来源
- [asmysql/v2/_engine.py:131-183](file://asmysql/v2/_engine.py#L131-L183)
- [asmysql/v2/_result.py:101-125](file://asmysql/v2/_result.py#L101-L125)
- [asmysql/v3dev/_async_engine.py:121-177](file://asmysql/v3dev/_async_engine.py#L121-L177)
- [asmysql/v3dev/_async_result.py:101-125](file://asmysql/v3dev/_async_result.py#L101-L125)

### URL 连接字符串解析与配置参数处理
- 支持格式：mysql://user:password@host:port/?key=value&...
- 解析逻辑
  - 校验 scheme 必须为 mysql
  - 从 hostname/username/password/port 提取基础信息
  - 从 query 参数解析 charset、min_pool_size、max_pool_size、pool_recycle、connect_timeout、auto_commit、echo_sql_log
  - 对数值型参数进行安全的类型转换，避免 None 传入 int/float
- 优先级：URL 中的值优先于显式关键字参数；未提供的则回退到默认值

```mermaid
flowchart TD
Start(["开始"]) --> Parse["解析 URL"]
Parse --> Scheme{"scheme == 'mysql' ?"}
Scheme -- "否" --> Err["抛出 ValueError"]
Scheme -- "是" --> Extract["提取 host/port/user/password"]
Extract --> Query["解析 query 参数"]
Query --> Convert["类型转换与合并"]
Convert --> SetAttrs["设置实例属性"]
SetAttrs --> End(["结束"])
```

图示来源
- [asmysql/v2/_engine.py:77-111](file://asmysql/v2/_engine.py#L77-L111)
- [asmysql/v3dev/_async_engine.py:67-101](file://asmysql/v3dev/_async_engine.py#L67-L101)
- [asmysql/v3dev/_sync_engine.py:66-100](file://asmysql/v3dev/_sync_engine.py#L66-L100)

章节来源
- [asmysql/v2/_engine.py:77-111](file://asmysql/v2/_engine.py#L77-L111)
- [asmysql/v3dev/_async_engine.py:67-101](file://asmysql/v3dev/_async_engine.py#L67-L101)
- [asmysql/v3dev/_sync_engine.py:66-100](file://asmysql/v3dev/_sync_engine.py#L66-L100)
- [mkdocs/v2/docs/zh/connection.md:1-131](file://mkdocs/v2/docs/zh/connection.md#L1-L131)

### 异步上下文管理器模式（__aenter__/__aexit__）
- Engine 层面
  - __aenter__ 返回 connect() 的结果，__aexit__ 调用 disconnect()
  - 同时支持 await engine 与 async with engine 两种用法
- Result 层面
  - __aenter__ 触发执行（__call__），__aexit__ 确保关闭游标并释放连接
  - 支持 async for item in result 直接迭代

```mermaid
sequenceDiagram
participant App as "应用"
participant Eng as "Engine"
participant Res as "Result"
App->>Eng : "async with engine : "
Eng->>Eng : "__aenter__() -> connect()"
App->>Res : "async with engine.execute(...) as result : "
Res->>Res : "__aenter__() -> __call__()"
App->>Res : "读取数据/迭代"
App-->>Res : "退出上下文"
Res->>Res : "__aexit__() -> close()"
App-->>Eng : "退出上下文"
Eng->>Eng : "__aexit__() -> disconnect()"
```

图示来源
- [asmysql/v2/_engine.py:124-128](file://asmysql/v2/_engine.py#L124-L128)
- [asmysql/v2/_result.py:71-79](file://asmysql/v2/_result.py#L71-L79)
- [asmysql/v3dev/_async_engine.py:114-118](file://asmysql/v3dev/_async_engine.py#L114-L118)
- [asmysql/v3dev/_async_result.py:71-79](file://asmysql/v3dev/_async_result.py#L71-L79)

章节来源
- [asmysql/v2/_engine.py:124-128](file://asmysql/v2/_engine.py#L124-L128)
- [asmysql/v2/_result.py:71-79](file://asmysql/v2/_result.py#L71-L79)
- [asmysql/v3dev/_async_engine.py:114-118](file://asmysql/v3dev/_async_engine.py#L114-L118)
- [asmysql/v3dev/_async_result.py:71-79](file://asmysql/v3dev/_async_result.py#L71-L79)

### execute() 与 execute_many() 执行流程
- 入口方法
  - execute(query, values=None, stream=None, result_class=None, commit=None)
  - execute_many(query, values, ...)
  - 两者均返回 Result 对象，内部仅差异在于是否标记 execute_many=True
- 参数处理
  - stream/result_class 若未传入，则回退至 Engine 实例级别默认值
  - commit 控制是否在单条语句后提交（受 auto_commit 与具体驱动行为影响）
- 执行路径
  - Result.__call__() 选择合适 Cursor 类型（普通/字典/流式）
  - 从连接池获取连接，创建游标，执行 SQL，必要时提交
  - 异常捕获并记录 error，保证连接与游标正确释放

```mermaid
flowchart TD
A["调用 execute/execute_many"] --> B["确定 stream/result_class"]
B --> C["构造 Result 对象"]
C --> D["await/with 触发执行"]
D --> E{"execute_many?"}
E -- "是" --> F["executemany(query, values)"]
E -- "否" --> G["execute(query, values)"]
F --> H["可选 commit()"]
G --> H
H --> I["返回 Result 供 fetch*/iterate 使用"]
```

图示来源
- [asmysql/v2/_engine.py:227-316](file://asmysql/v2/_engine.py#L227-L316)
- [asmysql/v2/_result.py:101-125](file://asmysql/v2/_result.py#L101-L125)
- [asmysql/v3dev/_async_engine.py:217-306](file://asmysql/v3dev/_async_engine.py#L217-L306)
- [asmysql/v3dev/_async_result.py:101-125](file://asmysql/v3dev/_async_result.py#L101-L125)

章节来源
- [asmysql/v2/_engine.py:227-316](file://asmysql/v2/_engine.py#L227-L316)
- [asmysql/v2/_result.py:101-125](file://asmysql/v2/_result.py#L101-L125)
- [asmysql/v3dev/_async_engine.py:217-306](file://asmysql/v3dev/_async_engine.py#L217-L306)
- [asmysql/v3dev/_async_result.py:101-125](file://asmysql/v3dev/_async_result.py#L101-L125)

### 流式查询与大结果集处理策略
- 流式游标选择
  - tuple + stream -> SSCursor
  - dict + stream -> SSDictCursor
  - 非流式 -> Cursor/DictCursor
- 大结果集处理
  - 使用 stream=True 或 iterate()/async for 逐行消费，避免一次性加载全部数据
  - row_count 在流式模式下不可用（返回 None）
- 适用场景
  - 导出、ETL、报表生成等大数据量处理

```mermaid
flowchart TD
S["开始"] --> Opt{"stream 启用?"}
Opt -- "否" --> NC["使用普通游标<br/>可获取 row_count"]
Opt -- "是" --> SC["使用流式游标<br/>不支持 row_count"]
NC --> Fetch["fetch_one/many/all"]
SC --> Iterate["iterate()/async for 逐行"]
Fetch --> End(["结束"])
Iterate --> End
```

图示来源
- [asmysql/v2/_result.py:10-18](file://asmysql/v2/_result.py#L10-L18)
- [asmysql/v2/_result.py:153-165](file://asmysql/v2/_result.py#L153-L165)
- [asmysql/v3dev/_async_result.py:10-18](file://asmysql/v3dev/_async_result.py#L10-L18)
- [asmysql/v3dev/_async_result.py:153-165](file://asmysql/v3dev/_async_result.py#L153-L165)

章节来源
- [asmysql/v2/_result.py:10-18](file://asmysql/v2/_result.py#L10-L18)
- [asmysql/v2/_result.py:153-165](file://asmysql/v2/_result.py#L153-L165)
- [asmysql/v3dev/_async_result.py:10-18](file://asmysql/v3dev/_async_result.py#L10-L18)
- [asmysql/v3dev/_async_result.py:153-165](file://asmysql/v3dev/_async_result.py#L153-L165)

### 连接状态监控与错误处理
- 状态监控
  - is_connected 快速判断是否已建立连接池
  - status 返回地址、连接池容量与使用率等关键指标
- 错误处理
  - 连接阶段：MySQLError 被转换为 ConnectionError，附带 err_msg 格式化后的消息
  - 执行阶段：Result.error/error_no/error_msg 暴露错误详情，不影响后续安全关闭
- 日志与调试
  - echo_sql_log 控制底层 echo 输出，便于定位问题

章节来源
- [asmysql/v2/_engine.py:155-166](file://asmysql/v2/_engine.py#L155-L166)
- [asmysql/v2/_engine.py:149-151](file://asmysql/v2/_engine.py#L149-L151)
- [asmysql/v2/_result.py:133-151](file://asmysql/v2/_result.py#L133-L151)
- [asmysql/v2/_error.py:1-7](file://asmysql/v2/_error.py#L1-L7)
- [mkdocs/v2/docs/zh/connection.md:48-65](file://mkdocs/v2/docs/zh/connection.md#L48-L65)

### 性能优化技巧
- 合理设置 min_pool_size/max_pool_size 以匹配并发度
- 使用 pool_recycle 定期回收空闲 TCP 连接，避免中间代理断开
- 大数据集务必开启 stream=True 并使用 iterate()/async for
- 使用 result_class=dict 提升可读性，但注意字典开销略高于元组
- 利用 status 监控 pool_size/pool_free/pool_used，识别瓶颈与扩容点

[本节为通用指导，不直接分析具体文件]

## 依赖关系分析
- 外部依赖
  - aiomysql：异步连接池与游标
  - pymysql.err.MySQLError：数据库异常基类
- 内部依赖
  - Engine 依赖 Result 完成 SQL 执行与结果消费
  - v3dev 引入 _types.EngineStatus 用于状态 TypedDict 定义
  - v2 与 v3dev 的 Result 实现高度一致，区别在于同步/异步接口

```mermaid
graph LR
Engine["Engine"] --> Result["Result"]
Engine --> aiomysql["aiomysql.Pool/create_pool"]
Result --> aiomysql["Cursor/SSCursor/DictCursor/SSDictCursor"]
Engine --> Error["pymysql.err.MySQLError"]
Result --> Error
Types["_types.EngineStatus"] --> Engine
```

图示来源
- [asmysql/v2/_engine.py:17-21](file://asmysql/v2/_engine.py#L17-L21)
- [asmysql/v2/_result.py:1-6](file://asmysql/v2/_result.py#L1-L6)
- [asmysql/v3dev/_async_engine.py:16-21](file://asmysql/v3dev/_async_engine.py#L16-L21)
- [asmysql/v3dev/_async_result.py:1-6](file://asmysql/v3dev/_async_result.py#L1-L6)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)

章节来源
- [asmysql/v2/_engine.py:17-21](file://asmysql/v2/_engine.py#L17-L21)
- [asmysql/v2/_result.py:1-6](file://asmysql/v2/_result.py#L1-L6)
- [asmysql/v3dev/_async_engine.py:16-21](file://asmysql/v3dev/_async_engine.py#L16-L21)
- [asmysql/v3dev/_async_result.py:1-6](file://asmysql/v3dev/_async_result.py#L1-L6)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)

## 性能考量
- 连接池规模应与业务 QPS 和延迟目标相匹配，避免过大导致资源浪费或过小造成排队
- 流式查询能显著降低内存占用，但会延长端到端耗时，需结合批处理策略平衡吞吐
- 使用 result_class=dict 提升开发效率，但在高吞吐场景下建议评估元组带来的性能收益
- 通过 status 监控连接池使用率，动态调整 min/max 大小或增加副本实例

[本节为通用指导，不直接分析具体文件]

## 故障排查指南
- 连接失败
  - 检查 URL 格式与权限，确认 host/port/user/password 正确
  - 查看 ConnectionError 的 err_msg 内容，定位底层 MySQLError
- 执行报错
  - 通过 result.error/error_no/error_msg 获取错误码与信息
  - 确认参数化查询是否正确传参，避免 SQL 注入风险
- 资源泄漏
  - 确保使用 async with/engine.execute(...) 或手动调用 close()
  - 观察 status 的 pool_free/pool_used 变化，排查未释放的连接
- 性能问题
  - 针对大结果集启用 stream=True 并使用 iterate()/async for
  - 调整连接池参数与 echo_sql_log 辅助诊断

章节来源
- [asmysql/v2/_engine.py:149-151](file://asmysql/v2/_engine.py#L149-L151)
- [asmysql/v2/_result.py:133-151](file://asmysql/v2/_result.py#L133-L151)
- [asmysql/v2/_result.py:65-79](file://asmysql/v2/_result.py#L65-L79)
- [mkdocs/v2/docs/zh/connection.md:103-131](file://mkdocs/v2/docs/zh/connection.md#L103-L131)

## 结论
Engine 提供了简洁一致的数据库访问入口，结合 Result 实现了完整的 SQL 执行与结果消费生命周期。其设计在易用性与性能之间取得良好平衡：通过连接池复用、流式查询、上下文管理器与完善的错误处理，满足从简单脚本到高并发服务的多样化需求。

[本节为总结性内容，不直接分析具体文件]

## 附录：使用示例与最佳实践
以下为常见使用场景的路径参考，便于快速定位示例代码：
- 基本连接与查询
  - [mkdocs/v2/docs/zh/examples.md:25-45](file://mkdocs/v2/docs/zh/examples.md#L25-L45)
  - [mkdocs/v2/docs/zh/query.md:5-39](file://mkdocs/v2/docs/zh/query.md#L5-L39)
- 上下文管理器与直接迭代
  - [mkdocs/v2/docs/zh/query.md:17-39](file://mkdocs/v2/docs/zh/query.md#L17-L39)
  - [tests/v3/test_async.py:84-101](file://tests/v3/test_async.py#L84-L101)
- 流式查询与大结果集
  - [mkdocs/v2/docs/zh/examples.md:406-469](file://mkdocs/v2/docs/zh/examples.md#L406-L469)
  - [mkdocs/v2/docs/zh/query.md:77-91](file://mkdocs/v2/docs/zh/query.md#L77-L91)
- 批量操作（insert/update/delete）
  - [mkdocs/v2/docs/zh/examples.md:471-535](file://mkdocs/v2/docs/zh/examples.md#L471-L535)
- 自定义模型（Pydantic/普通类）
  - [mkdocs/v2/docs/zh/examples.md:537-617](file://mkdocs/v2/docs/zh/examples.md#L537-L617)
- 错误处理
  - [mkdocs/v2/docs/zh/examples.md:619-686](file://mkdocs/v2/docs/zh/examples.md#L619-L686)
- 事务管理（手动提交/回滚思路）
  - [mkdocs/v2/docs/zh/examples.md:356-404](file://mkdocs/v2/docs/zh/examples.md#L356-L404)
- 同步版本示例
  - [tests/v3/test_sync.py:109-131](file://tests/v3/test_sync.py#L109-L131)

章节来源
- [mkdocs/v2/docs/zh/examples.md:25-45](file://mkdocs/v2/docs/zh/examples.md#L25-L45)
- [mkdocs/v2/docs/zh/query.md:5-39](file://mkdocs/v2/docs/zh/query.md#L5-L39)
- [mkdocs/v2/docs/zh/query.md:17-39](file://mkdocs/v2/docs/zh/query.md#L17-L39)
- [tests/v3/test_async.py:84-101](file://tests/v3/test_async.py#L84-L101)
- [mkdocs/v2/docs/zh/examples.md:406-469](file://mkdocs/v2/docs/zh/examples.md#L406-L469)
- [mkdocs/v2/docs/zh/query.md:77-91](file://mkdocs/v2/docs/zh/query.md#L77-L91)
- [mkdocs/v2/docs/zh/examples.md:471-535](file://mkdocs/v2/docs/zh/examples.md#L471-L535)
- [mkdocs/v2/docs/zh/examples.md:537-617](file://mkdocs/v2/docs/zh/examples.md#L537-L617)
- [mkdocs/v2/docs/zh/examples.md:619-686](file://mkdocs/v2/docs/zh/examples.md#L619-L686)
- [mkdocs/v2/docs/zh/examples.md:356-404](file://mkdocs/v2/docs/zh/examples.md#L356-L404)
- [tests/v3/test_sync.py:109-131](file://tests/v3/test_sync.py#L109-L131)