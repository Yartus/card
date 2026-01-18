/**
 * 图标库配置
 * 管理系统中所有可用的图标资源
 * 
 * 图标存储路径: /static/icons/
 * 前端访问路径: /icons/${icon.file}
 * 
 * Nuxt会将 /static/ 目录直接映射到网站根路径
 * 因此 /static/icons/facebook.svg 可通过 /icons/facebook.svg 访问
 * 
 * 注意: 这些是SVG图标，用于名片中的图标选择
 *      不要与Logo图片和素材库封面图片混淆
 *      素材库封面必须使用真实的图片而不是图标
 */
export const SVG_ICONS = [
  // 基础通信
  { name: '电话', file: 'phone.svg', category: 'contact' },
  { name: '呼叫', file: 'call.svg', category: 'contact' },
  { name: '邮箱', file: 'email.svg', category: 'contact' },
  { name: '短信', file: 'sms.svg', category: 'contact' },
  { name: '短信0', file: 'sms0.svg', category: 'contact' },
  { name: '传真', file: 'fax.svg', category: 'contact' },
  { name: '传真1', file: 'fax1.svg', category: 'contact' },
  { name: '位置', file: 'location.svg', category: 'contact' },
  { name: '网站', file: 'website.svg', category: 'contact' },
  { name: '办公室', file: 'Office.svg', category: 'contact' },
  { name: '家', file: 'Home.svg', category: 'contact' },
  { name: '手机', file: 'Mobile.svg', category: 'contact' },
  
  // 社交媒体
  { name: 'Facebook', file: 'facebook.svg', category: 'social' },
  { name: 'Instagram', file: 'instagram.svg', category: 'social' },
  { name: 'Instagram1', file: 'instagram1.svg', category: 'social' },
  { name: 'LinkedIn', file: 'linkedin.svg', category: 'social' },
  { name: 'Twitter', file: 'twitter.svg', category: 'social' },
  { name: 'X', file: 'x.svg', category: 'social' },
  { name: 'YouTube', file: 'youtube.svg', category: 'social' },
  { name: 'TikTok', file: 'TikTok.svg', category: 'social' },
  { name: 'Snapchat', file: 'snapchat.svg', category: 'social' },
  { name: 'WhatsApp', file: 'whatsApp.svg', category: 'social' },
  { name: 'WeChat', file: 'WeChat.svg', category: 'social' },
  { name: 'Telegram', file: 'telegram.svg', category: 'social' },
  { name: 'Signal', file: 'Signal.svg', category: 'social' },
  { name: 'Discord', file: 'discord.svg', category: 'social' },
  { name: 'Messenger', file: 'messenger.svg', category: 'social' },
  { name: 'Messenger0', file: 'messenger0.svg', category: 'social' },
  { name: 'Viber', file: 'Viber.svg', category: 'social' },
  { name: 'Line', file: 'Line.svg', category: 'social' },
  { name: 'Zalo', file: 'Zalo.svg', category: 'social' },
  { name: 'Skype', file: 'Skype.svg', category: 'social' },
  { name: 'Threads', file: 'threads.svg', category: 'social' },
  { name: 'Siilo', file: 'Siilo.svg', category: 'social' },
  
  // 专业社交
  { name: 'GitHub', file: 'github.svg', category: 'professional' },
  { name: 'GitLab', file: 'gitlab.svg', category: 'professional' },
  { name: 'Codeberg', file: 'codeberg.svg', category: 'professional' },
  { name: 'Medium', file: 'medium.svg', category: 'professional' },
  { name: 'Dribbble', file: 'dribbble.svg', category: 'professional' },
  { name: 'Behance', file: 'behance.svg', category: 'professional' },
  { name: 'ArtStation', file: 'ArtStation.svg', category: 'professional' },
  
  // 社区平台
  { name: 'Reddit', file: 'reddit.svg', category: 'community' },
  { name: 'Quora', file: 'quora.svg', category: 'community' },
  { name: 'Mastodon', file: 'mastodon.svg', category: 'community' },
  { name: 'Diaspora', file: 'diaspora.svg', category: 'community' },
  { name: 'Friendica', file: 'friendica.svg', category: 'community' },
  { name: 'Pixelfed', file: 'pixelfed.svg', category: 'community' },
  { name: 'PeerTube', file: 'peertube.svg', category: 'community' },
  { name: 'Matrix', file: 'Matrix.svg', category: 'community' },
  { name: 'Skool', file: 'Skool.svg', category: 'community' },
  
  // 媒体娱乐
  { name: 'Spotify', file: 'spotify.svg', category: 'media' },
  { name: 'SoundCloud', file: 'soundcloud.svg', category: 'media' },
  { name: 'Vimeo', file: 'vimeo.svg', category: 'media' },
  { name: 'Twitch', file: 'twitch.svg', category: 'media' },
  { name: 'Tumblr', file: 'tumblr.svg', category: 'media' },
  { name: 'Pinterest', file: 'pinterest.svg', category: 'media' },
  { name: 'VK', file: 'vk.svg', category: 'media' },
  { name: 'Funkwhale', file: 'funkwhale.svg', category: 'media' },
  { name: '小红书', file: 'Little Red Book.svg', category: 'media' },
  
  // 支付与商务
  { name: 'PayPal', file: 'paypal.svg', category: 'payment' },
  { name: 'Venmo', file: 'Venmo.svg', category: 'payment' },
  { name: 'Cash App', file: 'Cash App.svg', category: 'payment' },
  { name: 'Square', file: 'Square.svg', category: 'payment' },
  { name: 'Bitcoin', file: 'bitcoin.svg', category: 'payment' },
  { name: 'Monero', file: 'monero.svg', category: 'payment' },
  { name: 'UPI', file: 'upi.svg', category: 'payment' },
  { name: 'Patreon', file: 'patreon.svg', category: 'payment' },
  { name: 'Gumroad', file: 'Gumroad.svg', category: 'payment' },
  { name: 'Open Collective', file: 'open-collective.svg', category: 'payment' },
  { name: 'Buy me a coffee', file: 'Buy me a coffee.svg', category: 'payment' },
  { name: 'Beamer', file: 'Beamer.svg', category: 'payment' },
  
  // 外卖配送
  { name: 'Uber Eats', file: 'Uber Eats.svg', category: 'delivery' },
  { name: 'DoorDash', file: 'Doordash.svg', category: 'delivery' },
  { name: 'Grubhub', file: 'Grubhub.svg', category: 'delivery' },
  { name: 'Postmates', file: 'Postmates.svg', category: 'delivery' },
  { name: 'Seamless', file: 'Seamless.svg', category: 'delivery' },
  { name: 'ChowNow', file: 'ChowNow.svg', category: 'delivery' },
  { name: 'Delivery.com', file: 'Delivery.com.svg', category: 'delivery' },
  { name: 'Caviar', file: 'Caviar.svg', category: 'delivery' },
  { name: 'Rappi', file: 'Rappi.svg', category: 'delivery' },
  
  // 应用商店
  { name: 'App Store', file: 'App Store.svg', category: 'store' },
  { name: 'Play Store', file: 'Play Store.svg', category: 'store' },
  { name: 'Yelp', file: 'yelp.svg', category: 'store' },
  { name: 'HighLevel', file: 'HighLevel.svg', category: 'store' },
  
  // 功能图标
  { name: '分享', file: 'share.svg', category: 'action' },
  { name: '二维码', file: 'qrcode.svg', category: 'action' },
  { name: '日历', file: 'calendar.svg', category: 'action' },
  { name: '复制', file: 'copy.svg', category: 'action' },
  { name: '下载', file: 'download.svg', category: 'action' },
  { name: '关闭', file: 'close.svg', category: 'action' },
  { name: '确认', file: 'check.svg', category: 'action' },
  { name: '添加', file: 'add.svg', category: 'action' },
  { name: '添加用户', file: 'add-user.svg', category: 'action' },
  { name: '添加图片', file: 'add-img.svg', category: 'action' },
  { name: '拖拽', file: 'drag.svg', category: 'action' },
  { name: '省略', file: 'ellipsis.svg', category: 'action' },
  { name: '播放', file: 'play.svg', category: 'action' },
  { name: '暂停', file: 'pause.svg', category: 'action' },
  { name: '停止', file: 'stop.svg', category: 'action' },
  
  // 文件与内容
  { name: '文件', file: 'file.svg', category: 'content' },
  { name: '文档', file: 'documents.svg', category: 'content' },
  { name: '图片', file: 'image.svg', category: 'content' },
  { name: '照片', file: 'photo.svg', category: 'content' },
  { name: '视频', file: 'videos.svg', category: 'content' },
  { name: '音乐', file: 'music.svg', category: 'content' },
  { name: '文本', file: 'text.svg', category: 'content' },
  { name: '代码', file: 'code.svg', category: 'content' },
  { name: '密钥', file: 'key.svg', category: 'content' },
  { name: '盒子', file: 'box.svg', category: 'content' },
  
  // 商业与品牌
  { name: '商店', file: 'store.svg', category: 'business' },
  { name: '品牌', file: 'brand.svg', category: 'business' },
  { name: '特色', file: 'featured.svg', category: 'business' },
  { name: '评价', file: 'Review.svg', category: 'business' },
  { name: 'Google', file: 'google.svg', category: 'business' },
  { name: 'Google Chat', file: 'googlechat-old.svg', category: 'business' },
  { name: 'AppSumo', file: 'appsumo-logo.svg', category: 'business' }
]

