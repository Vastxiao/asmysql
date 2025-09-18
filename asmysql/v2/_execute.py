class ExecuteResult:
    def __init__(self, coro):
        self._coro = coro
        self._result = None

    def __await__(self):
        return self._coro.__await__()

    async def __aenter__(self):
        self._result = await self._coro
        return self._result

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 可以在这里处理清理工作
        pass
