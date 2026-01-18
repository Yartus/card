<template>
  <section class="media-showcase-section">
    <div class="ms-card">
      <!-- 标题 -->
      <div v-if="data.title" class="ms-header">
        <h3 class="ms-title">{{ data.title }}</h3>
        <p v-if="data.subtitle" class="ms-subtitle">{{ data.subtitle }}</p>
      </div>
      
      <!-- 视频模式 -->
      <div v-if="data.mode === 'video'" class="ms-body">
        <div class="video-grid" :class="`grid-cols-${data.grid_columns || 2}`">
          <div
            v-for="video in displayVideos"
            :key="video.id"
            class="video-item"
            @click="handleVideoClick(video)"
          >
            <!-- 封面图 -->
            <div class="video-thumbnail">
              <img
                v-if="video.thumbnail"
                :src="video.thumbnail"
                :alt="video.title"
                class="thumbnail-image"
              />
              <div v-else class="thumbnail-placeholder">
                <i class="icon-video">🎬</i>
              </div>
              
              <!-- 播放按钮 -->
              <div class="play-overlay">
                <div class="play-button">
                  <i class="icon-play">▶</i>
                </div>
              </div>
            </div>
            
            <!-- 视频信息 -->
            <div class="video-info">
              <h4 class="video-title">{{ video.title }}</h4>
              <p v-if="video.description" class="video-description">
                {{ video.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图文交替模式（新版：blocks） -->
      <div v-if="data.mode === 'text-image-alt'" class="ms-body">
        <div v-if="data.content && data.content.blocks && data.content.blocks.length > 0" class="blocks-container">
          <div
            v-for="(block, index) in data.content.blocks"
            :key="block.id || index"
            :class="['content-block', `block-type-${block.type}`]"
          >
            <!-- 文字块 -->
            <div v-if="block.type === 'text'" class="text-block">
              <p v-for="(para, pIdx) in splitParagraphs(block.text)" :key="pIdx" class="text-paragraph">
                {{ para }}
              </p>
            </div>
            
            <!-- 图片块 -->
            <div v-if="block.type === 'image' && block.src" class="image-block">
              <div class="block-image-wrapper" @click="openImagePreview(block.src)">
                <img :src="block.src" :alt="block.caption || '图片'" class="block-image" />
                <div class="image-zoom-hint">
                  <span>点击放大</span>
                </div>
              </div>
              <p v-if="block.caption" class="image-caption">{{ block.caption }}</p>
            </div>
          </div>
        </div>
        <div v-else class="empty-placeholder">
          <p>暂无内容</p>
        </div>
      </div>
      
      <!-- 图片横滑模式 -->
      <div v-if="data.mode === 'image-grid'" class="ms-body">
        <!-- 顶部文字内容 -->
        <div v-if="data.content && data.content.topText" class="text-content">
          <p v-for="(para, index) in splitParagraphs(data.content.topText)" :key="index" class="text-paragraph">
            {{ para }}
          </p>
        </div>
        
        <!-- 单行横滑图片 -->
        <div 
          v-if="data.content && data.content.images && data.content.images.length > 0" 
          class="images-scroll-wrapper"
        >
          <div 
            class="images-scroll"
            :style="{ '--image-card-width': imageCardWidth }"
          >
            <div
              v-for="(image, index) in data.content.images"
              :key="image.id || index"
              class="image-item-horizontal"
            >
              <div class="image-frame">
                <img :src="image.src" :alt="image.caption || '图片'" class="image-grid" />
              </div>
              <p v-if="image.caption" class="image-caption">{{ image.caption }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
      <!-- 图片预览Modal -->
      <div v-if="previewImage" class="image-preview-modal" @click="closeImagePreview">
        <div class="preview-content" @click.stop>
          <button class="modal-close" @click="closeImagePreview">×</button>
          <img :src="previewImage" alt="预览图片" />
        </div>
      </div>
      
      <!-- 视频播放Modal（仅视频模式） -->
    <div v-if="showVideoModal && currentVideo" class="video-modal" @click="closeVideoModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeVideoModal">×</button>
        <div class="video-container">
          <iframe
            v-if="videoEmbedUrl"
            :src="videoEmbedUrl"
            frameborder="0"
            allowfullscreen
            class="video-iframe"
          ></iframe>
          <p v-else class="video-error">暂不支持该视频链接</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'VideoShowcase',
  
  props: {
    data: {
      type: Object,
      required: true,
      default: () => ({
        title: '',
        subtitle: '',
        mode: 'video',
        grid_columns: 2,
        videos: [],
        content: {
          text: '',
          images: []
        }
      })
    }
  },
  
  data() {
    return {
      showVideoModal: false,
      currentVideo: null,
      previewImage: null
    }
  },
  
  computed: {
    displayVideos() {
      return this.data.videos || []
    },
    
    imageCardWidth() {
      const columns = this.data.grid_columns || 2
      if (columns === 3) return '220px'
      return '260px'
    },
    
    videoEmbedUrl() {
      if (!this.currentVideo || !this.currentVideo.url) return null
      
      const url = this.currentVideo.url
      
      // 优酷
      if (url.includes('youku.com')) {
        const match = url.match(/id_([^=]+)/)
        if (match) {
          return `https://player.youku.com/embed/${match[1]}`
        }
      }
      
      // 腾讯视频
      if (url.includes('v.qq.com')) {
        const match = url.match(/\/([a-zA-Z0-9]+)\.html/)
        if (match) {
          return `https://v.qq.com/txp/iframe/player.html?vid=${match[1]}`
        }
      }
      
      // B站
      if (url.includes('bilibili.com')) {
        const match = url.match(/video\/([^/?]+)/)
        if (match) {
          return `https://player.bilibili.com/player.html?bvid=${match[1]}`
        }
      }
      
      // 如果是直接的嵌入URL或本地视频
      return url
    }
  },
  
  methods: {
    // 分割文字段落
    splitParagraphs(text) {
      if (!text) return []
      return text.split('\n').filter(p => p.trim())
    },
    
    handleVideoClick(video) {
      this.currentVideo = video
      this.showVideoModal = true
      document.body.style.overflow = 'hidden'
    },
    
    closeVideoModal() {
      this.showVideoModal = false
      this.currentVideo = null
      document.body.style.overflow = ''
    }
    ,
    openImagePreview(src) {
      this.previewImage = src
      document.body.style.overflow = 'hidden'
    },
    closeImagePreview() {
      this.previewImage = null
      document.body.style.overflow = ''
    }
  },
  
  beforeDestroy() {
    document.body.style.overflow = ''
  }
}
</script>

<style lang="scss" scoped>
/* 参考设计规范：间距 16-24px，圆角 12px，呼吸感设计 */

.media-showcase-section {
  margin: 12px 16px;
}

.ms-card {
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

/* 标题区域 */
.ms-header {
  padding: 20px 20px 16px 20px;
  border-bottom: 1px solid #f0f2f5;
}

.ms-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 6px 0;
  line-height: 1.4;
}

.ms-subtitle {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
  line-height: 1.6;
}

/* 内容区域 */
.ms-body {
  padding: 20px;
}

/* ===== 视频模式 ===== */
.video-grid {
  display: grid;
  gap: 16px;
  
  &.grid-cols-1 {
    grid-template-columns: 1fr;
  }
  
  &.grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  &.grid-cols-3 {
    grid-template-columns: repeat(3, 1fr);
  }
}

.video-item {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.06);
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    
    .play-button {
      transform: scale(1.1);
      background: rgba(0, 255, 170, 0.95);
    }
  }
}

