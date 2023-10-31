# asmysql

## 【简介】

asmysql是封装aiomysql的mysql异步客户端使用库。

## 【特性】

* 代码支持类型注释。
* 使用极为简单，直接继承AsMysql类进行逻辑开发。
* 支持自动管理mysql连接池，和重连机制。
* 全局自动捕获处理MysqlError错误。
* 分离执行语句和数据获取。

## 【安装asmysql包】

```sh
# Python3.11+

# 从PyPI安装
pip install asmysql

# 如果从本地包安装使用以下命令
pip install asmysql-X.X.X.tar.gz
# or
pip install asmysql-X.X.X-py3-none-any.whl
```

## 【使用文档】

### 快速开始

```python
import asyncio
from asmysql import AsMysql


class TestAsMysql(AsMysql):
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    password = 'pass'

    async def get_users(self):
        result = await self.client.execute('select user,authentication_string,host from mysql.user')
        if result.err:
            print(result.err)
        else:
            async for item in result.iterate():
                print(item)

                
async def main():
    mysql = await TestAsMysql()
    await mysql.get_users()
    await mysql.disconnect()


asyncio.run(main())
```

### 创建实例的更多用法

```python
import asyncio
from asmysql import AsMysql

class TestAsMysql(AsMysql):
    async def get_users(self):
        result = await self.client.execute('select user,authentication_string,host from mysql.user')
        if result.err:
            print(result.err)
        else:
            return await result.fetch_all()

mysql = TestAsMysql(host='192.168.1.192', port=3306)

async def main():
    await mysql.connect()  # or: await mysql
    print(await mysql.get_users())
    await mysql.disconnect()

asyncio.run(main())
```
