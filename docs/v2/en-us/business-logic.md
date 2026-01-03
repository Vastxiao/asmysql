# Business Logic Development

## Inherit AsMysql Class

The `AsMysql` class provides a base class for business logic development, making it convenient to organize code through inheritance:

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
            raise Exception(f"Failed to create user: {result.error_msg}")
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

## Using Business Logic Class

```python
# Create engine
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

# Create business logic instance
user_service = UserService(engine)

# Use business methods
user = await user_service.get_user_by_id(1)
users = await user_service.list_users()
new_user_id = await user_service.create_user("张三", "zhangsan@example.com")
```

## Advantages

- **Code Organization**: Encapsulate database operations in business classes for easy maintenance
- **Reusability**: Business methods can be reused in multiple places
- **Type Safety**: Combined with type hints to improve code quality
- **Test Friendly**: Easy to perform unit testing

## Related Documentation

- [Quick Start](quickstart.md) - View basic usage examples
- [Usage Examples](examples.md) - View more business logic examples

