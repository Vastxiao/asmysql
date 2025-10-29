# Change Log

## v2.0.0

> (Breaking Changes)
> 完整重构了新版本，功能与旧版本不兼容。
> Result结果err属性变更为error属性。
> 分离AsMysql类的逻辑，新增Engine类来处理mysql连接和执行语句，Engine可单独使用。
>
> (New Features)
> 执行结果Result支持MysqlError的错误码error_no和错误信息error_msg属性。
> Mysql初始化连接支持url参数: mysql://user:password@host:port/?charset=utf8mb4。
> 支持获取mysql连接的状态，使用status属性(Engine.status)。
> execute方法支持stream参数，返回无缓存数据流。
> Result支持上下文和迭代器模式。
> Result支持无缓存数据流获取模式。
> 支持Result返回自定义类型的数据。
> 新增pytest测试。
>
> (Update)使用uv作为包管理工具。
> 
> (Features)
> 1. asmysql是对aiomysql封装的简易使用库。
> 2. 支持自动管理mysql连接池，和重连机制。
> 3. 全局自动捕获处理MysqlError错误。
> 4. 分离执行语句和数据获取。
> 5. 支持IDE编程的Python类型提示。
> 6. 直接集成AsMysql类进行逻辑开发。
