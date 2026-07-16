# Transaction Control

## Auto-Commit Mechanism

v2 uses an SQL statement type-based auto-commit mechanism. The `Result` class internally uses the `_should_commit()` method to analyze the first keyword of the SQL statement and automatically determines whether to execute `COMMIT`.

### Write Operations Auto-Commit

For the following write operation keywords, `COMMIT` is automatically executed after execution:

- `INSERT`, `UPDATE`, `DELETE`, `REPLACE`
- `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`
- `GRANT`, `REVOKE`, `LOCK`, `UNLOCK`
- `SET`, `LOAD`, `CALL`

```python
# Write operations auto-commit, no manual control needed
result = await engine.execute(
    "INSERT INTO users (name) VALUES (%s)", ("张三",)
)
# Automatically COMMIT after execution
```

### Read Operations Do Not Commit

For read operations like `SELECT`, `COMMIT` is not executed since read operations don't require transaction commits.

```python
# Read operations do not trigger COMMIT
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()
```

### Stream Mode Does Not Commit

In `stream=True` mode, even write operations are not auto-committed. This is because `COMMIT` in stream mode would interrupt the stream.

```python
# Streaming queries do not auto-commit
result = await engine.execute(
    "SELECT * FROM large_table",
    stream=True
)
async for row in result:
    process(row)
```

## Connection Pool Configuration

The connection pool is created with `autocommit=False` hardcoded, which means:

- Each connection defaults to no auto-commit
- Transaction commits are handled automatically by `Result` internal logic based on SQL type
- No need to manually configure `auto_commit` parameter

## Related Documentation

- [Query Operations](query.md) - Learn how to execute SQL statements
- [Best Practices](best-practices.md) - Learn recommended usage patterns
