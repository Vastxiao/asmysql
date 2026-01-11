#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def suite():
    """
    创建并返回V3版本的测试套件
    """
    # 临时解决导入问题
    import asmysql.v3dev
    sys.modules['asmysql.v3'] = asmysql.v3dev
    
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # 添加v3异步mock测试
    test_suite.addTests(loader.loadTestsFromModule(
        __import__("pytest.v3.test_asmysql_async_mock", fromlist=[""])
    ))
    
    # 添加v3同步mock测试
    test_suite.addTests(loader.loadTestsFromModule(
        __import__("pytest.v3.test_asmysql_sync_mock", fromlist=[""])
    ))
    
    return test_suite


def print_header():
    """
    打印V3测试的头部信息
    """
    print("\n" + "="*50)
    print("Running V3 Mock Tests")
    print("="*50)


def print_results(result):
    """
    打印V3测试结果
    """
    print(f"V3 Mock Tests: Ran {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")


def run():
    """
    运行V3测试套件
    """
    print_header()
    test_suite = suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    print_results(result)
    return result