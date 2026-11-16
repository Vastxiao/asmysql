---
name: asmysql-dev
description: 使用 asmysql（Python 异步 MySQL 客户端库）开发数据访问代码的规范与避坑指南。覆盖 Engine/AsMysql/Result 的 v2 用法、流式读取、result_class 映射、错误检查与文档获取。Use when writing or reviewing Python code that uses asmysql, async MySQL access via Engine/AsMysql/Result, or when the user mentions asmysql、异步 MySQL、连接池开发.
---

# asmysql-dev：asmysql 开发技能

asmysql 是基于 aiomysql 的 Python asyncio 异步 MySQL 客户端/连接池库，当前生产 API 为 v2。
本 skill 是 AI 辅助开发 asmysql 的第一入口：先做版本自检，再按速查与避坑清单写代码，按需取文档。

## 1. 版本自检（强制门禁，使用前必须执行）

已安装的 skill 只是缓存，事实来源永远是**当前包内置 skill**（随 wheel 版本匹配）与**在线最新版**。
使用本 skill 内容前必须先执行以下自检：

1. 读取与本 SKILL.md 同目录的 `.asmysql-skill.json` 戳记文件，取 `asmysql_version` 字段。
2. 获取已安装包版本：

   ```python
   from importlib.metadata import version
   installed = version("asmysql")
   ```

3. 比对两者：
   - **一致**：本 skill 与已装包匹配，可信任本地 `references/`。
   - **不一致，或无戳记文件**（如手动 zip 拷贝、来源不明）：**禁止信任本地 references**，改读以下任一版本匹配来源：
     - 包内 skill（与已装 wheel 一致，离线可得）：运行 `python -m asmysql skill path` 打印其目录，读取其中 SKILL.md 与 references；
     - 在线最新 SKILL.md：<https://vastxiao.github.io/asmysql/ai/skill/SKILL.md>。
   - 同时提示用户刷新本地副本：`python -m asmysql skill install --target <原目标> --force`。

## 2. 版本与导入

- 顶层导出（v2）：`from asmysql import AsMysql, Engine, EngineStatus, Result`；别名 `AsyncEngine = Engine`、`AsyncResult = Result`。
- `from asmysql.v1 import AsMysql` 为冻结旧版，仅兼容维护，**新代码一律 v2**。
- Python >= 3.12；核心依赖 `aiomysql[rsa]`。
- 核对已装版本：`importlib.metadata.version("asmysql")`。

## 3. 核心用法速查

完整速查见 [references/api-quickref.md](references/api-quickref.md)。最小示例：

```python
from asmysql import Engine

engine = Engine("mysql://user:pass@127.0.0.1:3306/?charset=utf8mb4")

async def demo():
    async with engine:  # 进入时 connect，退出时 disconnect
        async with engine.execute(
            "SELECT id, name FROM mydb.users WHERE id=%s", (1,)
        ) as result:
            if result.error:  # 取数前必须检查错误
                raise result.error
            row = await result.fetch_one()
```

要点：

- `Engine` 管理连接池：`connect()` / `disconnect()`；简写 `async with engine:`、`await engine`、`await engine()` 均等价 connect。
- `execute()` / `execute_many()` 返回**懒执行 `Result` 对象（不是协程）**，实际执行发生在 `async with` / `async for`。
- 业务类继承 `AsMysql`：构造只收 `Engine`，经 `self.client` 访问引擎；构造式单例（同子类 + 同引擎恒返回同一实例）。
- `stream=True` 流式读取大结果集；`result_class` 控制行映射（tuple / dict / 自定义类）。

## 4. 高频陷阱 Top 5

展开版与「错误写法 → 正确写法」代码对照见 [references/pitfalls.md](references/pitfalls.md)。

1. `execute()` 返回懒执行 `Result`，**不是协程**，禁止 `await engine.execute(...)`。
2. 取数前必须检查 `result.error`，否则错误被静默吞掉（iterate 返空伪装 0 行）。
3. 大结果集必须 `stream=True`，v1 缓冲游标会内存暴涨。
4. 每条 execute 是独立提交单元，**不支持跨语句事务**。
5. 活池不可跨事件循环共享。

## 5. 文档获取指引

按需获取，避免整站抓取 HTML：

1. **先读索引**：<https://vastxiao.github.io/asmysql/ai/llms.txt>（LLM 友好纯文本索引，每页附一句话摘要）。
2. **按需取单页**：中文站 `https://vastxiao.github.io/asmysql/v2/zh/<page>/`、英文站 `https://vastxiao.github.io/asmysql/v2/<page>/`；页面清单与 GitHub raw md 双通道见 [references/doc-map.md](references/doc-map.md)。
3. **全文（中文）**：<https://vastxiao.github.io/asmysql/ai/llms-full.txt>（需要完整上下文时用，体积较大）。
4. **离线**：读本 skill `references/` 与安装包内源码 docstring（包内 AI 入口 `asmysql/_ai/AGENTS.md`）。

## 6. skill 安装 / 更新

- 一键安装（在项目根运行，`--target` 必填，项目级优先）：

  ```bash
  python -m asmysql skill install --target claude
  ```

- `--target` 取值：`claude` / `cursor` / `agents`（项目级）；`user:claude` / `user:cursor` / `user:agents`（用户级）；`all` / `user:all`（仅向已存在的工具目录建软链）；支持逗号分隔多目标与任意自定义路径。
- 安装模型：`.agents/skills/asmysql-dev/` 单一真源 + 各工具目录 per-skill 软链；安装时写入 `.asmysql-skill.json` 版本戳记。
- **asmysql 升级后必须加 `--force` 重跑刷新**，否则第 1 节自检会判定副本过期。
- 零安装路径：直接在线读取本 SKILL.md 与 llms.txt（第 5 节），按内容开发。