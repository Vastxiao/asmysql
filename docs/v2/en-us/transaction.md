# Transaction Control

## Auto Commit (Default)

```python
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    auto_commit=True  # Default value
)
await engine.connect()

# Auto commit
result = await engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))
```

## Manual Commit

```python
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    auto_commit=False
)
await engine.connect()

# No auto commit
result = await engine.execute(
    "INSERT INTO users (name) VALUES (%s)",
    ("张三",),
    commit=False
)

# Manual commit
await result.close()  # Need to manually manage connection
```

## Notes

Transaction management in v2 requires manual connection control. It is recommended to choose an appropriate commit strategy based on actual requirements in production environments.

## Related Documentation

- [Query Operations](query.md) - Learn how to execute SQL statements
- [Best Practices](best-practices.md) - Learn recommended usage patterns

