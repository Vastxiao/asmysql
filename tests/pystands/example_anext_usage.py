#!/usr/bin/env python3
"""
示例文件，展示 __anext__ 方法的用法

这个示例展示了如何在 Python 中实现和使用异步迭代器，
以及在 asmysql 库中如何使用异步迭代处理数据库查询结果。
"""

import asyncio


class ExampleIterator:
    """
    一个简单的示例类，演示 __anext__ 方法的实现和使用
    """
    def __init__(self, data):
        self.data = data
        self.index = 0
    
    def __aiter__(self):
        """返回异步迭代器对象本身"""
        return self
    
    async def __anext__(self):
        """
        异步迭代器的下一个元素方法
        
        当还有数据时，返回下一个元素
        当没有更多数据时，抛出 StopAsyncIteration 异常
        """
        if self.index >= len(self.data):
            raise StopAsyncIteration
        
        # 模拟异步操作
        await asyncio.sleep(0.01)
        value = self.data[self.index]
        self.index += 1
        return value


async def basic_anext_example():
    """
    基础的 __anext__ 使用示例
    """
    print("=== 基础 __anext__ 使用示例 ===")
    
    # 创建一个异步迭代器
    async_iter = ExampleIterator([1, 2, 3, 4, 5])
    
    # 方法1: 使用 async for 循环 (推荐方式)
    print("方法1: 使用 async for 循环")
    async for item in async_iter:
        print(f"  数据项: {item}")
    
    print()
    
    # 方法2: 手动调用 __anext__ 方法
    print("方法2: 手动调用 __anext__ 方法")
    async_iter2 = ExampleIterator(['a', 'b', 'c'])
    
    try:
        while True:
            item = await async_iter2.__anext__()
            print(f"  数据项: {item}")
    except StopAsyncIteration:
        print("  迭代完成!")


async def streaming_anext_example():
    """
    流式处理大数据集的示例
    """
    print("\n=== 流式处理示例 ===")
    
    # 模拟一个大数据集的异步迭代器
    large_dataset = list(range(100))  # 模拟100条数据
    async_iter = ExampleIterator(large_dataset)
    
    print("处理大数据集，限制只处理前10条:")
    count = 0
    try:
        while count < 10:
            item = await async_iter.__anext__()
            print(f"  处理数据项 {item}")
            count += 1
    except StopAsyncIteration:
        print("  数据集已处理完")
    
    print(f"总共处理了 {count} 条数据")


# 模拟 asmysql 中的 Result 类实现
class MockResult:
    """
    模拟 asmysql 中的 Result 类，展示在数据库查询中的 __anext__ 使用
    """
    def __init__(self, data):
        self.data = data
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        """
        异步获取下一行查询结果
        """
        if self.index >= len(self.data):
            raise StopAsyncIteration
        
        # 模拟从数据库获取数据的异步操作
        await asyncio.sleep(0.001)
        row = self.data[self.index]
        self.index += 1
        return row


async def asmysql_anext_example():
    """
    在 asmysql 中使用 __anext__ 的示例
    """
    print("\n=== asmysql 中的 __anext__ 使用示例 ===")
    
    # 模拟数据库查询结果
    mock_data = [
        (1, 'Alice', 'alice@example.com'),
        (2, 'Bob', 'bob@example.com'),
        (3, 'Charlie', 'charlie@example.com')
    ]
    
    result = MockResult(mock_data)
    
    print("方法1: 使用 async for 循环遍历结果 (推荐)")
    async for row in result:
        print(f"  行数据: {row}")
    
    print()
    
    # 重新创建结果对象以演示手动调用 __anext__
    result2 = MockResult(mock_data)
    
    print("方法2: 手动调用 __anext__ 方法")
    try:
        while True:
            row = await result2.__anext__()
            print(f"  行数据: {row}")
    except StopAsyncIteration:
        print("  查询结果遍历完成!")


async def main():
    """
    主函数，运行所有示例
    """
    await basic_anext_example()
    await asmysql_anext_example()
    await streaming_anext_example()


if __name__ == "__main__":
    asyncio.run(main())