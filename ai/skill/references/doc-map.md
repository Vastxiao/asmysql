# asmysql 文档地图

> 本文件是 asmysql-dev skill 的本地参考：站点页面与 GitHub raw md 双通道 URL 清单。
> 使用前必须先完成 SKILL.md 第 1 节的版本自检；版本不匹配时改读包内 skill 或在线来源。

## AI 入口（版本无关，永远最新）

| 用途 | URL |
|------|-----|
| 文档站根 | <https://vastxiao.github.io/asmysql/> |
| AI 资产根 | <https://vastxiao.github.io/asmysql/ai/> |
| llms.txt（LLM 友好索引，先读这个） | <https://vastxiao.github.io/asmysql/ai/llms.txt> |
| llms-full.txt（中文全文拼接，体积大） | <https://vastxiao.github.io/asmysql/ai/llms-full.txt> |
| skill 在线主文件 | <https://vastxiao.github.io/asmysql/ai/skill/SKILL.md> |
| skill zip 下载 | <https://vastxiao.github.io/asmysql/ai/assets/asmysql-dev-skill.zip> |
| 根 llms.txt 指针（指向 /ai/llms.txt） | <https://vastxiao.github.io/asmysql/llms.txt> |
| GitHub 仓库 | <https://github.com/Vastxiao/asmysql> |
| PyPI | <https://pypi.org/project/asmysql/> |
| Gitee 镜像 | <https://gitee.com/vastxiao/asmysql> |

llms.txt 用途：纯文本索引，每页附一句话摘要，供 AI 按需取单页；llms-full.txt 用途：需要完整上下文时一次性读取中文全文。

## 文档页双通道（v2）

站点 URL 前缀：中文 `https://vastxiao.github.io/asmysql/v2/zh/`，英文 `https://vastxiao.github.io/asmysql/v2/`（英文为默认语言，无前缀）。
raw md 前缀：`https://raw.githubusercontent.com/Vastxiao/asmysql/main/mkdocs/v2/docs/`，后接 `zh/<page>.md` 或 `en/<page>.md`。

| 页面 | 中文站点 | 英文站点 | raw md（zh / en 同构） |
|------|----------|----------|------------------------|
| 首页 | <https://vastxiao.github.io/asmysql/v2/zh/> | <https://vastxiao.github.io/asmysql/v2/> | `index.md` |
| 安装 | <https://vastxiao.github.io/asmysql/v2/zh/installation/> | <https://vastxiao.github.io/asmysql/v2/installation/> | `installation.md` |
| 快速开始 | <https://vastxiao.github.io/asmysql/v2/zh/quickstart/> | <https://vastxiao.github.io/asmysql/v2/quickstart/> | `quickstart.md` |
| 连接管理 | <https://vastxiao.github.io/asmysql/v2/zh/connection/> | <https://vastxiao.github.io/asmysql/v2/connection/> | `connection.md` |
| 查询操作 | <https://vastxiao.github.io/asmysql/v2/zh/query/> | <https://vastxiao.github.io/asmysql/v2/query/> | `query.md` |
| 结果处理 | <https://vastxiao.github.io/asmysql/v2/zh/result/> | <https://vastxiao.github.io/asmysql/v2/result/> | `result.md` |
| 事务 | <https://vastxiao.github.io/asmysql/v2/zh/transaction/> | <https://vastxiao.github.io/asmysql/v2/transaction/> | `transaction.md` |
| 业务逻辑 | <https://vastxiao.github.io/asmysql/v2/zh/business-logic/> | <https://vastxiao.github.io/asmysql/v2/business-logic/> | `business-logic.md` |
| 示例 | <https://vastxiao.github.io/asmysql/v2/zh/examples/> | <https://vastxiao.github.io/asmysql/v2/examples/> | `examples.md` |
| API 参考 | <https://vastxiao.github.io/asmysql/v2/zh/api/> | <https://vastxiao.github.io/asmysql/v2/api/> | `api.md` |
| 最佳实践 | <https://vastxiao.github.io/asmysql/v2/zh/best-practices/> | <https://vastxiao.github.io/asmysql/v2/best-practices/> | `best-practices.md` |
| 迁移指南 | <https://vastxiao.github.io/asmysql/v2/zh/migration/> | <https://vastxiao.github.io/asmysql/v2/migration/> | `migration.md` |
| 常见问题 | <https://vastxiao.github.io/asmysql/v2/zh/faq/> | <https://vastxiao.github.io/asmysql/v2/faq/> | `faq.md` |
| 更新日志索引 | <https://vastxiao.github.io/asmysql/v2/zh/changelog/> | <https://vastxiao.github.io/asmysql/v2/changelog/> | `changelog.md`（版本详情 `changelog/v<X.Y.Z>.md`） |
| AI 辅助开发 | <https://vastxiao.github.io/asmysql/v2/zh/ai/> | <https://vastxiao.github.io/asmysql/v2/ai/> | `ai.md` |
| 论坛 | <https://vastxiao.github.io/asmysql/v2/zh/forum/> | <https://vastxiao.github.io/asmysql/v2/forum/> | `forum.md` |

## 包内资产（离线可得，随 wheel 分发）

| 路径（相对 site-packages） | 内容 |
|----------------------------|------|
| `asmysql/_ai/AGENTS.md` | 包内 AI 入口指引 |
| `asmysql/_ai/skills/asmysql-dev/SKILL.md` | skill 主文件（与已装包版本匹配） |
| `asmysql/_ai/skills/asmysql-dev/references/api-quickref.md` | API 速查 |
| `asmysql/_ai/skills/asmysql-dev/references/pitfalls.md` | 避坑清单 |
| `asmysql/_ai/skills/asmysql-dev/references/doc-map.md` | 本文档地图 |

定位包内 skill 目录：`python -m asmysql skill path`。

## 通道纪律

- raw 通道只允许指向手写 docs 页（上表）与包内 `asmysql/_ai/` 路径。
- 生成产物（llms*.txt / zip / skill 站点副本）不入库，raw 不可达；在线读取一律走站点 `/ai/` 完整 URL。
- 站点页面为 HTML，AI 抓取优先 raw md 或 llms.txt 纯文本通道。