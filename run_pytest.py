#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    # 显示Python版本
    print(f"Python version: {sys.version}")

    # 运行mock测试（不需要数据库连接）
    print("\n=== Running Mock Tests ===")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加v2 mock测试
    suite.addTests(loader.loadTestsFromModule(__import__("pytest.v2.test_asmysql_mock", fromlist=[""])))
    
    # 添加v3 mock测试
    suite.addTests(loader.loadTestsFromModule(__import__("pytest.v3.test_asmysql_mock", fromlist=[""])))
    
    # 运行所有mock测试
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()