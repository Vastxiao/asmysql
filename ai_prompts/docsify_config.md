# Docsify 文档配置系统 - AI 维护指南

## 功能概述

本项目使用 Docsify 构建多语言文档系统，支持中英文自动切换。文档系统基于 Docsify v4，提供搜索、代码高亮、分页导航等功能。

## 目录结构

```
docs/
├── index.html              # Docsify 主配置文件（核心配置）
├── README.md               # 英文首页
├── README_zh.md            # 中文首页
├── _sidebar.md             # 英文侧边栏导航
├── _sidebar.zh.md          # 中文侧边栏导航
├── _navbar.md              # 英文顶部导航栏
├── _navbar.zh.md           # 中文顶部导航栏
├── 404.md                  # 404 错误页面
├── .nojekyll               # GitHub Pages 配置文件（空文件）
├── README_DOCSIFY.md        # 使用说明文档
│
├── v1/                     # v1 版本文档
│   ├── en-us/              # 英文文档
│   │   ├── README.md
│   │   └── CHANGELOG.md
│   └── zh-cn/              # 中文文档
│       ├── README.md
│       └── CHANGELOG.md
│
├── v2/                     # v2 版本文档（当前最新版本）
│   └── zh-cn/              # 中文文档（v2 目前只有中文版）
│       ├── readme.md
│       ├── api.md
│       ├── examples.md
│       └── changelog.md
│
└── latest/                 # 最新版本文档（v2 的副本，用于指向最新版本）
    └── zh-cn/
        ├── readme.md
        ├── api.md
        ├── examples.md
        └── changelog.md
```

## 核心配置文件说明

### 1. index.html - 主配置文件

**位置**: `docs/index.html`

**关键配置项**:
- `name`: 文档名称 'asmysql'
- `repo`: GitHub 仓库地址
- `loadSidebar`: 启用侧边栏
- `loadNavbar`: 启用导航栏
- `homepage`: 默认首页 'README.md'
- `routerMode`: 'history' 模式（支持 SEO）
- `search`: 搜索功能配置
- `pagination`: 分页导航配置

**多语言自动切换插件**:
- 通过自定义插件实现根据路径自动切换侧边栏和导航栏
- 检测逻辑：
  - 路径包含 `/zh-cn/` → 加载中文界面
  - 路径包含 `/en-us/` → 加载英文界面
  - 路径包含 `README_zh.md` → 加载中文界面
  - `v2/` 和 `latest/` 目录（默认只有中文）→ 加载中文界面

**已启用的插件**:
- Docsify v4 核心
- 搜索插件 (search.min.js)
- 代码高亮 (Prism.js - Python, Bash)
- 代码复制 (docsify-copy-code)
- 分页导航 (docsify-pagination)
- 图片缩放 (zoom-image)
- 表情符号 (emoji)
- 外部脚本 (external-script)

### 2. _sidebar.md / _sidebar.zh.md - 侧边栏导航

**位置**: `docs/_sidebar.md` (英文), `docs/_sidebar.zh.md` (中文)

**格式**: Markdown 列表格式
- 使用 `*` 创建一级菜单
- 使用缩进创建二级菜单
- 链接格式: `[显示文本](相对路径)`

**维护规则**:
- 英文侧边栏链接指向 `en-us/` 目录下的文档
- 中文侧边栏链接指向 `zh-cn/` 目录下的文档
- 添加新文档时，需要同时更新两个侧边栏文件
- 保持中英文侧边栏结构一致

### 3. _navbar.md / _navbar.zh.md - 顶部导航栏

**位置**: `docs/_navbar.md` (英文), `docs/_navbar.zh.md` (中文)

**内容**: 语言切换链接和外部资源链接

### 4. README.md / README_zh.md - 首页

**位置**: `docs/README.md` (英文), `docs/README_zh.md` (中文)

**作用**: 文档入口页面，包含快速导航链接

**维护规则**:
- 保持中英文内容对应
- 链接路径需要指向正确的语言版本目录
- 更新版本信息时同步更新两个文件

## 多语言支持机制

### 语言检测逻辑

系统通过路径检测自动切换语言界面：

```javascript
// 检测是否为中文路径
var isZh = path.includes('/zh-cn/') ||           // 包含中文目录
          path.includes('README_zh.md') ||       // 中文首页
          path === '/README_zh.md' ||            // 中文首页路径
          (!path.includes('/en-us/') &&          // 不包含英文目录
           (path.startsWith('/v2/') ||           // v2 目录（默认中文）
            path.startsWith('/latest/')));       // latest 目录（默认中文）
```

### 文件命名规范

1. **语言目录结构**:
   - 英文文档: `{version}/en-us/{filename}.md`
   - 中文文档: `{version}/zh-cn/{filename}.md`

