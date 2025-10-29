#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def suite():
    """
    创建并返回V2版本的测试套件
    """
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # 添加v2 mock测试
    test_suite.addTests(loader.loadTestsFromModule(
        __import__("pytest.v2.test_asmysql_mock", fromlist=[""])
    ))
    
    return test_suite


def print_header():
    """
    打印V2测试的头部信息
    """
    print("\n" + "="*50)
    print("Running V2 Mock Tests")
    print("="*50)


def print_results(result):
    """
    打印V2测试结果
    """
    print(f"V2 Mock Tests: Ran {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")


def run():
    """
    运行V2测试套件
    """
    print_header()
    test_suite = suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    print_results(result)
    return result