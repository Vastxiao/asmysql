# Quick Start

This guide will help you get started with asmysql v2 quickly.

## Method 1: Using Engine Class

The `Engine` class is an independent MySQL connection engine that can be used directly:

```python
import asyncio
from asmysql import Engine

# Create MySQL connection engine
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

async def main():
    # Connect to MySQL
    await engine.connect()
    
    # Execute SQL statement
    async with engine.execute("SELECT user, host FROM mysql.user") as result:
        async for item in result.iterate():
            print(item)
    
    # Disconnect from MySQL
    await engine.disconnect()

asyncio.run(main())
```

## Method 2: Using AsMysql Class

The `AsMysql` class is used for business logic development, ready to use by inheritance:

```python
import asyncio
from asmysql import Engine, AsMysql

# Create MySQL connection engine
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

# Write business logic class
class UserService(AsMysql):
    async def get_all_users(self):
        result = await self.client.execute("SELECT user, host FROM mysql.user")
        if result.error:
            print(f"Error code: {result.error_no}, Error message: {result.error_msg}")
        else:
            async for item in result.iterate():
                print(item)

async def main():
    # Connect to MySQL
    await engine.connect()
    
    # Create business logic instance
    user_service = UserService(engine)
    
    # Execute business logic
    await user_service.get_all_users()
    
    # Disconnect from MySQL
    await engine.disconnect()

asyncio.run(main())
```

## Next Steps

- Learn about [Connection Management](connection.md) for detailed configuration
- Learn about [Query Operations](query.md) for various usage patterns
- Check out [Usage Examples](examples.md) for more example code

