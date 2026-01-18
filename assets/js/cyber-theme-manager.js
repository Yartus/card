/**
 * WeCard 科幻主题管理系统
 * 动态主题切换和颜色配置
 */

class CyberThemeManager {
  constructor() {
    this.currentTheme = 'cyber';
    this.themes = {
      cyber: {
        name: '青蓝科技',
        description: '经典科幻风格，青色霓虹光效',
        colors: {
          primary: '#00ffff',
          secondary: '#0099cc',
          accent: '#ff00ff',
          background: {
            primary: '#0a0a0a',
            secondary: '#1a1a2e',
            tertiary: '#16213e'
          }
        }
      },
      energy: {
        name: '橙红能量',
        description: '活力四射，橙红色能量光效',
        colors: {
          primary: '#ff6b35',
          secondary: '#cc5529',
          accent: '#ffaa00',
          background: {
            primary: '#0a0a0a',
            secondary: '#2e1a1a',
            tertiary: '#3e2116'
          }
        }
      },
      mystic: {
        name: '紫色神秘',
        description: '神秘优雅，紫色魔幻光效',
        colors: {
          primary: '#8a2be2',
          secondary: '#6a1b9a',
          accent: '#e91e63',
          background: {
            primary: '#0a0a0a',
            secondary: '#1a0a2e',
            tertiary: '#2e1a3e'
          }
        }
      },
      matrix: {
        name: '绿色矩阵',
        description: '黑客风格，绿色矩阵光效',
        colors: {
          primary: '#00ff41',
          secondary: '#00cc33',
          accent: '#39ff14',
          background: {
            primary: '#0a0a0a',
            secondary: '#0a2e0a',
            tertiary: '#162e16'
          }
        }
      }
    };
    
    this.init();
  }
  
  /**
   * 初始化主题系统
   */
  init() {
    // 从localStorage读取保存的主题
    const savedTheme = localStorage.getItem('wecard-theme');
    if (savedTheme && this.themes[savedTheme]) {
      this.currentTheme = savedTheme;
    }
    
    // 应用主题
    this.applyTheme(this.currentTheme);
    
    // 监听主题切换事件
    this.bindEvents();
  }
  
  /**
   * 应用主题
   * @param {string} themeName - 主题名称
   */
  applyTheme(themeName) {
    if (!this.themes[themeName]) {
      console.warn(`主题 "${themeName}" 不存在`);
      return;
    }
    
    // 设置data-theme属性
    document.documentElement.setAttribute('data-theme', themeName);
    
    // 更新当前主题
    this.currentTheme = themeName;
    
    // 保存到localStorage
    localStorage.setItem('wecard-theme', themeName);
    
    // 触发主题变更事件
    this.dispatchThemeChangeEvent(themeName);
    
    console.log(`已切换到主题: ${this.themes[themeName].name}`);
  }
  
  /**
   * 获取当前主题
   * @returns {Object} 当前主题配置
   */
  getCurrentTheme() {
    return {
      name: this.currentTheme,
      config: this.themes[this.currentTheme]
    };
  }
  
  /**
   * 获取所有可用主题
   * @returns {Object} 所有主题配置
   */
  getAllThemes() {
    return this.themes;
  }
  
  /**
   * 切换到下一个主题
   */
  nextTheme() {
    const themeNames = Object.keys(this.themes);
    const currentIndex = themeNames.indexOf(this.currentTheme);
    const nextIndex = (currentIndex + 1) % themeNames.length;
    const nextTheme = themeNames[nextIndex];
    
    this.applyTheme(nextTheme);
  }
  
  /**
   * 自定义颜色配置
   * @param {Object} customColors - 自定义颜色配置
   */
  setCustomColors(customColors) {
    const root = document.documentElement;
    
    // 应用自定义颜色到CSS变量
    if (customColors.primary) {
      root.style.setProperty('--primary-color', customColors.primary);
    }
    if (customColors.secondary) {
      root.style.setProperty('--secondary-color', customColors.secondary);
    }
    if (customColors.accent) {
      root.style.setProperty('--accent-color', customColors.accent);
    }
    
    // 更新边框和光晕颜色
    if (customColors.primary) {
      const primaryRgb = this.hexToRgb(customColors.primary);
      root.style.setProperty('--border-color', `rgba(${primaryRgb.r}, ${primaryRgb.g}, ${primaryRgb.b}, 0.2)`);
      root.style.setProperty('--border-hover', `rgba(${primaryRgb.r}, ${primaryRgb.g}, ${primaryRgb.b}, 0.4)`);
      root.style.setProperty('--border-active', `rgba(${primaryRgb.r}, ${primaryRgb.g}, ${primaryRgb.b}, 0.6)`);
      root.style.setProperty('--glow-color', `rgba(${primaryRgb.r}, ${primaryRgb.g}, ${primaryRgb.b}, 0.3)`);
      root.style.setProperty('--glow-intense', `rgba(${primaryRgb.r}, ${primaryRgb.g}, ${primaryRgb.b}, 0.5)`);
    }
    
    console.log('已应用自定义颜色配置');
  }
  