// CSS图标列表（基于现有的图标类）
export const CSS_ICONS = [
  { class: 'icon-phone', name: '电话', category: 'contact' },
  { class: 'icon-email', name: '邮箱', category: 'contact' },
  { class: 'icon-location', name: '位置', category: 'contact' },
  { class: 'icon-website', name: '网站', category: 'contact' },
  { class: 'icon-share', name: '分享', category: 'action' },
  { class: 'icon-qrcode', name: '二维码', category: 'action' },
  { class: 'icon-user', name: '用户', category: 'user' },
  { class: 'icon-user-plus', name: '添加用户', category: 'user' },
  { class: 'icon-star', name: '星标', category: 'rating' },
  { class: 'icon-heart', name: '喜欢', category: 'rating' },
  { class: 'icon-calendar', name: '日历', category: 'time' },
  { class: 'icon-clock', name: '时钟', category: 'time' },
  { class: 'icon-plus', name: '加号', category: 'action' },
  { class: 'icon-delete', name: '删除', category: 'action' },
  { class: 'icon-edit', name: '编辑', category: 'action' },
  { class: 'icon-close', name: '关闭', category: 'action' },
  { class: 'icon-check', name: '确认', category: 'action' },
  { class: 'icon-arrow-left', name: '左箭头', category: 'navigation' },
  { class: 'icon-arrow-right', name: '右箭头', category: 'navigation' },
  { class: 'icon-arrow-up', name: '上箭头', category: 'navigation' },
  { class: 'icon-arrow-down', name: '下箭头', category: 'navigation' }
]

