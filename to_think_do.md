# 待研究问题

## Result 异步迭代协议设计 (`asmysql/v2/_result.py`)

### 现状

`Result` 同时定义了 `__aiter__`（async generator 函数）和 `__anext__`，但 `__anext__` 实际上是死代码：

- `async for item in result` → 调用 `result.__aiter__()` → 返回一个 **async generator 对象**（不是 `self`）→ Python 对该 generator 调用 `__anext__`
- `Result.__anext__`（第115行）永远不会被 `async for` 触发
- `async for` 实际走的是 `__aiter__` 内部的 `fetch_one` 循环

### 影响

- `async for` 本身能正常工作，功能无损
- 但 `Result` 不是自身的 async iterator（`__aiter__` 不返回 `self`），所以 `anext(result)` 不可用
- `__anext__` 的存在可能误导阅读代码的人

### 可选方案

1. **删除 `__anext__`**：最简方案，保持 `__aiter__` 作为 async generator 函数不变
2. **重构为规范 async iterator**：让 `__aiter__` 返回 `self`，`__anext__` 驱动 `fetch_one`，支持 `anext(result)`
3. **保持现状**：功能正常，死代码不影响运行

### 建议

先确认是否有用户依赖 `anext(result)` 的用法（大概率没有），再决定方案 1 或 2。
