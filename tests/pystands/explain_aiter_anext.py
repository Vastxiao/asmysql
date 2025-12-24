#!/usr/bin/env python3
"""
演示 __aiter__ 和 __anext__ 的区别和关联

这个示例文件将详细展示这两个方法的区别、关联以及它们如何协同工作
实现异步迭代器协议。
"""

import asyncio
from typing import Any, List


class AsyncIteratorExample:
    """
    一个简单的异步迭代器示例，展示 __aiter__ 和 __anext__ 的使用
    """
    def __init__(self, data: List[Any]):
        """初始化异步迭代器"""
        self.data = data
        self.index = 0
        print(f"创建异步迭代器，包含 {len(data)} 个元素: {data}")
    
    def __aiter__(self):
        """
        __aiter__ 方法:
        - 返回一个异步迭代器对象
        - 在这个例子中，返回对象本身（self）
        - 当使用 'async for' 语句时首先被调用
        """
        print("__aiter__ 被调用")
        # 重置索引以支持多次迭代
        self.index = 0
        # 返回异步迭代器对象（在这个例子中是 self）
        return self
    
    async def __anext__(self):
        """
        __anext__ 方法:
        - 返回下一个异步迭代值
        - 当没有更多元素时抛出 StopAsyncIteration 异常
        - 每次迭代时被调用
        """
        print(f"__anext__ 被调用，当前索引: {self.index}")
        
        # 检查是否还有更多元素
        if self.index >= len(self.data):
            print("__anext__ 抛出 StopAsyncIteration 异常")
            raise StopAsyncIteration
        
        # 模拟异步操作（例如 I/O 操作）
        await asyncio.sleep(0.1)
        
        # 获取当前元素
        value = self.data[self.index]
        print(f"__anext__ 返回值: {value}")
        
        # 移动到下一个元素
        self.index += 1
        
        return value


class SeparateAsyncIterator:
    """
    分离的异步迭代器示例
    展示 __aiter__ 返回不同对象的情况
    """
    def __init__(self, data: List[Any]):
        self.data = data
        print(f"创建可迭代对象，包含 {len(data)} 个元素: {data}")
    
    def __aiter__(self):
        """
        __aiter__ 返回一个新的异步迭代器对象
        这种方式更加灵活，允许一个对象支持多个并发迭代
        """
        print("__aiter__ 被调用，返回新的异步迭代器对象")
        return SeparateAsyncIteratorImpl(self.data)


class SeparateAsyncIteratorImpl:
    """
    独立的异步迭代器实现类
    """
    def __init__(self, data: List[Any]):
        self.data = data
        self.index = 0
    
    def __aiter__(self):
        """返回自身"""
        return self
    
    async def __anext__(self):
        """异步获取下一个元素"""
        if self.index >= len(self.data):
            raise StopAsyncIteration
        
        await asyncio.sleep(0.05)
        value = self.data[self.index]
        self.index += 1
        return value


async def demonstrate_aiter_anext():
    """演示 __aiter__ 和 __anext__ 的使用"""
    print("=" * 50)
    print("演示1: 基本的 __aiter__ 和 __anext__ 使用")
    print("=" * 50)
    
    # 创建异步迭代器
    async_iter = AsyncIteratorExample([1, 2, 3])
    
    print("\n使用 'async for' 循环:")
    async for item in async_iter:
        print(f"  接收到值: {item}")
    
    print("\n" + "-" * 30)
    print("手动调用 __aiter__ 和 __anext__:")
    
    # 手动获取异步迭代器
    aiter_obj = async_iter.__aiter__()
    print(f"__aiter__ 返回的对象: {aiter_obj}")
    
    # 手动调用 __anext__
    try:
        while True:
            item = await aiter_obj.__anext__()
            print(f"  接收到值: {item}")
    except StopAsyncIteration:
        print("  迭代完成!")


async def demonstrate_separate_iterator():
    """演示分离的迭代器"""
    print("\n" + "=" * 50)
    print("演示2: 分离的迭代器对象")
    print("=" * 50)
    
    # 创建可迭代对象
    iterable_obj = SeparateAsyncIterator(['a', 'b', 'c'])
    
    print("\n使用 'async for' 循环:")
    async for item in iterable_obj:
        print(f"  接收到值: {item}")


async def demonstrate_multiple_iterations():
    """演示多次迭代同一个对象"""
    print("\n" + "=" * 50)
    print("演示3: 多次迭代")
    print("=" * 50)
    
    async_iter = AsyncIteratorExample([10, 20, 30])
    
    print("\n第一次迭代:")
    async for item in async_iter:
        print(f"  第一次: {item}")
    
    print("\n第二次迭代:")
    async for item in async_iter:
        print(f"  第二次: {item}")


async def compare_with_sync_iterator():
    """对比同步迭代器"""
    print("\n" + "=" * 50)
    print("演示4: 与同步迭代器的对比")
    print("=" * 50)
    
    class SyncIteratorExample:
        def __init__(self, data):
            self.data = data
            self.index = 0
        
        def __iter__(self):
            """同步迭代器使用 __iter__"""
            self.index = 0
            return self
        
        def __next__(self):
            """同步迭代器使用 __next__"""
            if self.index >= len(self.data):
                raise StopIteration
            
            value = self.data[self.index]
            self.index += 1
            return value
    
    sync_iter = SyncIteratorExample([100, 200, 300])
    print("同步迭代:")
    for item in sync_iter:
        print(f"  同步值: {item}")
    
    async_iter = AsyncIteratorExample([100, 200, 300])
    print("异步迭代:")
    async for item in async_iter:
        print(f"  异步值: {item}")


async def main():
    """主函数"""
    await demonstrate_aiter_anext()
    await demonstrate_separate_iterator()
    await demonstrate_multiple_iterations()
    await compare_with_sync_iterator()
    
    print("\n" + "=" * 50)
    print("总结:")
    print("=" * 50)
    print("1. __aiter__ 方法:")
    print("   - 返回异步迭代器对象")
    print("   - 在 'async for' 开始时调用")
    print("   - 通常返回 self 或一个新的异步迭代器对象")
    print("\n2. __anext__ 方法:")
    print("   - 返回下一个异步值")
    print("   - 每次迭代时调用")
    print("   - 必须是 async 方法")
    print("   - 没有更多元素时必须抛出 StopAsyncIteration")
    print("\n3. 关联:")
    print("   - 两者共同实现异步迭代器协议")
    print("   - __aiter__ 先被调用，然后多次调用 __anext__")
    print("   - __aiter__ 返回的对象必须实现 __anext__ 方法")


if __name__ == "__main__":
    asyncio.run(main())