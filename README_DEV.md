# 环境配置帮助文档

## 环境依赖

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or
pip install uv
```

## 开发环境搭建

```bash
# 初始化开发环境
uv sync

# 查看包依赖
#uv tree
# 查看已安装的依赖
#uv pip list
# 在当前shell激活python环境
#. .venv/bin/activate
```

## 运行 pytest 测试

### 基本命令

```bash
# 运行全部测试（Mock 测试通过，集成测试自动跳过）
uv run pytest

# 等价于 uv run pytest -v，带详细输出
uv run python run_pytest.py

# 等价写法
uv run python -m pytest
```

### 使用 marker 过滤测试

测试文件 `test_asmysql.py` 顶部声明了 `pytestmark = pytest.mark.integration`，
将所有测试标记为**集成测试**（需要真实 MySQL 数据库）。

```bash
# 只运行 Mock 测试，排除集成测试
uv run pytest -m "not integration"
# 结果：10 passed, 6 deselected

# 只运行集成测试
uv run pytest -m integration
# 结果：6 skipped（无 MySQL 时自动跳过）

# 运行全部测试（包括集成测试，需要 MySQL）
uv run pytest -m "" -o addopts=""
# other
uv run pytest -m ""
uv run pytest -o addopts=""
```

### skipped vs deselected 的区别

| 状态 | 含义 | 何时出现 |
|------|------|----------|
| **skipped** | 测试被收集了，但在运行时跳过 | fixture 中调用 `pytest.skip()`（如 MySQL 不可用） |
| **deselected** | 测试在收集阶段就被排除，根本不运行 | 使用 `-m` marker 过滤时 |

示例：
- `uv run pytest` → 收集 16 个测试，集成测试运行时 skip → `10 passed, 6 skipped`
- `uv run pytest -m "not integration"` → 收集时排除集成测试 → `10 passed, 6 deselected`

### 运行指定测试

```bash
# 运行指定测试文件
uv run pytest autopytest/v2/test_asmysql_mock.py -v

# 运行单个测试函数
uv run pytest autopytest/v2/test_asmysql_mock.py::test_asmysql_creation -v
```

### run_pytest.py 的作用

`run_pytest.py` 是 pytest 的简单脚本封装，等价于 `uv run pytest -v`。
适合在 CI/CD 或 IDE 中使用，便于统一管理测试入口。

### 测试架构

```
autopytest/
└── v2/
    ├── conftest.py              # 共享 fixtures（mock_engine, asmysql, mock_result）
    ├── test_asmysql_mock.py     # Mock 测试（无需 MySQL）
    └── test_asmysql.py          # 集成测试（@pytest.mark.integration）
```

- **conftest.py**：定义共享 fixtures，pytest 自动发现并注入到测试函数参数中
- **Mock 测试**：使用 `unittest.mock.Mock` 模拟 Engine 和 Result，无需真实数据库
- **集成测试**：使用 `pytest.mark.integration` 标记，fixture 中尝试连接 MySQL，失败时自动 skip

## 构建软件包

```bash
[ -f dist ] && rm -rvf dist
uv build
# 打包文件在dist目录下
```

## 发布软件包

```bash
# test:
uv publish --username __token__

# pypi:
uv publish --index testpypi --username __token__
```
