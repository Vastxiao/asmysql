# 业务逻辑开发

## 继承 AsMysql 类

`AsMysql` 类提供了业务逻辑开发的基类，通过继承可以方便地组织代码：

```python
from asmysql import Engine, AsMysql

class UserService(AsMysql):
    async def get_user_by_id(self, user_id: int):
        result = await self.client.execute(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            result_class=dict
        )
        if result.error:
            return None
        return await result.fetch_one()

    async def create_user(self, name: str, email: str):
        result = await self.client.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        if result.error:
            raise Exception(f"创建用户失败: {result.error_msg}")
        return result.last_rowid

    async def list_users(self):
        result = await self.client.execute(
            "SELECT * FROM users",
            result_class=dict
        )
        if result.error:
            return []
        return await result.fetch_all()
```

## 使用业务逻辑类

```python
# 创建引擎
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

# 创建业务逻辑实例
user_service = UserService(engine)

# 使用业务方法
user = await user_service.get_user_by_id(1)
users = await user_service.list_users()
new_user_id = await user_service.create_user("张三", "zhangsan@example.com")
```

## 优势

- **代码组织**：将数据库操作封装在业务类中，便于维护
- **复用性**：业务方法可以在多个地方复用
- **类型安全**：配合类型提示，提升代码质量
- **测试友好**：可以轻松进行单元测试

## 相关文档

- [快速开始](quickstart.md) - 查看基本使用示例
- [使用示例](examples.md) - 查看更多业务逻辑示例
