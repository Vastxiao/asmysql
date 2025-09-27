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
    
    # 运行v2 mock测试
    print("\n" + "="*50)
    print("Running V2 Mock Tests")
    print("="*50)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加v2 mock测试
    suite.addTests(loader.loadTestsFromModule(__import__("pytest.v2.test_asmysql_mock", fromlist=[""])))
    
    # 运行v2 mock测试
    runner = unittest.TextTestRunner(verbosity=2)
    result_v2 = runner.run(suite)
    
    # 运行v3 mock测试
    print("\n" + "="*50)
    print("Running V3 Mock Tests")
    print("="*50)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加v3 mock测试
    suite.addTests(loader.loadTestsFromModule(__import__("pytest.v3.test_asmysql_mock", fromlist=[""])))
    
    # 运行v3 mock测试
    runner = unittest.TextTestRunner(verbosity=2)
    result_v3 = runner.run(suite)
    
    # 汇总结果
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"V2 Tests: Ran {result_v2.testsRun} tests, {len(result_v2.failures)} failures, {len(result_v2.errors)} errors")
    print(f"V3 Tests: Ran {result_v3.testsRun} tests, {len(result_v3.failures)} failures, {len(result_v3.errors)} errors")
    
    total_tests = result_v2.testsRun + result_v3.testsRun
    total_failures = len(result_v2.failures) + len(result_v3.failures)
    total_errors = len(result_v2.errors) + len(result_v3.errors)
    
    print(f"Total: Ran {total_tests} tests, {total_failures} failures, {total_errors} errors")
    
    if total_failures == 0 and total_errors == 0:
        print("\nAll tests passed! ✓")
    else:
        print("\nSome tests failed! ✗")


if __name__ == "__main__":
    run_tests()