// Emoji分类列表
export const EMOJI_CATEGORIES = {
  smileys: {
    name: '表情',
    emojis: [
      '😀', '😃', '😄', '😁', '😅', '😂', '🤣', '😊', '😇', '🙂',
      '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋',
      '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳',
      '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖',
      '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯'
    ]
  },
  gestures: {
    name: '手势',
    emojis: [
      '👍', '👎', '👊', '✊', '🤛', '🤜', '🤞', '✌️', '🤟', '🤘',
      '👌', '🤏', '👈', '👉', '👆', '👇', '☝️', '✋', '🤚', '🖐',
      '🖖', '👋', '🤙', '💪', '🦾', '✍️', '🙏', '🤝', '👏', '🙌'
    ]
  },
  symbols: {
    name: '符号',
    emojis: [
      '🔥', '⭐', '✨', '💫', '⚡', '💥', '💯', '✔️', '✅', '❌',
      '❗', '❓', '⚠️', '🚫', '💢', '💬', '💭', '🗨', '🗯', '💤'
    ]
  },
  hearts: {
    name: '爱心',
    emojis: [
      '❤️', '💙', '💚', '💛', '🧡', '💜', '🖤', '🤍', '🤎', '💗',
      '💓', '💕', '💖', '💘', '💝', '💞', '💟', '❣️', '💔', '❤️‍🔥'
    ]
  },
  celebrations: {
    name: '庆祝',
    emojis: [
      '🎉', '🎊', '🎈', '🎁', '🎀', '🎂', '🎆', '🎇', '✨', '🎄',
      '🎃', '🎗', '🏆', '🥇', '🥈', '🥉', '🏅', '🎖', '🎗', '🎪'
    ]
  },
  tech: {
    name: '科技',
    emojis: [
      '📱', '💻', '⌨️', '🖥', '🖨', '🖱', '💾', '💿', '📀', '📷',
      '📞', '☎️', '📟', '📠', '📡', '🔋', '🔌', '💡', '🔦', '📡'
    ]
  },
  business: {
    name: '商务',
    emojis: [
      '💼', '📊', '📈', '📉', '📋', '📌', '📍', '📎', '🖇', '📏',
      '📐', '✂️', '🗃', '🗄', '🗂', '📂', '📁', '📅', '📆', '🗓'
    ]
  },
  buildings: {
    name: '建筑',
    emojis: [
      '🏠', '🏢', '🏦', '🏪', '🏬', '🏭', '🏗', '🏘', '🏛', '⛪',
      '🕌', '🕍', '⛩', '🗼', '🗽', '🗾', '🗿', '🏰', '🏯', '🏟'
    ]
  },
  transport: {
    name: '交通',
    emojis: [
      '🚀', '✈️', '🚁', '🚂', '🚃', '🚄', '🚅', '🚆', '🚇', '🚈',
      '🚉', '🚊', '🚝', '🚞', '🚋', '🚌', '🚍', '🚎', '🚐', '🚑'
    ]
  }
}

