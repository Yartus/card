<template>
  <section class="environment-showcase">
    <div class="es-card">
      <div class="es-header">环境/工厂展示</div>
      <div class="es-body">
        <div class="es-hscroll" tabindex="0">
          <div v-for="(item, idx) in items" :key="idx" class="es-slide">
            <img :src="item.image" :alt="item.title || ('环境'+(idx+1))" loading="lazy" />
            <div v-if="item.title || item.desc" class="es-caption">
              <div class="es-title">{{ item.title }}</div>
              <div class="es-desc">{{ item.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'EnvironmentShowcase',
  props: { items: { type: Array, default: () => [] } }
}
</script>

<style lang="scss" scoped>
.environment-showcase { 
  margin: 12px 16px; 
}

.es-card { 
  background: #fff; 
  border: 1px solid rgba(0,0,0,.08); 
  border-radius: 12px; 
  box-shadow: 0 2px 8px rgba(0,0,0,.04); 
  overflow: hidden; 
}

.es-header { 
  padding: 16px 18px; 
  border-bottom: 1px solid #f0f2f5; 
  font-weight: 600; 
  font-size: 16px;
  color: #262626; 
}

.es-body { 
  padding: 16px 18px; 
}

.es-hscroll { 
  display: flex; 
  gap: 12px; 
  overflow: auto; 
  scroll-snap-type: x mandatory; 
  padding-bottom: 6px; 
}

.es-slide { 
  flex: 0 0 72%; 
  max-width: 520px; 
  border: 1px solid rgba(0,0,0,.08); 
  border-radius: 10px; 
  overflow: hidden; 
  scroll-snap-align: start; 
}

.es-slide img { 
  width: 100%; 
  display: block; 
  aspect-ratio: 4/3; 
  object-fit: cover; 
}

.es-caption { 
  padding: 8px 10px; 
  background: #fff; 
}

.es-title { 
  font-weight: 600; 
  font-size: 14px; 
  color: #111; 
}

.es-desc { 
  font-size: 12px; 
  color: rgba(0,0,0,.60); 
}

@media (max-width: 480px) {
  .environment-showcase {
    margin: 12px 12px;
  }
  
  .es-header {
    padding: 14px 16px;
    font-size: 15px;
  }
  
  .es-body {
    padding: 14px 16px;
  }
}
</style>


