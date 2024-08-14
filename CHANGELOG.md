# Change Log

## [0.1.4] - 2024.08.15

### Features

1. AsMysql支持异步上下文管理器。

```python
import asyncio
from asmysql import AsMysql

class TestAsMysql(AsMysql):
    async def get_users(self):
        result = await self.client.execute('select user,authentication_string,host from mysql.user')
        if result.err:
            print(result.err)
        else:
            async for item in result.iterate():
                print(item)

async def main():
    async with TestAsMysql() as mysql:
        await mysql.get_users()

if __name__ == '__main__':
    asyncio.run(main())
```

## [0.1.1] - 2023.07.25

### Features

> 新增 Result.err_msg 返回exception错误的详情字符串。

## [0.1.0] - 2023.07.16

### Breaking Changes

### Features

> 1. asmysql是对aiomysql封装的简易使用库。
> 2. 支持自动管理mysql连接池，和重连机制。
> 3. 全局自动捕获处理MysqlError错误。
> 4. 分离执行语句和数据获取。
> 5. 直接集成AsMysql类进行逻辑开发。

### Internal

> 初始化项目，开发环境使用poetry进行管理。
