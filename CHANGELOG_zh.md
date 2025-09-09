# Change Log

## v2.0.0(dev)

> (Breaking Changes)
> Result结果err属性变更为error属性。
>
> (New Features)
> 执行结果Result支持MysqlError的错误码error_no和错误信息error_msg属性。
> Mysql初始化连接支持ｕrl参数: mysql://user:password@host:port/?charset=utf8mb4。
>
> (Update)使用uv作为包管理工具。
> 
> (Features)
> 1. asmysql是对aiomysql封装的简易使用库。
> 2. 支持自动管理mysql连接池，和重连机制。
> 3. 全局自动捕获处理MysqlError错误。
> 4. 分离执行语句和数据获取。
> 5. 直接集成AsMysql类进行逻辑开发。