// Lottie动画配置
export const LOTTIE_ANIMATIONS = [
  {
    key: 'phone-ring',
    name: '电话响铃',
    path: 'phone/ring.json',
    category: 'contact',
    preview: '/assets/animations/phone/ring.json',
    description: '电话拨打动画效果'
  },
  {
    key: 'share-float',
    name: '分享浮动',
    path: 'share/float.json',
    category: 'action',
    preview: '/assets/animations/share/float.json',
    description: '分享按钮浮动效果'
  }
  // 添加更多动画:
  // 1. 将动画JSON文件放入 /opt/qwcard/public/assets/animations/ 对应子目录
  // 2. 在此数组中添加配置项
  // 3. 运行: systemctl restart wecard-nuxt.service
  //
  // 免费Lottie资源:
  // - LottieFiles: https://lottiefiles.com/ (最大的Lottie动画库)
  // - Iconscout: https://iconscout.com/lottie-animations
  // - 使用脚本: /opt/qwcard/scripts/add-lottie-animation.sh
]

// 图标类别配置
export const ICON_CATEGORIES = {
  contact: { name: '联系方式', icon: '📞' },
  social: { name: '社交媒体', icon: '👥' },
  professional: { name: '专业平台', icon: '💼' },
  community: { name: '社区平台', icon: '🌐' },
  media: { name: '媒体娱乐', icon: '🎵' },
  payment: { name: '支付商务', icon: '💰' },
  delivery: { name: '外卖配送', icon: '🚚' },
  store: { name: '应用商店', icon: '🏪' },
  action: { name: '操作功能', icon: '⚡' },
  content: { name: '文件内容', icon: '📄' },
  business: { name: '商业品牌', icon: '🏢' },
  user: { name: '用户相关', icon: '👤' },
  rating: { name: '评价收藏', icon: '⭐' },
  time: { name: '时间日期', icon: '⏰' },
  navigation: { name: '导航箭头', icon: '➡️' }
}

/**
 * 获取指定类别的SVG图标
 */
export function getSvgIconsByCategory(category) {
  if (!category) return SVG_ICONS
  return SVG_ICONS.filter(icon => icon.category === category)
}

/**
 * 获取指定类别的CSS图标
 */
export function getCssIconsByCategory(category) {
  if (!category) return CSS_ICONS
  return CSS_ICONS.filter(icon => icon.category === category)
}

/**
 * 获取所有图标类别
 */
export function getAllCategories() {
  return Object.keys(ICON_CATEGORIES).map(key => ({
    key,
    ...ICON_CATEGORIES[key]
  }))
}

/**
 * 搜索图标
 */
export function searchIcons(query, type = 'all') {
  const lowerQuery = query.toLowerCase()
  const results = {
    svg: [],
    css: [],
    emoji: []
  }
  
  if (type === 'all' || type === 'svg') {
    results.svg = SVG_ICONS.filter(icon => 
      icon.name.toLowerCase().includes(lowerQuery) ||
      icon.file.toLowerCase().includes(lowerQuery)
    )
  }
  
  if (type === 'all' || type === 'css') {
    results.css = CSS_ICONS.filter(icon =>
      icon.name.toLowerCase().includes(lowerQuery) ||
      icon.class.toLowerCase().includes(lowerQuery)
    )
  }
  
  return results
}

