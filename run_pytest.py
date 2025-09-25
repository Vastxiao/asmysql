#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    # 显示Python版本
    print(f"Python version: {sys.version}")
    
    # 运行mock测试（不需要数据库连接）
    print("\n=== Running Mock Tests ===")
    unittest.main(module='pytest.v2.test_asmysql_mock', exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()