(function() {
  'use strict';

  // 语言映射配置
  const languageMap = {
    'zh-cn': { name: '中文', icon: 'material/translate' },
    'en-us': { name: 'English', icon: 'material/translate' }
  };

  // 页面路径映射（用于在不同语言版本间切换）
  const pageMap = {
    'index.md': { 'zh-cn': 'index.md', 'en-us': 'index.md' },
    'v2/zh-cn/index.md': { 'zh-cn': 'v2/zh-cn/index.md', 'en-us': 'v2/en-us/index.md' },
    'v2/zh-cn/installation.md': { 'zh-cn': 'v2/zh-cn/installation.md', 'en-us': 'v2/en-us/installation.md' },
    'v2/zh-cn/quickstart.md': { 'zh-cn': 'v2/zh-cn/quickstart.md', 'en-us': 'v2/en-us/quickstart.md' },
    'v2/zh-cn/connection.md': { 'zh-cn': 'v2/zh-cn/connection.md', 'en-us': 'v2/en-us/connection.md' },
    'v2/zh-cn/query.md': { 'zh-cn': 'v2/zh-cn/query.md', 'en-us': 'v2/en-us/query.md' },
    'v2/zh-cn/result.md': { 'zh-cn': 'v2/zh-cn/result.md', 'en-us': 'v2/en-us/result.md' },
    'v2/zh-cn/transaction.md': { 'zh-cn': 'v2/zh-cn/transaction.md', 'en-us': 'v2/en-us/transaction.md' },
    'v2/zh-cn/business-logic.md': { 'zh-cn': 'v2/zh-cn/business-logic.md', 'en-us': 'v2/en-us/business-logic.md' },
    'v2/zh-cn/best-practices.md': { 'zh-cn': 'v2/zh-cn/best-practices.md', 'en-us': 'v2/en-us/best-practices.md' },
    'v2/zh-cn/faq.md': { 'zh-cn': 'v2/zh-cn/faq.md', 'en-us': 'v2/en-us/faq.md' },
    'v2/zh-cn/api.md': { 'zh-cn': 'v2/zh-cn/api.md', 'en-us': 'v2/en-us/api.md' },
    'v2/zh-cn/examples.md': { 'zh-cn': 'v2/zh-cn/examples.md', 'en-us': 'v2/en-us/examples.md' },
    'v2/zh-cn/changelog.md': { 'zh-cn': 'v2/zh-cn/changelog.md', 'en-us': 'v2/en-us/changelog.md' },
    'v2/en-us/index.md': { 'zh-cn': 'v2/zh-cn/index.md', 'en-us': 'v2/en-us/index.md' },
    'v2/en-us/installation.md': { 'zh-cn': 'v2/zh-cn/installation.md', 'en-us': 'v2/en-us/installation.md' },
    'v2/en-us/quickstart.md': { 'zh-cn': 'v2/zh-cn/quickstart.md', 'en-us': 'v2/en-us/quickstart.md' },
    'v2/en-us/connection.md': { 'zh-cn': 'v2/zh-cn/connection.md', 'en-us': 'v2/en-us/connection.md' },
    'v2/en-us/query.md': { 'zh-cn': 'v2/zh-cn/query.md', 'en-us': 'v2/en-us/query.md' },
    'v2/en-us/result.md': { 'zh-cn': 'v2/zh-cn/result.md', 'en-us': 'v2/en-us/result.md' },
    'v2/en-us/transaction.md': { 'zh-cn': 'v2/zh-cn/transaction.md', 'en-us': 'v2/en-us/transaction.md' },
    'v2/en-us/business-logic.md': { 'zh-cn': 'v2/zh-cn/business-logic.md', 'en-us': 'v2/en-us/business-logic.md' },
    'v2/en-us/best-practices.md': { 'zh-cn': 'v2/zh-cn/best-practices.md', 'en-us': 'v2/en-us/best-practices.md' },
    'v2/en-us/faq.md': { 'zh-cn': 'v2/zh-cn/faq.md', 'en-us': 'v2/en-us/faq.md' },
    'v2/en-us/api.md': { 'zh-cn': 'v2/zh-cn/api.md', 'en-us': 'v2/en-us/api.md' },
    'v2/en-us/examples.md': { 'zh-cn': 'v2/zh-cn/examples.md', 'en-us': 'v2/en-us/examples.md' },
    'v2/en-us/changelog.md': { 'zh-cn': 'v2/zh-cn/changelog.md', 'en-us': 'v2/en-us/changelog.md' },
    'v1/zh-cn/index.md': { 'zh-cn': 'v1/zh-cn/index.md', 'en-us': 'v1/en-us/index.md' },
    'v1/zh-cn/CHANGELOG.md': { 'zh-cn': 'v1/zh-cn/CHANGELOG.md', 'en-us': 'v1/en-us/CHANGELOG.md' },
    'v1/en-us/index.md': { 'zh-cn': 'v1/zh-cn/index.md', 'en-us': 'v1/en-us/index.md' },
    'v1/en-us/CHANGELOG.md': { 'zh-cn': 'v1/zh-cn/CHANGELOG.md', 'en-us': 'v1/en-us/CHANGELOG.md' }
  };

  /**
   * 从当前 URL 检测语言
   */
  function detectCurrentLanguage() {
    const path = window.location.pathname;
    if (path.includes('/en-us/')) {
      return 'en-us';
    } else if (path.includes('/zh-cn/')) {
      return 'zh-cn';
    }
    // 默认返回中文
    return 'zh-cn';
  }

  /**
   * 获取当前页面对应的文件路径
   */
  function getCurrentPagePath() {
    const path = window.location.pathname;
    // 移除基础路径和尾部斜杠
    let pagePath = path.replace(/^\/asmysql\/?/, '').replace(/\/$/, '');
    
    // 如果是首页
    if (!pagePath || pagePath === '') {
      return 'index.md';
    }
    
    // 处理路径
    if (pagePath.endsWith('.html')) {
      pagePath = pagePath.replace('.html', '.md');
    } else if (!pagePath.endsWith('.md')) {
      // 如果路径不以 .md 结尾，可能是目录，添加 index.md
      pagePath += '/index.md';
    }
    
    // 确保路径格式正确
    if (!pagePath.startsWith('v1/') && !pagePath.startsWith('v2/') && pagePath !== 'index.md') {
      // 如果路径不包含版本信息，可能是根路径下的页面
      return pagePath;
    }
    
    return pagePath;
  }

  /**
   * 切换语言
   */
  function switchLanguage(targetLang) {
    const currentLang = detectCurrentLanguage();
    if (currentLang === targetLang) {
      return;
    }

    const currentPath = getCurrentPagePath();
    const targetPath = pageMap[currentPath]?.[targetLang];
    
    if (targetPath) {
      // 构建新的 URL
      const baseUrl = window.location.origin;
      const repoPath = '/asmysql/';
      let newPath = baseUrl + repoPath + targetPath.replace('.md', '/');
      
      // 如果是首页，直接跳转到首页
      if (targetPath === 'index.md') {
        newPath = baseUrl + repoPath;
      }
      
      window.location.href = newPath;
    } else {
      // 如果没有找到对应页面，跳转到对应语言的首页
      const baseUrl = window.location.origin;
      const repoPath = '/asmysql/';
      if (targetLang === 'zh-cn') {
        window.location.href = baseUrl + repoPath + 'v2/zh-cn/';
      } else {
        window.location.href = baseUrl + repoPath + 'v2/en-us/';
      }
    }
  }

  /**
   * 更新导航栏链接以匹配当前语言
   */
  function updateNavigationLinks() {
    const currentLang = detectCurrentLanguage();
    const navLinks = document.querySelectorAll('.md-nav__link[href]');
    
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (!href) return;
      
      // 移除查询参数和锚点
      const path = href.split('?')[0].split('#')[0];
      
      // 检查是否是 v2 文档链接
      if (path.includes('v2/zh-cn/') || path.includes('v2/en-us/')) {
        let newPath = path;
        
        if (currentLang === 'en-us' && path.includes('v2/zh-cn/')) {
          newPath = path.replace('v2/zh-cn/', 'v2/en-us/');
        } else if (currentLang === 'zh-cn' && path.includes('v2/en-us/')) {
          newPath = path.replace('v2/en-us/', 'v2/zh-cn/');
        }
        
        if (newPath !== path) {
          const newHref = href.replace(path, newPath);
          link.setAttribute('href', newHref);
        }
      }
    });
  }

  /**
   * 创建语言切换器
   */
  function createLanguageSwitcher() {
    const currentLang = detectCurrentLanguage();
    const header = document.querySelector('.md-header');
    
    if (!header) {
      return;
    }

    // 检查是否已经存在语言切换器
    if (header.querySelector('.md-header__language-switcher')) {
      return;
    }

    // 创建语言切换器容器
    const switcherContainer = document.createElement('div');
    switcherContainer.className = 'md-header__language-switcher';
    
    // 创建下拉框
    const select = document.createElement('select');
    select.className = 'md-header__language-select';
    select.setAttribute('aria-label', '选择语言');
    
    // 添加选项
    Object.keys(languageMap).forEach(lang => {
      const option = document.createElement('option');
      option.value = lang;
      option.textContent = languageMap[lang].name;
      if (lang === currentLang) {
        option.selected = true;
      }
      select.appendChild(option);
    });
    
    // 添加事件监听
    select.addEventListener('change', function(e) {
      switchLanguage(e.target.value);
    });
    
    switcherContainer.appendChild(select);
    
    // 插入到 header 中（在搜索框之前）
    const searchButton = header.querySelector('[data-md-component="search"]');
    if (searchButton && searchButton.parentElement) {
      searchButton.parentElement.insertBefore(switcherContainer, searchButton);
    } else {
      header.appendChild(switcherContainer);
    }
    
    // 更新导航链接
    updateNavigationLinks();
  }

  // 等待 DOM 加载完成
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      createLanguageSwitcher();
      updateNavigationLinks();
    });
  } else {
    createLanguageSwitcher();
    updateNavigationLinks();
  }

  // 如果使用 instant loading，需要在导航后重新创建和更新
  document.addEventListener('DOMContentLoaded', function() {
    const observer = new MutationObserver(function(mutations) {
      if (!document.querySelector('.md-header__language-switcher')) {
        createLanguageSwitcher();
      }
      updateNavigationLinks();
    });
    
    const header = document.querySelector('.md-header');
    const nav = document.querySelector('.md-nav');
    if (header) {
      observer.observe(header, { childList: true, subtree: true });
    }
    if (nav) {
      observer.observe(nav, { childList: true, subtree: true });
    }
  });
})();