2. **首页文件**:
   - 英文: `README.md`
   - 中文: `README_zh.md`

3. **侧边栏和导航栏**:
   - 英文: `_sidebar.md`, `_navbar.md`
   - 中文: `_sidebar.zh.md`, `_navbar.zh.md`

### 添加新语言版本

1. 创建新的语言目录（如 `ja-jp/` 用于日语）
2. 创建对应的侧边栏文件（如 `_sidebar.ja.md`）
3. 创建对应的导航栏文件（如 `_navbar.ja.md`）
4. 更新 `index.html` 中的语言检测逻辑

## 维护操作指南

### 添加新文档

1. **创建文档文件**:
   ```bash
   # 在对应版本和语言目录下创建文件
   docs/v2/zh-cn/new-doc.md
   docs/v2/en-us/new-doc.md  # 如果有英文版
   ```

2. **更新侧边栏**:
   - 编辑 `_sidebar.md` 和 `_sidebar.zh.md`
   - 在对应版本章节下添加新链接
   - 保持中英文结构一致

3. **更新首页**（如需要）:
   - 在 `README.md` 和 `README_zh.md` 中添加快速链接

### 添加新版本

1. **创建版本目录**:
   ```bash
   docs/v3/
   ├── en-us/
   └── zh-cn/
   ```

2. **更新侧边栏**:
   - 在 `_sidebar.md` 和 `_sidebar.zh.md` 中添加新版本章节
   - 更新 "Latest" 章节指向新版本

3. **更新首页**:
   - 更新 `README.md` 和 `README_zh.md` 中的版本信息

### 修改多语言检测逻辑

编辑 `docs/index.html` 中的 `updateSidebarAndNavbar` 函数：

```javascript
function updateSidebarAndNavbar(vm) {
  var path = vm.route.path;
  // 修改这里的检测逻辑
  var isZh = /* 你的检测逻辑 */;
  
  var sidebarFile = isZh ? '_sidebar.zh.md' : '_sidebar.md';
  var navbarFile = isZh ? '_navbar.zh.md' : '_navbar.md';
  // ...
}
```

### 更新插件配置

在 `docs/index.html` 中修改 `window.$docsify` 配置对象：

```javascript
window.$docsify = {
  // 修改配置项
  search: { /* 搜索配置 */ },
  pagination: { /* 分页配置 */ },
  // ...
}
```

## 启动和部署

### 本地开发

```bash
# 在 docs 目录下运行
cd docs
docsify serve .

# 或使用全局命令
docsify serve docs
```

访问: `http://localhost:3000`

### GitHub Pages 部署

1. 确保 `docs/.nojekyll` 文件存在（空文件即可）
2. 在 GitHub 仓库设置中启用 Pages
3. 选择 `docs` 目录作为源目录
4. 访问: `https://{username}.github.io/{repo}/`

## 常见问题处理

### 侧边栏不显示

- 检查 `_sidebar.md` 或 `_sidebar.zh.md` 文件是否存在
- 检查文件格式是否正确（Markdown 列表格式）
- 检查链接路径是否正确

### 多语言切换不工作

- 检查 `index.html` 中的语言检测逻辑
- 检查路径是否包含正确的语言标识（`/zh-cn/` 或 `/en-us/`）
- 检查浏览器控制台是否有 JavaScript 错误

### 搜索功能不工作

- 确保 `search.min.js` 插件已加载
- 检查 `search.paths` 配置是否正确
- 清除浏览器缓存后重试

### 代码高亮不显示

- 确保 Prism.js 相关脚本已加载
- 检查代码块是否使用正确的语言标识（如 `python`, `bash`）
- 确保代码块使用三个反引号格式

## 最佳实践

1. **保持结构一致**: 中英文文档目录结构应保持一致
2. **及时更新链接**: 添加新文档后立即更新侧边栏和首页链接
3. **测试多语言**: 添加内容后测试中英文界面是否正常切换
4. **版本管理**: 新版本发布时及时更新 "Latest" 章节
5. **文档规范**: 遵循 Markdown 规范，确保文档格式正确

## 相关文件清单

- 主配置: `docs/index.html`
- 侧边栏: `docs/_sidebar.md`, `docs/_sidebar.zh.md`
- 导航栏: `docs/_navbar.md`, `docs/_navbar.zh.md`
- 首页: `docs/README.md`, `docs/README_zh.md`
- 说明文档: `docs/README_DOCSIFY.md`

## 技术栈

- **Docsify**: v4
- **主题**: Vue 主题
- **代码高亮**: Prism.js
- **搜索**: Docsify 内置搜索
- **部署**: GitHub Pages

---

**最后更新**: 2024年
**维护者**: 开发团队
**相关文档**: [Docsify 官方文档](https://docsify.js.org/)
