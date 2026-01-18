<template>
  <section class="solution-intro">
    <div class="si-card">
      <div class="si-header">方案介绍</div>
      <div class="si-body">
        <div class="si-split">
          <div class="si-text">
            <h3 v-if="solution && solution.title" class="si-title">{{ solution.title }}</h3>
            <p v-if="solution && solution.summary" class="si-summary">{{ solution.summary }}</p>
            <ul v-if="Array.isArray(solution && solution.points)" class="si-points">
              <li v-for="(p, idx) in solution.points" :key="idx">{{ p }}</li>
            </ul>
          </div>
          <div class="si-media" v-if="solution && solution.image">
            <img :src="solution.image" :alt="solution.title || '方案配图'" loading="lazy" />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'SolutionIntro',
  props: { solution: { type: Object, default: () => ({}) } }
}
</script>

<style lang="scss" scoped>
.solution-intro { 
  margin: 12px 16px; 
}

.si-card { 
  background: #fff; 
  border: 1px solid rgba(0,0,0,.08); 
  border-radius: 12px; 
  box-shadow: 0 2px 8px rgba(0,0,0,.04); 
  overflow: hidden; 
}

.si-header { 
  padding: 16px 18px; 
  border-bottom: 1px solid #f0f2f5; 
  font-weight: 600; 
  font-size: 16px;
  color: #262626; 
}

.si-body { 
  padding: 16px 18px; 
}

.si-split { 
  display: grid; 
  gap: 18px; 
}

@media (min-width: 900px) { 
  .si-split { 
    grid-template-columns: 1.1fr 1fr; 
  } 
}

.si-title { 
  margin: 0 0 8px 0; 
  font-size: 16px; 
  color: #111; 
}

.si-summary { 
  margin: 0 0 8px 0; 
  color: rgba(0,0,0,.65); 
  line-height: 1.6; 
  font-size: 14px;
}

.si-points { 
  margin: 12px 0 0 18px; 
  color: rgba(0,0,0,.70); 
  
  li {
    margin-bottom: 4px;
    font-size: 14px;
    line-height: 1.5;
  }
}

.si-media img { 
  width: 100%; 
  border-radius: 10px; 
  border: 1px solid rgba(0,0,0,.08); 
  display: block; 
}

@media (max-width: 480px) {
  .solution-intro {
    margin: 12px 12px;
  }
  
  .si-header {
    padding: 14px 16px;
    font-size: 15px;
  }
  
  .si-body {
    padding: 14px 16px;
  }
  
  .si-split {
    gap: 14px;
  }
}
</style>