  /**
   * 重置为默认主题
   */
  resetToDefault() {
    this.applyTheme('cyber');
  }
  
  /**
   * 绑定事件监听
   */
  bindEvents() {
    // 监听主题切换按钮
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-theme-switch]')) {
        const targetTheme = e.target.getAttribute('data-theme-switch');
        this.applyTheme(targetTheme);
      }
      
      if (e.target.matches('[data-theme-next]')) {
        this.nextTheme();
      }
    });
    
    // 监听键盘快捷键 (Ctrl + T)
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        this.nextTheme();
      }
    });
  }
  
  /**
   * 触发主题变更事件
   * @param {string} themeName - 新主题名称
   */
  dispatchThemeChangeEvent(themeName) {
    const event = new CustomEvent('themeChange', {
      detail: {
        theme: themeName,
        config: this.themes[themeName]
      }
    });
    document.dispatchEvent(event);
  }
  
  /**
   * 创建主题选择器UI
   * @param {string} containerId - 容器元素ID
   */
  createThemeSelector(containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.warn(`容器 #${containerId} 不存在`);
      return;
    }
    
    const selectorHTML = `
      <div class="cyber-theme-selector">
        <h3 class="cyber-subtitle">主题选择</h3>
        <div class="theme-grid">
          ${Object.entries(this.themes).map(([key, theme]) => `
            <div class="theme-option ${key === this.currentTheme ? 'active' : ''}" 
                 data-theme-switch="${key}">
              <div class="theme-preview" style="background: ${theme.colors.primary}"></div>
              <div class="theme-info">
                <div class="theme-name">${theme.name}</div>
                <div class="theme-desc">${theme.description}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    
    container.innerHTML = selectorHTML;
    
    // 添加样式
    this.injectThemeSelectorStyles();
  }
  
  /**
   * 注入主题选择器样式
   */
  injectThemeSelectorStyles() {
    if (document.getElementById('theme-selector-styles')) return;
    
    const styles = `
      <style id="theme-selector-styles">
        .cyber-theme-selector {
          padding: 20px;
          background: var(--glass-bg);
          border: 1px solid var(--border-color);
          border-radius: 12px;
          backdrop-filter: blur(15px);
        }
        
        .theme-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-top: 16px;
        }
        
        .theme-option {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          border: 1px solid var(--border-color);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
          background: var(--overlay-bg);
        }
        
        .theme-option:hover {
          border-color: var(--border-hover);
          transform: translateY(-2px);
          box-shadow: 0 4px 15px var(--glow-color);
        }
        
        .theme-option.active {
          border-color: var(--primary-color);
          box-shadow: 0 0 20px var(--glow-intense);
        }
        
        .theme-preview {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          box-shadow: 0 0 15px currentColor;
        }
        
        .theme-info {
          flex: 1;
        }
        
        .theme-name {
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 4px;
        }
        
        .theme-desc {
          font-size: 12px;
          color: var(--text-muted);
        }
      </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', styles);
  }
  
  /**
   * 工具方法：HEX转RGB
   * @param {string} hex - HEX颜色值
   * @returns {Object} RGB颜色值
   */
  hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }
  
  /**
   * 工具方法：RGB转HEX
   * @param {number} r - 红色值
   * @param {number} g - 绿色值
   * @param {number} b - 蓝色值
   * @returns {string} HEX颜色值
   */
  rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }
}

// 全局实例
window.CyberTheme = new CyberThemeManager();

// 导出给模块使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CyberThemeManager;
}

// Vue.js 插件支持
if (typeof window !== 'undefined' && window.Vue) {
  window.Vue.prototype.$cyberTheme = window.CyberTheme;
}

console.log('🎨 WeCard 科幻主题系统已加载');
