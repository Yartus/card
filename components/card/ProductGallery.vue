<template>
  <section class="product-gallery">
    <div class="pg-card">
      <div class="pg-header">产品展示</div>
      <div class="pg-body">
        <div v-if="layout === 'grid'" class="pg-grid">
          <div v-for="(item, idx) in items" :key="idx" class="pg-item">
            <img :src="item.image" :alt="item.title || ('产品'+(idx+1))" loading="lazy" />
            <div v-if="item.title || item.desc" class="pg-caption">
              <div class="pg-title">{{ item.title }}</div>
              <div class="pg-desc">{{ item.desc }}</div>
            </div>
          </div>
        </div>
        <div v-else class="pg-hscroll" tabindex="0">
          <div v-for="(item, idx) in items" :key="idx" class="pg-slide">
            <img :src="item.image" :alt="item.title || ('产品'+(idx+1))" loading="lazy" />
            <div v-if="item.title || item.desc" class="pg-caption">
              <div class="pg-title">{{ item.title }}</div>
              <div class="pg-desc">{{ item.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ProductGallery',
  props: {
    items: { type: Array, default: () => [] },
    layout: { type: String, default: 'grid' } // grid | hscroll
  }
}
</script>

<style lang="scss" scoped>
.product-gallery { 
  margin: 12px 16px; 
}

.pg-card { 
  background: #fff; 
  border: 1px solid rgba(0,0,0,.08); 
  border-radius: 12px; 
  box-shadow: 0 2px 8px rgba(0,0,0,.04); 
  overflow: hidden; 
}

.pg-header { 
  padding: 16px 18px; 
  border-bottom: 1px solid #f0f2f5; 
  font-weight: 600; 
  font-size: 16px;
  color: #262626; 
}

.pg-body { 
  padding: 16px 18px; 
}

.pg-grid { display: grid; gap: 12px; grid-template-columns: repeat(1, 1fr); }
@media (min-width: 768px) { .pg-grid { grid-template-columns: repeat(3, 1fr); } }
.pg-item { position: relative; border:1px solid rgba(0,0,0,.08); border-radius: 10px; overflow: hidden; transition: transform .2s ease; }
.pg-item:hover { transform: translateY(-2px); }
.pg-item img { width: 100%; height: 100%; object-fit: cover; display:block; aspect-ratio: 4/3; }

.pg-hscroll { display: flex; gap: 12px; overflow: auto; scroll-snap-type: x mandatory; padding-bottom: 6px; }
.pg-slide { flex: 0 0 72%; max-width: 520px; border:1px solid rgba(0,0,0,.08); border-radius: 10px; overflow: hidden; scroll-snap-align: start; }
.pg-slide img { width: 100%; display:block; aspect-ratio: 4/3; object-fit: cover; }

.pg-caption { padding: 8px 10px; background: #fff; }
.pg-title { font-weight: 600; font-size: 14px; color:#111; }
.pg-desc { font-size: 12px; color: rgba(0,0,0,.60); }

@media (max-width: 480px) {
  .product-gallery {
    margin: 12px 12px;
  }
  
  .pg-header {
    padding: 14px 16px;
    font-size: 15px;
  }
  
  .pg-body {
    padding: 14px 16px;
  }
}
</style>


