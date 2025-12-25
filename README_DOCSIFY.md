# Docsify 文档配置说明

## 启动文档服务器

在 `docs` 目录下运行：

```bash
docsify serve .
```

或者使用全局安装的 docsify-cli：

```bash
docsify serve docs
```

文档将在 `http://localhost:3000` 启动。

## 目录结构

```
docs/
├── index.html              # Docsify 主配置文件
├── README.md               # 英文首页
├── README_zh.md            # 中文首页
├── _sidebar.md             # 英文侧边栏
├── _sidebar.zh.md          # 中文侧边栏
├── _navbar.md              # 英文导航栏
├── _navbar.zh.md           # 中文导航栏
├── 404.md                  # 404 页面
├── .nojekyll               # GitHub Pages 配置
├── v1/                     # v1 版本文档
│   ├── en-us/              # 英文文档
│   │   ├── README.md
│   │   └── CHANGELOG.md
│   └── zh-cn/              # 中文文档
│       ├── README.md
│       └── CHANGELOG.md
├── v2/                     # v2 版本文档
│   └── zh-cn/              # 中文文档
│       ├── readme.md
│       ├── api.md
│       ├── examples.md
│       └── changelog.md
└── latest/                 # 最新版本文档（v2 的副本）
    └── zh-cn/              # 中文文档
        ├── readme.md
        ├── api.md
        ├── examples.md
        └── changelog.md
```

## 多语言支持

文档支持中英文切换：
- 访问包含 `/zh-cn/` 路径的页面时，自动加载中文侧边栏和导航栏
- 访问包含 `/en-us/` 路径的页面时，自动加载英文侧边栏和导航栏
- 访问 `README_zh.md` 时，自动加载中文界面
- 通过导航栏可以快速切换语言

## 部署到 GitHub Pages

1. 将 `docs` 目录推送到 GitHub
2. 在仓库设置中启用 GitHub Pages
3. 选择 `docs` 目录作为源目录
4. 访问 `https://yourusername.github.io/asmysql/` 查看文档

## 功能特性

- ✅ 多语言支持（中英文）
- ✅ 搜索功能
- ✅ 代码高亮
- ✅ 代码复制
- ✅ 分页导航
- ✅ 图片缩放
- ✅ 响应式设计
