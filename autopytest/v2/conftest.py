#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""V2 测试共享 fixtures"""

from unittest.mock import Mock

import pytest

from asmysql.v2 import AsMysql, Engine, Result


@pytest.fixture
def mock_engine():
    """创建一个 Mock 的 Engine 实例"""
    engine = Mock(spec=Engine)
    engine.url = "mysql://localhost:3306/test_db"
    engine.host = "localhost"
    engine.port = 3306
    return engine


@pytest.fixture
def asmysql(mock_engine):
    """创建使用 mock engine 的 AsMysql 实例"""
    return AsMysql(mock_engine)


@pytest.fixture
def mock_result():
    """创建一个 Mock 的 Result 实例"""
    result = Mock(spec=Result)
    result.error = None
    result.row_count = 1
    return result
