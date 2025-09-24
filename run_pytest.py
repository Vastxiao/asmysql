#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest

if __name__ == '__main__':
    # 运行测试
    unittest.main(module='pytest.v2.test_asmysql_mock', exit=False, verbosity=2)
