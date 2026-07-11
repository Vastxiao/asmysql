#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""V2 测试 pytest 插件 — 通过 pyproject.toml addopts 中的 -p 早期加载

注册集成测试所需的命令行选项和 fixtures。
必须作为独立模块（非 conftest.py），以便 pytest 在 argparse 之前加载，
使 --mysql-url 选项及时可用。
"""

import os

import pytest

DEFAULT_TEST_URL = "mysql://root:@localhost:3306/"


def pytest_addoption(parser):
    """注册 --mysql-url 命令行选项"""
    parser.addoption(
        "--mysql-url",
        action="store",
        default=None,
        help="MySQL 连接 URL，用于集成测试（优先级高于环境变量 ASMYSQL_TEST_URL）",
    )


@pytest.fixture(scope="session")
def mysql_url(request):
    """获取集成测试用的 MySQL 连接 URL

    优先级（从高到低）：
    1. 命令行参数 --mysql-url
    2. 环境变量 ASMYSQL_TEST_URL
    3. 默认值 mysql://root:@localhost:3306/
    """
    cli_url = request.config.getoption("--mysql-url")
    if cli_url:
        return cli_url
    return os.environ.get("ASMYSQL_TEST_URL", DEFAULT_TEST_URL)
