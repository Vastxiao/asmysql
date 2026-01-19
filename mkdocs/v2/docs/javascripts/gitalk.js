(function () {
    'use strict';

    // 从 MkDocs 配置中获取 Gitalk 参数
    function getGitalkConfig() {
        // 尝试从 window 对象获取配置（如果通过脚本注入）
        if (window.mkdocs && window.mkdocs.gitalk) {
            return window.mkdocs.gitalk;
        }

        // 尝试从 meta 标签获取配置
        const metaConfig = document.querySelector('meta[name="gitalk-config"]');
        if (metaConfig) {
            try {
                return JSON.parse(metaConfig.getAttribute('content'));
            } catch (e) {
                console.warn('Failed to parse Gitalk config from meta tag:', e);
            }
        }

        // 默认配置
        return {
            owner: 'vastxiao',
            repo: 'asmysql',
            admin: ['vastxiao'],
            client_id: '',
            client_secret: '',
            language: 'zh-CN',
            distraction_free_mode: false,
            create_issue_manually: false,
            labels: ['Gitalk']
        };
    }

    // 创建 Gitalk 容器
    function createGitalkContainer() {
        const mainContent = document.querySelector('.md-content__inner');
        if (!mainContent) {
            return null;
        }

        // 检查是否已存在容器
        let container = document.getElementById('gitalk-container');
        if (container) {
            return container;
        }

        // 创建容器
        container = document.createElement('div');
        container.id = 'gitalk-container';
        mainContent.appendChild(container);
        return container;
    }

    // 等待 Gitalk 库加载完成
    function initGitalk() {
        if (typeof Gitalk === 'undefined') {
            setTimeout(initGitalk, 100);
            return;
        }

        const config = getGitalkConfig();

        // 如果没有配置 client_id，不初始化
        if (!config.client_id || config.client_id.trim() === '') {
            console.warn('Gitalk: client_id is not configured. Please set it in mkdocs.yml');
            return;
        }

        // 创建容器
        const container = createGitalkContainer();
        if (!container) {
            return;
        }

        // 生成唯一 ID（基于页面路径）
        const path = window.location.pathname;
        const pathId = path.replace(/\/$/, '').replace(/\//g, '-').replace(/^-/, '') || 'index';

        // 构建 Gitalk 配置
        const gitalkConfig = {
            id: pathId,
            owner: config.owner || 'vastxiao',
            repo: config.repo || 'asmysql',
            admin: Array.isArray(config.admin) ? config.admin : [config.admin || 'vastxiao'],
            clientID: config.client_id,
            clientSecret: config.client_secret || '',
            language: config.language || 'zh-CN',
            distractionFreeMode: config.distraction_free_mode === true,
            createIssueManually: config.create_issue_manually === true,
            labels: Array.isArray(config.labels) ? config.labels : [config.labels || 'Gitalk'],
            title: document.title
        };

        try {
            const gitalk = new Gitalk(gitalkConfig);
            gitalk.render('gitalk-container');
        } catch (error) {
            console.error('Failed to initialize Gitalk:', error);
        }
    }

    // 页面加载完成后初始化
    function setupGitalk() {
        // 等待 DOM 和配置都准备好
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function () {
                setTimeout(initGitalk, 500);
            });
        } else {
            setTimeout(initGitalk, 500);
        }
    }

    // 如果使用 instant loading，需要在导航后重新初始化
    document.addEventListener('DOMContentLoaded', function () {
        setupGitalk();

        const observer = new MutationObserver(function () {
            const container = document.getElementById('gitalk-container');
            if (container && !container.hasChildNodes()) {
                // 清除旧的容器，重新创建
                if (container.parentNode) {
                    container.parentNode.removeChild(container);
                }
                setTimeout(initGitalk, 300);
            }
        });

        const mainContent = document.querySelector('.md-content__inner');
        if (mainContent) {
            observer.observe(mainContent, { childList: true, subtree: true });
        }
    });

    // 立即执行一次（如果 DOM 已准备好）
    if (document.readyState !== 'loading') {
        setupGitalk();
    }
})();

