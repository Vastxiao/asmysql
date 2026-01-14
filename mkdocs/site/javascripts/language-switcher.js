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
    'zh/v2/index.md': { 'zh-cn': 'zh/v2/index.md', 'en-us': 'en/v2/index.md' },
    'zh/v2/installation.md': { 'zh-cn': 'zh/v2/installation.md', 'en-us': 'en/v2/installation.md' },
    'zh/v2/quickstart.md': { 'zh-cn': 'zh/v2/quickstart.md', 'en-us': 'en/v2/quickstart.md' },
    'zh/v2/connection.md': { 'zh-cn': 'zh/v2/connection.md', 'en-us': 'en/v2/connection.md' },
    'zh/v2/query.md': { 'zh-cn': 'zh/v2/query.md', 'en-us': 'en/v2/query.md' },
    'zh/v2/result.md': { 'zh-cn': 'zh/v2/result.md', 'en-us': 'en/v2/result.md' },
    'zh/v2/transaction.md': { 'zh-cn': 'zh/v2/transaction.md', 'en-us': 'en/v2/transaction.md' },
    'zh/v2/business-logic.md': { 'zh-cn': 'zh/v2/business-logic.md', 'en-us': 'en/v2/business-logic.md' },
    'zh/v2/best-practices.md': { 'zh-cn': 'zh/v2/best-practices.md', 'en-us': 'en/v2/best-practices.md' },
    'zh/v2/faq.md': { 'zh-cn': 'zh/v2/faq.md', 'en-us': 'en/v2/faq.md' },
    'zh/v2/api.md': { 'zh-cn': 'zh/v2/api.md', 'en-us': 'en/v2/api.md' },
    'zh/v2/examples.md': { 'zh-cn': 'zh/v2/examples.md', 'en-us': 'en/v2/examples.md' },
    'zh/v2/changelog.md': { 'zh-cn': 'zh/v2/changelog.md', 'en-us': 'en/v2/changelog.md' },
    'en/v2/index.md': { 'zh-cn': 'zh/v2/index.md', 'en-us': 'en/v2/index.md' },
    'en/v2/installation.md': { 'zh-cn': 'zh/v2/installation.md', 'en-us': 'en/v2/installation.md' },
    'en/v2/quickstart.md': { 'zh-cn': 'zh/v2/quickstart.md', 'en-us': 'en/v2/quickstart.md' },
    'en/v2/connection.md': { 'zh-cn': 'zh/v2/connection.md', 'en-us': 'en/v2/connection.md' },
    'en/v2/query.md': { 'zh-cn': 'zh/v2/query.md', 'en-us': 'en/v2/query.md' },
    'en/v2/result.md': { 'zh-cn': 'zh/v2/result.md', 'en-us': 'en/v2/result.md' },
    'en/v2/transaction.md': { 'zh-cn': 'zh/v2/transaction.md', 'en-us': 'en/v2/transaction.md' },
    'en/v2/business-logic.md': { 'zh-cn': 'zh/v2/business-logic.md', 'en-us': 'en/v2/business-logic.md' },
    'en/v2/best-practices.md': { 'zh-cn': 'zh/v2/best-practices.md', 'en-us': 'en/v2/best-practices.md' },
    'en/v2/faq.md': { 'zh-cn': 'zh/v2/faq.md', 'en-us': 'en/v2/faq.md' },
    'en/v2/api.md': { 'zh-cn': 'zh/v2/api.md', 'en-us': 'en/v2/api.md' },
    'en/v2/examples.md': { 'zh-cn': 'zh/v2/examples.md', 'en-us': 'en/v2/examples.md' },
    'en/v2/changelog.md': { 'zh-cn': 'zh/v2/changelog.md', 'en-us': 'en/v2/changelog.md' },
    'zh/v1/index.md': { 'zh-cn': 'zh/v1/index.md', 'en-us': 'en/v1/index.md' },
    'zh/v1/CHANGELOG.md': { 'zh-cn': 'zh/v1/CHANGELOG.md', 'en-us': 'en/v1/CHANGELOG.md' },
    'en/v1/index.md': { 'zh-cn': 'zh/v1/index.md', 'en-us': 'en/v1/index.md' },
    'en/v1/CHANGELOG.md': { 'zh-cn': 'zh/v1/CHANGELOG.md', 'en-us': 'en/v1/CHANGELOG.md' }
  };

  /**
   * 从当前 URL 检测语言
   */
  function detectCurrentLanguage() {
    const path = window.location.pathname;
    if (path.includes('/en/')) {
      return 'en-us';
    } else if (path.includes('/zh/')) {
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
    if (!pagePath.startsWith('zh/') && !pagePath.startsWith('en/') && pagePath !== 'index.md') {
      // 如果路径不包含语言信息，可能是根路径下的页面
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
        window.location.href = baseUrl + repoPath + 'zh/v2/';
      } else {
        window.location.href = baseUrl + repoPath + 'en/v2/';
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
      if (path.includes('zh/v2/') || path.includes('en/v2/')) {
        let newPath = path;
        
        if (currentLang === 'en-us' && path.includes('zh/v2/')) {
          newPath = path.replace('zh/v2/', 'en/v2/');
        } else if (currentLang === 'zh-cn' && path.includes('en/v2/')) {
          newPath = path.replace('en/v2/', 'zh/v2/');
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