.video-thumbnail {
  position: relative;
  padding-top: 56.25%; /* 16:9 */
  background: #f0f0f0;
  overflow: hidden;
  border-radius: 12px;
}

.thumbnail-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.thumbnail-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  
  .icon-video {
    font-size: 48px;
    opacity: 0.3;
  }
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  border-radius: 12px;
  pointer-events: none;
  
  .play-button {
    pointer-events: auto;
  }
}

.play-button {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(0, 255, 170, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 255, 170, 0.4);
  
  .icon-play {
    font-size: 24px;
    color: #1a1a2e;
    margin-left: 4px;
  }
}

.video-info {
  padding: 16px;
}

.video-title {
  font-size: 15px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.video-description {
  font-size: 13px;
  color: #8c8c8c;
  margin: 0;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* ===== 图文交替模式 ===== */
.text-content {
  margin-bottom: 16px; /* 文字与图片间距 */
}

.blocks-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  
  .content-block {
    margin-bottom: 0; /* 使用gap，不需要margin */
  }
  
  .text-block {
    .text-paragraph {
      font-size: 14px;
      color: #595959;
      line-height: 1.4;
      margin: 0 0 6px 0;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
  
  .image-block {
    .block-image-wrapper {
      position: relative;
      cursor: zoom-in;
      
      &:hover .image-zoom-hint {
        opacity: 1;
        transform: translate(-50%, -10px);
      }
    }
    
    .block-image {
      width: 100%;
      height: 240px;
      object-fit: cover;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      display: block;
      transition: transform 0.4s ease;
      
      &:hover {
        transform: scale(1.02);
      }
    }
    
    .image-zoom-hint {
      position: absolute;
      left: 50%;
      bottom: 16px;
      transform: translate(-50%, 0);
      padding: 4px 12px;
      border-radius: 999px;
      background: rgba(0, 0, 0, 0.5);
      color: #fff;
      font-size: 12px;
      opacity: 0;
      transition: all 0.3s ease;
      pointer-events: none;
    }
    
    .image-caption {
      font-size: 12px;
      color: #8c8c8c;
      line-height: 1.4;
      margin: 12px 0 0 0;
      text-align: center;
    }
  }
.image-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.image-preview-modal .preview-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.image-preview-modal img {
  width: 100%;
  height: auto;
  max-height: 90vh;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
}

.image-preview-modal .modal-close {
  position: absolute;
  top: -40px;
  right: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.3);
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.image-preview-modal .modal-close:hover {
  background: rgba(255, 255, 255, 0.5);
}
}

.text-paragraph {
  font-size: 14px;
  color: #595959;
  line-height: 1.4;
  margin: 0 0 6px 0;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.images-alt {
  display: flex;
  flex-direction: column;
  gap: 16px; /* 图片间距 */
}

.image-item-alt {
  width: 100%;
}

.image-full {
  width: 100%;
  height: auto;
  border-radius: 12px;
  display: block;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  }
}

/* ===== 图片横滑模式 ===== */
.images-scroll-wrapper {
  margin-top: 12px;
}

.images-scroll {
  --image-card-width: 260px;
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 16px;
  scroll-snap-type: x mandatory;
  scroll-padding: 8px;
}

.images-scroll::-webkit-scrollbar {
  height: 6px;
}

.images-scroll::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 999px;
}

.image-item-horizontal {
  flex: 0 0 var(--image-card-width);
  max-width: var(--image-card-width);
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
}

.image-frame {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  background: #fff;
  aspect-ratio: 16 / 9;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  }
}

.image-grid {
  width: 100%;
  height: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
  border-radius: 12px;
}

/* 图片说明 */
.image-caption {
  font-size: 12px;
  color: #8c8c8c;
  line-height: 1.4;
  margin: 12px 0 0 0;
  text-align: center;
}

/* ===== 视频播放Modal ===== */
.video-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  position: relative;
  width: 100%;
  max-width: 900px;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

.modal-close {
  position: absolute;
  top: -40px;
  right: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: none;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.1);
  }
}

