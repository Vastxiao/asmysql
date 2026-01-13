# asmysql

[![PyPI](https://img.shields.io/pypi/v/asmysql.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Python](https://img.shields.io/pypi/pyversions/asmysql.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Licence](https://img.shields.io/github/license/Vastxiao/asmysql.svg)](https://github.com/Vastxiao/asmysql/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/asmysql)](https://pepy.tech/project/asmysql)
[![Downloads](https://static.pepy.tech/badge/asmysql/month)](https://pepy.tech/project/asmysql)
[![Downloads](https://static.pepy.tech/badge/asmysql/week)](https://pepy.tech/project/asmysql)

* PyPI: https://pypi.org/project/asmysql/
* GitHub: https://github.com/vastxiao/asmysql
* Gitee: https://gitee.com/vastxiao/asmysql

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
# 从PyPI安装
pip install asmysql
```

## 【使用文档】

### 快速开始

```python
import asyncio
from asmysql import AsMysql


# 直接继承AsMysql类进行开发:
class TestAsMysql(AsMysql):
    # 这里可以定义一些Mysql实例初始化的默认参数
    # 属性跟 __init__ 参数一致
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    password = 'pass'

    async def get_users(self):
        # self.client属性是专门用来执行sql语句的，提供aiomysql的execute和execute_many方法
        result = await self.client.execute('select user,authentication_string,host from mysql.user')
        # result是专门用来获取执行结果的，提供fetch_one、fetch_many、fetch_all、iterate方法
        # result.err是所有关于mysql执行的异常对象(Exception)
        if result.err:
            print(result.err_msg)
        else:
            # result.iterate()是一个异步迭代器，可以获取执行结果的每一行数据
            async for item in result.iterate():
                print(item)

                
async def main():
    # 这个会创建实例并连接mysql：
    mysql = await TestAsMysql()

    await mysql.get_users()

    # 程序退出前记得断开mysql连接：
    await mysql.disconnect()


asyncio.run(main())
```

### 支持异步上下文管理器。

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
    # 使用 async with 的话，在代码退出时会自动断开mysql连接
    async with TestAsMysql() as mysql:
        await mysql.get_users()

if __name__ == '__main__':
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

# 创建mysql实例时可以传入mysql地址，用户密码等参数
mysql = TestAsMysql(host='192.168.1.192', port=3306)

async def main():
    # 执行会连接到mysql：
    await mysql.connect()  # or: await mysql

    print(await mysql.get_users())

    # 断开mysql连接：
    await mysql.disconnect()

asyncio.run(main())
```
