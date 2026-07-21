# AsMysql 基类 API

<cite>
**本文引用的文件**   
- [asmysql/__init__.py](file://asmysql/__init__.py)
- [asmysql/v2/_asmysql.py](file://asmysql/v2/_asmysql.py)
- [asmysql/v2/_engine.py](file://asmysql/v2/_engine.py)
- [asmysql/v2/_result.py](file://asmysql/v2/_result.py)
- [asmysql/v3dev/_asmysql.py](file://asmysql/v3dev/_asmysql.py)
- [asmysql/v3dev/_async_engine.py](file://asmysql/v3dev/_async_engine.py)
- [asmysql/v3dev/_sync_engine.py](file://asmysql/v3dev/_sync_engine.py)
- [asmysql/v3dev/_types.py](file://asmysql/v3dev/_types.py)
- [tests/v2/v2_start.py](file://tests/v2/v2_start.py)
- [pytest/v2/test_asmysql.py](file://pytest/v2/test_asmysql.py)
- [mkdocs/v2/docs/zh/business-logic.md](file://mkdocs/v2/docs/zh/business-logic.md)
- [mkdocs/v2/docs/zh/best-practices.md](file://mkdocs/v2/docs/zh/best-practices.md)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构总览](#架构总览)
5. [详细组件分析](#详细组件分析)
6. [依赖关系分析](#依赖关系分析)
7. [性能与资源管理](#性能与资源管理)
8. [故障排查指南](#故障排查指南)
9. [结论](#结论)
10. [附录：类型注解与泛型使用](#附录类型注解与泛型使用)

## 简介
本文件面向基于 asmysql 开发业务逻辑的开发者，系统化梳理 AsMysql 基类的 API、继承关系、扩展点以及与 Engine 的关系。文档重点包括：
- AsMysql 在 v2 与 v3dev 中的差异与演进
- client 属性的职责边界与类型约束
- 结果集 Result 的异步/同步迭代与流式处理
- 业务类设计最佳实践与代码组织模式
- 调试信息输出与错误处理建议
- 完整的类型注解说明与泛型用法示例路径

## 项目结构
仓库按版本与功能分层组织，AsMysql 基类主要位于 v2 与 v3dev 两个分支：
- v2：稳定版，提供异步 Engine 与 AsMysql 基类
- v3dev：开发版，引入 Generic[EngineType] 以支持同步/异步 Engine 的统一抽象

```mermaid
graph TB
subgraph "v2"
A["asmysql/v2/_asmysql.py<br/>AsMysql 基类"]
B["asmysql/v2/_engine.py<br/>Engine(异步)"]
C["asmysql/v2/_result.py<br/>Result(异步)"]
end
subgraph "v3dev"
D["asmysql/v3dev/_asmysql.py<br/>AsMysql(Generic[EngineType])"]
E["asmysql/v3dev/_async_engine.py<br/>Engine(异步)"]
F["asmysql/v3dev/_sync_engine.py<br/>Engine(同步)"]
G["asmysql/v3dev/_types.py<br/>EngineStatus 类型定义"]
end
H["asmysql/__init__.py<br/>对外导出 v2 默认实现"]
I["tests/v2/v2_start.py<br/>使用示例"]
J["pytest/v2/test_asmysql.py<br/>测试用例"]
K["mkdocs/v2/docs/zh/business-logic.md<br/>业务逻辑文档"]
L["mkdocs/v2/docs/zh/best-practices.md<br/>最佳实践文档"]
H --> A
A --> B
B --> C
D --> E
D --> F
E --> G
F --> G
I --> A
J --> A
K --> A
L --> A
```

图示来源
- [asmysql/__init__.py:1-16](file://asmysql/__init__.py#L1-L16)
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v3dev/_asmysql.py:1-30](file://asmysql/v3dev/_asmysql.py#L1-L30)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)

章节来源
- [asmysql/__init__.py:1-16](file://asmysql/__init__.py#L1-L16)
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v3dev/_asmysql.py:1-30](file://asmysql/v3dev/_asmysql.py#L1-L30)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)

## 核心组件
- AsMysql（v2）
  - 职责：为业务逻辑提供统一入口，持有 Engine 实例并通过 client 属性暴露执行能力
  - 关键成员：
    - __init__(engine: Engine)：接收并持有 Engine
    - client：只读属性，返回内部 Engine 实例
    - __repr__/__str__：便于调试输出
- AsMysql（v3dev）
  - 职责：在 v2 基础上引入泛型，使 client 的类型可精确到具体 Engine 实现（同步或异步）
  - 关键成员：
    - __init__(engine: EngineType)：EngineType 为 TypeVar，限定为 SyncEngine 或 AsyncEngine
    - client：返回对应 EngineType 实例
- Engine（v2/v3dev 异步）
  - 职责：封装 aiomysql 连接池，提供 connect/disconnect/status/is_connected/pool 等能力
  - 关键方法：
    - execute(query, values=None, *, stream=None, result_class=tuple, commit=None) -> Result[T]
    - execute_many(query, values, *, stream=None, result_class=tuple, commit=None) -> Result[T]
    - 上下文管理与 awaitable/callable 支持
- Engine（v3dev 同步）
  - 职责：封装 pymysql 连接池，接口风格与异步一致
- Result（v2/v3dev）
  - 职责：封装游标生命周期、错误捕获、数据获取与迭代
  - 关键能力：
    - error/error_no/error_msg：错误状态
    - row_count/last_rowid/row_number：元信息
    - fetch_one/fetch_many/fetch_all：数据读取
    - iterate()/async for：流式/非流式迭代
    - 自动关闭与上下文管理

章节来源
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [asmysql/v3dev/_asmysql.py:1-30](file://asmysql/v3dev/_asmysql.py#L1-L30)
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)

## 架构总览
AsMysql 作为业务层基类，不直接操作底层驱动，而是通过 client 访问 Engine。Engine 负责连接池与执行，Result 负责结果集与游标生命周期管理。

```mermaid
classDiagram
class AsMysql_v2 {
+__init__(engine : Engine)
+client : Engine
+__repr__()
+__str__()
}
class AsMysql_v3dev {
+__init__(engine : EngineType)
+client : EngineType
+__repr__()
+__str__()
}
class Engine_Async_v2 {
+connect()
+disconnect()
+execute(...)
+execute_many(...)
+status
+is_connected
+pool
}
class Engine_Async_v3dev {
+connect()
+disconnect()
+execute(...)
+execute_many(...)
+status
+is_connected
+pool
}
class Engine_Sync_v3dev {
+connect()
+disconnect()
+execute(...)
+execute_many(...)
+status
+is_connected
+pool
}
class Result_Async {
+error/error_no/error_msg
+fetch_one/close
+fetch_many/close
+fetch_all()
+iterate()
+__aiter__/__anext__
}
class Result_Sync {
+error/error_no/error_msg
+fetch_one/close
+fetch_many/close
+fetch_all()
+iterate()
+__iter__/__next__
}
AsMysql_v2 --> Engine_Async_v2 : "client"
AsMysql_v3dev --> Engine_Async_v3dev : "client"
AsMysql_v3dev --> Engine_Sync_v3dev : "client"
Engine_Async_v2 --> Result_Async : "execute/execute_many"
Engine_Async_v3dev --> Result_Async : "execute/execute_many"
Engine_Sync_v3dev --> Result_Sync : "execute/execute_many"
```

图示来源
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [asmysql/v3dev/_asmysql.py:1-30](file://asmysql/v3dev/_asmysql.py#L1-L30)
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)

## 详细组件分析

### AsMysql 基类（v2）
- 继承关系
  - 无显式父类，作为业务逻辑基类被用户自定义类继承
- 构造与属性
  - __init__(engine: Engine)：接收 Engine 实例并保存
  - client：只读属性，返回内部 Engine，用于执行 SQL
- 调试输出
  - __repr__/__str__：包含类名与 Engine.url，便于日志记录
- 扩展点
  - 子类可在其中定义业务方法，通过 self.client 调用 Engine.execute/execute_many
- 典型用法参考
  - 参见测试与示例中对 self.client.execute 的使用

```mermaid
sequenceDiagram
participant Biz as "业务类(继承AsMysql)"
participant Base as "AsMysql(v2)"
participant Eng as "Engine(异步)"
participant Res as "Result(异步)"
Biz->>Base : 调用业务方法
Biz->>Base : self.client.execute(...)
Base-->>Biz : 返回 Result 对象
Biz->>Res : 检查 error / 调用 fetch_* 或 iterate()
Res-->>Biz : 返回数据或空
```

图示来源
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [asmysql/v2/_engine.py:204-317](file://asmysql/v2/_engine.py#L204-L317)
- [asmysql/v2/_result.py:101-273](file://asmysql/v2/_result.py#L101-L273)

章节来源
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [pytest/v2/test_asmysql.py:34-48](file://pytest/v2/test_asmysql.py#L34-L48)
- [tests/v2/v2_start.py:12-88](file://tests/v2/v2_start.py#L12-L88)

### AsMysql 基类（v3dev，泛型）
- 泛型设计
  - AsMysql(Generic[EngineType])，EngineType = TypeVar("EngineType", SyncEngine, AsyncEngine)
  - 使得 client 的类型可静态推导为具体的 Engine 实现，提升类型安全
- 其他行为与 v2 一致

章节来源
- [asmysql/v3dev/_asmysql.py:1-30](file://asmysql/v3dev/_asmysql.py#L1-L30)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)

### Engine（异步，v2 与 v3dev）
- 连接管理
  - connect()/disconnect()：建立/释放连接池
  - is_connected：是否已连接
  - status：返回连接池状态字典（含地址、连接数、空闲/占用等）
- 执行接口
  - execute(...)/execute_many(...)：返回 Result[T]，支持 context manager 与 async for 直接迭代
  - 参数：query, values, stream, result_class, commit
- URL 解析
  - 支持 mysql://user:pass@host:port/?charset=... 及 pool/recycle/timeout/auto_commit/echo_sql_log 等查询参数
- 上下文与可调用
  - 支持 async with engine: 与 await engine() 两种便捷用法

```mermaid
flowchart TD
Start(["调用 execute/execute_many"]) --> BuildResult["构建 Result 对象<br/>携带 query/values/stream/result_class/commit"]
BuildResult --> UseMode{"使用模式"}
UseMode --> |await result| AwaitExec["等待执行完成"]
UseMode --> |async with result| WithCtx["进入上下文管理器"]
UseMode --> |async for item in execute(...)| DirectIter["直接迭代结果"]
AwaitExec --> FetchOps["fetch_one/fetch_many/fetch_all/iterate"]
WithCtx --> FetchOps
DirectIter --> FetchOps
FetchOps --> End(["结束/释放资源"])
```

图示来源
- [asmysql/v2/_engine.py:204-317](file://asmysql/v2/_engine.py#L204-L317)
- [asmysql/v3dev/_async_engine.py:194-307](file://asmysql/v3dev/_async_engine.py#L194-L307)
- [asmysql/v2/_result.py:101-273](file://asmysql/v2/_result.py#L101-L273)

章节来源
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)

### Engine（同步，v3dev）
- 与异步 Engine 一致的接口风格，但基于 pymysql 与同步 Pool
- 同样支持 execute/execute_many 与上下文管理、迭代器协议

章节来源
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)

### Result（异步，v2）
- 生命周期
  - 支持 __aenter__/__aexit__ 与 __aiter__/__anext__，可配合 async with 与 async for
  - 自动关闭：在 fetch_one/fetch_many 返回 None 时或迭代结束时自动 close
- 错误处理
  - error/error_no/error_msg：统一错误状态与消息
- 数据获取
  - fetch_one/close：单条
  - fetch_many/close：批量
  - fetch_all：全部
  - iterate()：异步生成器逐行产出
- 结果类型
  - result_class 支持 tuple/dict/自定义模型（如 Pydantic BaseModel），由引擎侧传入 Result 构造

```mermaid
sequenceDiagram
participant Client as "调用方"
participant Res as "Result(异步)"
participant Cur as "Cursor"
participant Pool as "连接池"
Client->>Res : __call__()/__aenter__()/__aiter__()
Res->>Pool : acquire()
Pool-->>Res : conn
Res->>Cur : cursor(cursor_class)
Res->>Cur : execute/executemany
alt 成功
Res-->>Client : 返回 Result
Client->>Res : fetch_one/fetch_many/fetch_all/iterate
Res->>Cur : 读取数据
Res->>Pool : release(conn)
else 异常
Res->>Cur : close()
Res->>Pool : release(conn)
Res-->>Client : 设置 error/error_no/error_msg
end
```

图示来源
- [asmysql/v2/_result.py:101-273](file://asmysql/v2/_result.py#L101-L273)

章节来源
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)

### Result（同步，v3dev）
- 与异步版本一致的接口风格，基于 pymysql 的 Cursor/SSCursor/DictCursor/SSDictCursor
- 支持 for item in result 与 with result: 语法

章节来源
- [asmysql/v3dev/_sync_result.py:1-200](file://asmysql/v3dev/_sync_result.py#L1-L200)

## 依赖关系分析
- 模块导出
  - asmysql.__init__ 默认导出 v2 的 AsMysql/Engine/Result 以及别名 AsyncEngine/AsyncResult
- 运行时依赖
  - v2/v3dev 异步 Engine 依赖 aiomysql.Pool/create_pool
  - v3dev 同步 Engine 依赖 pymysql 与自定义同步 Pool
- 类型依赖
  - v3dev 中 EngineStatus TypedDict 用于 status 返回的结构化类型

```mermaid
graph LR
Root["asmysql/__init__.py"] --> V2A["v2/_asmysql.py"]
Root --> V2E["v2/_engine.py"]
Root --> V2R["v2/_result.py"]
V2E --> V2R
V3D["v3dev/_asmysql.py"] --> V3AE["v3dev/_async_engine.py"]
V3D --> V3SE["v3dev/_sync_engine.py"]
V3AE --> V3T["v3dev/_types.py"]
V3SE --> V3T
```

图示来源
- [asmysql/__init__.py:1-16](file://asmysql/__init__.py#L1-L16)
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [asmysql/v2/_engine.py:1-317](file://asmysql/v2/_engine.py#L1-L317)
- [asmysql/v2/_result.py:1-273](file://asmysql/v2/_result.py#L1-L273)
- [asmysql/v3dev/_asmysql.py:1-30](file://asmysql/v3dev/_asmysql.py#L1-L30)
- [asmysql/v3dev/_async_engine.py:1-307](file://asmysql/v3dev/_async_engine.py#L1-L307)
- [asmysql/v3dev/_sync_engine.py:1-298](file://asmysql/v3dev/_sync_engine.py#L1-L298)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)

章节来源
- [asmysql/__init__.py:1-16](file://asmysql/__init__.py#L1-L16)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)

## 性能与资源管理
- 连接池配置
  - min_pool_size/max_pool_size/pool_recycle/connect_timeout/auto_commit/echo_sql_log 等参数可通过构造函数或 URL 查询参数设置
- 流式处理
  - 大数据集建议使用 stream=True 并结合 async for 或 result.iterate()，避免一次性加载导致内存压力
- 自动关闭
  - 推荐优先使用 async with 或 async for，框架会在合适时机释放连接；若手动控制 close=False，务必在完成后调用 result.close()

章节来源
- [asmysql/v2/_engine.py:55-112](file://asmysql/v2/_engine.py#L55-L112)
- [asmysql/v2/_result.py:186-273](file://asmysql/v2/_result.py#L186-L273)
- [mkdocs/v2/docs/zh/best-practices.md:1-141](file://mkdocs/v2/docs/zh/best-practices.md#L1-L141)

## 故障排查指南
- 常见错误定位
  - 通过 result.error/error_no/error_msg 判断执行是否失败并获取错误码与消息
- 连接未建立
  - 访问 Engine.pool 前需确保已 connect()，否则抛出 ConnectionError
- 资源泄漏
  - 未正确关闭游标/连接可能导致连接池耗尽，遵循“上下文管理优先”的原则
- 调试输出
  - 使用 __repr__/__str__ 打印 AsMysql/Engine 实例，快速确认目标数据库地址

章节来源
- [asmysql/v2/_result.py:133-151](file://asmysql/v2/_result.py#L133-L151)
- [asmysql/v2/_engine.py:176-203](file://asmysql/v2/_engine.py#L176-L203)
- [asmysql/v2/_asmysql.py:14-21](file://asmysql/v2/_asmysql.py#L14-L21)

## 结论
- AsMysql 将业务逻辑与底层连接解耦，通过 client 暴露 Engine 能力，简化了业务层的数据库访问
- v3dev 引入泛型后，client 的类型更精确，有利于静态类型检查与 IDE 提示
- 结合 Result 的上下文管理与迭代协议，可实现简洁、健壮且高性能的数据访问流程
- 建议在生产环境中合理配置连接池、启用流式处理、严格错误处理与资源释放

## 附录：类型注解与泛型使用
- v2
  - AsMysql(client: Engine)，Engine.execute/execute_many 返回 Result[T]，T 由 result_class 决定
- v3dev
  - AsMysql(Generic[EngineType])，EngineType 限定为 SyncEngine 或 AsyncEngine
  - Engine.status 返回 EngineStatus TypedDict，字段包含 address/connected/pool_minsize/pool_maxsize/pool_size/pool_free/pool_used
- 结果类型
  - result_class 可为 tuple/dict/自定义模型（如 Pydantic BaseModel），Result 会自动构造对应类型

章节来源
- [asmysql/v2/_asmysql.py:1-26](file://asmysql/v2/_asmysql.py#L1-L26)
- [asmysql/v3dev/_asmysql.py:1-30](file://asmysql/v3dev/_asmysql.py#L1-L30)
- [asmysql/v2/_engine.py:204-317](file://asmysql/v2/_engine.py#L204-L317)
- [asmysql/v3dev/_async_engine.py:194-307](file://asmysql/v3dev/_async_engine.py#L194-L307)
- [asmysql/v3dev/_sync_engine.py:184-298](file://asmysql/v3dev/_sync_engine.py#L184-L298)
- [asmysql/v3dev/_types.py:1-12](file://asmysql/v3dev/_types.py#L1-L12)
- [pytest/v2/test_asmysql.py:8-12](file://pytest/v2/test_asmysql.py#L8-L12)

## 业务类设计与最佳实践
- 继承 AsMysql 组织业务方法，通过 self.client 执行 SQL
- 使用 result_class=dict 或自定义模型进行强类型映射
- 对大结果集采用 stream=True 与 async for/iterate()
- 使用 async with 或 async for 自动管理连接与游标
- 始终检查 result.error，并在出错时记录 error_no/error_msg

章节来源
- [mkdocs/v2/docs/zh/business-logic.md:1-67](file://mkdocs/v2/docs/zh/business-logic.md#L1-L67)
- [mkdocs/v2/docs/zh/best-practices.md:1-141](file://mkdocs/v2/docs/zh/best-practices.md#L1-L141)
- [tests/v2/v2_start.py:12-88](file://tests/v2/v2_start.py#L12-L88)
- [pytest/v2/test_asmysql.py:49-146](file://pytest/v2/test_asmysql.py#L49-L146)