.video-container {
  position: relative;
  padding-top: 56.25%; /* 16:9 */
  background: #000;
}

.video-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-size: 16px;
  text-align: center;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(40px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .ms-header {
    padding: 16px;
  }
  
  .ms-body {
    padding: 16px;
  }
  
  .video-grid {
    &.grid-cols-2,
    &.grid-cols-3 {
      grid-template-columns: 1fr;
    }
  }
  
  .images-scroll {
    --image-card-width: 220px;
  }

  .blocks-container .image-block .block-image {
    height: 200px;
  }
  
  .text-paragraph {
    font-size: 13px;
  }
  
  .play-button {
    width: 56px;
    height: 56px;
    
    .icon-play {
      font-size: 20px;
    }
  }
  
  /* 图文交替blocks样式 */
  .blocks-container {
    .content-block {
      margin-bottom: 16px;
    }
    
    .text-block {
      .text-paragraph {
        font-size: 13px;
      }
    }
    
    .image-block .block-image {
      height: 200px;
    }
    
    .image-caption {
      font-size: 12px;
    }
  }
}

@media (max-width: 480px) {
  .images-scroll {
    --image-card-width: 180px;
    gap: 12px;
  }
  
  .blocks-container .image-block .block-image {
    height: 180px;
  }
}

@media (max-width: 480px) {
  .media-showcase-section {
    margin: 12px 12px;
  }
  
  .ms-title {
    font-size: 16px;
  }
  
  .ms-subtitle {
    font-size: 13px;
  }
  
  .modal-close {
    top: 10px;
    right: 10px;
  }
}

/* 减少动画模式支持 */
@media (prefers-reduced-motion: reduce) {
  .video-item,
  .image-item-grid,
  .play-button {
    transition: none;
  }
  
  .video-modal,
  .modal-content {
    animation: none;
  }
}
</style>
