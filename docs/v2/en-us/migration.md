# Migration Guide

## Migrating from v1 to v2

1. **Update Imports**
   ```python
   # v1
   from asmysql import AsMysql
   
   # v2
   from asmysql import Engine, AsMysql
   ```

2. **Update Connection Method**
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

3. **Update Error Attributes**
   ```python
   # v1
   if result.err:
       print(result.err_msg)
   
   # v2
   if result.error:
       print(result.error_msg)
   ```

4. **Use New Features**
   ```python
   # v2 new: URL connection
   engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
   
   # v2 new: Streaming query
   async for row in engine.execute("SELECT * FROM large_table", stream=True):
       process(row)
   
   # v2 new: Custom result type
   result = await engine.execute("SELECT * FROM users", result_class=dict)
   ```

