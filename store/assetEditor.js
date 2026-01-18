/**
 * 素材编辑器状态管理
 * 用于在左侧编辑区和右侧预览区之间同步数据
 */

export const state = () => ({
  // 当前编辑中的素材草稿
  draftAsset: null,
  
  // 编辑模式：'create' | 'edit'
  editMode: 'create',
  
  // 是否有未保存的更改
  isDirty: false,
  
  // 最后保存时间
  lastSaved: null
})

export const getters = {
  // 获取当前草稿
  currentDraft: (state) => state.draftAsset,
  
  // 是否有草稿
  hasDraft: (state) => !!state.draftAsset,
  
  // 是否为新建模式
  isCreating: (state) => state.editMode === 'create',
  
  // 是否为编辑模式
  isEditing: (state) => state.editMode === 'edit',
  
  // 是否有未保存更改
  hasUnsavedChanges: (state) => state.isDirty
}

export const mutations = {
  // 设置草稿素材
  SET_DRAFT(state, asset) {
    state.draftAsset = asset ? { ...asset } : null
    state.isDirty = false
  },
  
  // 更新草稿字段
  UPDATE_DRAFT_FIELD(state, { field, value }) {
    if (state.draftAsset) {
      state.draftAsset[field] = value
      state.isDirty = true
    }
  },
  
  // 更新整个草稿
  UPDATE_DRAFT(state, asset) {
    state.draftAsset = asset ? { ...asset } : null
    state.isDirty = true
  },
  
  // 设置编辑模式
  SET_EDIT_MODE(state, mode) {
    state.editMode = mode
  },
  
  // 标记为已保存
  MARK_SAVED(state) {
    state.isDirty = false
    state.lastSaved = new Date().toISOString()
  },
  
  // 清空草稿
  CLEAR_DRAFT(state) {
    state.draftAsset = null
    state.isDirty = false
    state.editMode = 'create'
  }
}

export const actions = {
  // 开始创建新素材
  startCreate({ commit }) {
    const emptyAsset = {
      title: '',
      summary: '',
      cover: '',
      tags: [],
      category: 'product',
      status: 'draft',
      metadata: {
        blocks: [],
        version: '2.0',
        highlightColumns: 2
      }
    }
    commit('SET_DRAFT', emptyAsset)
    commit('SET_EDIT_MODE', 'create')
  },
  
  // 开始编辑已有素材
  startEdit({ commit }, asset) {
    // 确保metadata存在
    const assetWithMeta = {
      ...asset,
      metadata: asset.metadata || {
        blocks: [],
        version: '2.0',
        highlightColumns: 2
      }
    }
    commit('SET_DRAFT', assetWithMeta)
    commit('SET_EDIT_MODE', 'edit')
  },
  
  // 更新草稿
  updateDraft({ commit }, asset) {
    commit('UPDATE_DRAFT', asset)
  },
  
  // 更新单个字段
  updateField({ commit }, payload) {
    commit('UPDATE_DRAFT_FIELD', payload)
  },
  
  // 保存成功后标记
  markSaved({ commit }) {
    commit('MARK_SAVED')
  },
  
  // 取消编辑
  cancelEdit({ commit }) {
    commit('CLEAR_DRAFT')
  }
}

