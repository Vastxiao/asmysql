# 迁移指南

## 从 v1 迁移到 v2

1. **更新导入**
   ```python
   # v1
   from asmysql import AsMysql
   
   # v2
   from asmysql import Engine, AsMysql
   ```

2. **更新连接方式**
   ```python
   # v1
   class MyService(AsMysql):
       host = '127.0.0.1'
       port = 3306
       user = 'root'
       password = 'pass'
   
   mysql = await MyService()
   
   # v2
   engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
   await engine.connect()
   
   class MyService(AsMysql):
       pass
   
   service = MyService(engine)
   ```

3. **更新错误属性**
   ```python
   # v1
   if result.err:
       print(result.err_msg)
   
   # v2
   if result.error:
       print(result.error_msg)
   ```

4. **使用新的功能**
   ```python
   # v2 新增：URL 连接
   engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
   
   # v2 新增：流式查询
   async for row in engine.execute("SELECT * FROM large_table", stream=True):
       process(row)
   
   # v2 新增：自定义结果类型
   result = await engine.execute("SELECT * FROM users", result_class=dict)
   ```

