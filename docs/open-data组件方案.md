# Open-Data 组件方案详解

## 问题分析

### 当前困境
1. **后端无法获取真实姓名**：企微隐私保护，OAuth只返回加密的open_userid
2. **管理后台需要识别成员**：管理员在"成员管理"界面需要知道是谁
3. **名片需要显示真实姓名**：员工名片要显示真实姓名和联系方式

### 企微的设计逻辑
```
第三方应用 → OAuth授权 → 只能获取 open_userid (加密ID)
                            ↓
                     前端使用 ww-open-data 组件
                            ↓
                     企微客户端渲染真实姓名
```

**关键点**：姓名不存在于您的数据库中，而是在渲染时由企微动态注入。

---

## 核心矛盾

### 矛�盾1：管理后台的成员识别

**场景**：管理员在"成员管理"界面看到一堆加密ID：
```
womKtScgAAEkyZS7yXhQkhLqeCvf7ehQ
womKtScgAAnk8xvR6WLRzU8Q7CZNlevQ
womKtScgAAUn6WKq_NHdfHkOABxsHw5A
```

❌ **问题**：管理员完全无法识别这是谁！

#### 解决方案选项：

**选项1：管理后台也用 open-data 组件**
```vue
<!-- 成员管理表格 -->
<td>
  <ww-open-data type="userName" :openid="member.open_userid"></ww-open-data>
</td>
```

✅ **优点**：可以显示真实姓名  
❌ **缺点**：
- 需要在管理后台也初始化企微JSSDK
- 搜索和排序功能无法使用（无法对加密ID进行搜索）
- 导出Excel时无法包含真实姓名

**选项2：增加"对外显示名称"字段**
```
数据库字段：
- open_userid (加密ID) - 企微返回，不可修改
- display_name (对外显示名称) - 管理员手动输入
- mobile (手机号) - 管理员手动输入
```

✅ **优点**：
- 管理员可以自己输入易识别的名称（如"张三"、"李四"）
- 后端可以搜索、排序
- 可以导出到Excel

❌ **缺点**：
- 需要管理员手动维护
- 可能与员工真实姓名不一致

---

## 推荐方案：混合方案

### 数据模型

```python
class Member(db.Model):
    # 企微相关（自动获取）
    open_userid = db.Column(db.String(128))  # OAuth获取的加密ID
    avatar_url = db.Column(db.String(512))   # OAuth获取的头像
    
    # 管理员维护（手动输入）
    display_name = db.Column(db.String(128)) # 对外显示名称
    mobile = db.Column(db.String(64))        # 手机号码
    position = db.Column(db.String(128))     # 职位
    
    # 管理员自定义（可选）
    custom_avatar_url = db.Column(db.String(512))      # 自定义头像
    custom_push_photo_url = db.Column(db.String(512))  # 推送照片
```

### 前端渲染逻辑

#### 场景1：名片前端（企微环境内）

```vue
<!-- components/card/CardHeader.vue -->
<template>
  <div class="card-header">
    <!-- 头像：优先自定义 > 企微头像 -->
    <img :src="avatarUrl" />
    
    <!-- 姓名：使用 open-data 组件显示真实姓名 -->
    <ww-open-data 
      v-if="openUserid"
      type="userName" 
      :openid="openUserid"
    ></ww-open-data>
    <span v-else>{{ displayName }}</span>
    
    <!-- 职位：从数据库获取 -->
    <span>{{ position }}</span>
  </div>
</template>

<script>
export default {
  props: {
    openUserid: String,      // 从后端获取
    displayName: String,     // 备用名称
    avatarUrl: String,       // 优先自定义头像
    position: String
  },
  mounted() {
    // 初始化 open-data 组件
    if (window.WWOpenData && this.openUserid) {
      this.$nextTick(() => {
        WWOpenData.bind(this.$el.querySelector('ww-open-data'))
      })
    }
  }
}
</script>
```

#### 场景2：管理后台（Web环境）

```vue
<!-- pages/wecom/workspace.vue - 成员管理 -->
<template>
  <table class="members-table">
    <thead>
      <tr>
        <th>头像</th>
        <th>对外显示名称</th>
        <th>手机号码</th>
        <th>职位</th>
        <th>UserID (识别用)</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="member in membersList" :key="member.id">
        <td>
          <img :src="member.avatar_url || member.custom_avatar_url" />
        </td>
        
        <!-- 编辑模式 -->
        <td v-if="editingMemberId === member.id">
          <input v-model="editForm.display_name" placeholder="请输入姓名（如：张三）" />
        </td>
        <!-- 显示模式 -->
        <td v-else>
          {{ member.display_name || '未设置' }}
          <span v-if="!member.display_name" class="hint">
            请编辑设置姓名
          </span>
        </td>
        
        <td>
          <input v-if="editingMemberId === member.id" v-model="editForm.mobile" />
          <span v-else>{{ member.mobile || '-' }}</span>
        </td>
        
        <td>
          <input v-if="editingMemberId === member.id" v-model="editForm.position" />
          <span v-else>{{ member.position || '-' }}</span>
        </td>
        
        <!-- 显示加密ID的缩略版（用于识别） -->
        <td>
          <code class="userid-short">
            {{ member.open_userid ? member.open_userid.slice(0, 8) + '...' : '-' }}
          </code>
        </td>
        
        <td>
          <button @click="startEdit(member)">编辑</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
```

---

## 数据流设计

### 1. OAuth授权流程（自动）

```
员工在企微中打开应用
  ↓
触发OAuth授权
  ↓
后端获取：
  - open_userid (加密ID) ✅
  - avatar_url (头像) ✅
  - name (仍是加密ID) ❌
  - mobile (为空) ❌
  ↓
保存到数据库 members 表
```

### 2. 管理员配置流程（手动）

```
管理员打开"成员管理"
  ↓
看到成员列表（按 open_userid 前8位识别）
  ↓
点击"编辑"按钮
  ↓
输入：
  - display_name (对外显示名称) ← 管理员输入
  - mobile (手机号码) ← 管理员输入
  - position (职位) ← 管理员输入
  - custom_avatar_url (自定义头像) ← 可选
  ↓
保存到数据库
```

### 3. 名片渲染流程（前端）

**API返回数据**：
```json
{
  "basic_info": {
    "open_userid": "womKtScgAAEkyZS7yXhQkhLqeCvf7ehQ",
    "display_name": "张三",
    "position": "产品经理",
    "avatar_url": "https://..."
  },
  "contact_info": {
    "mobile": "13800138000",
    "email": "zhangsan@company.com"
  }
}
```

**前端渲染**：
```vue
<!-- 如果在企微环境 -->
<ww-open-data type="userName" openid="womKtScgAAEkyZS7yXhQkhLqeCvf7ehQ">
  <!-- 企微自动渲染为："张三（真实姓名）" -->
</ww-open-data>

<!-- 如果不在企微环境（如PC浏览器） -->
<span>张三</span>  <!-- 显示 display_name -->
```

---

## 实施步骤

### Step 1: 修改数据库字段

```sql
-- 重命名字段
ALTER TABLE members CHANGE COLUMN name display_name VARCHAR(128);

-- 添加注释
ALTER TABLE members MODIFY COLUMN open_userid VARCHAR(128) COMMENT 'OAuth获取的加密用户ID';
ALTER TABLE members MODIFY COLUMN display_name VARCHAR(128) COMMENT '管理员设置的对外显示名称';
```

### Step 2: 修改后端API

```python
# app/routes/wecom.py - get_my_card
def get_my_card():
    # ...
    card_data = {
        'basic_info': {
            'open_userid': member.open_userid,      # 传给前端用于open-data
            'display_name': member.display_name,    # 备用显示名称
            'avatar_url': get_avatar_url(member),   # 头像（优先自定义）
            'position': member.position
        },
        'contact_info': {
            'mobile': member.mobile,
            'email': member.email
        }
    }
    return jsonify(card_data)
```

### Step 3: 修改前端名片组件

```vue
<!-- components/card/CardHeader.vue -->
<template>
  <div class="name-display">
    <!-- 企微环境：使用 open-data -->
    <ww-open-data 
      v-if="isWecomEnv && openUserid"
      type="userName" 
      :openid="openUserid"
      ref="opendata"
    ></ww-open-data>
    
    <!-- 非企微环境：显示 display_name -->
    <span v-else>{{ displayName }}</span>
  </div>
</template>

<script>
export default {
  computed: {
    isWecomEnv() {
      return /wxwork/i.test(navigator.userAgent)
    }
  },
  mounted() {
    if (this.isWecomEnv && window.WWOpenData) {
      this.$nextTick(() => {
        const el = this.$refs.opendata
        if (el) WWOpenData.bind(el)
      })
    }
  }
}
</script>
```

### Step 4: 修改管理后台界面

简化显示，重点是让管理员能方便地输入和识别：

```vue
<td>
  <!-- 编辑时 -->
  <input 
    v-if="editing" 
    v-model="editForm.display_name"
    placeholder="姓名（如：张三）"
  />
  
  <!-- 显示时 -->
  <div v-else>
    <strong>{{ member.display_name || '未设置' }}</strong>
    <br />
    <small class="userid-hint">
      ID: {{ member.open_userid.slice(0, 8) }}...
    </small>
  </div>
</td>
```

---

## 优势总结

### ✅ 解决的问题

1. **名片显示真实姓名**：在企微环境中使用 open-data 组件
2. **管理后台可识别**：使用 display_name 字段
3. **数据可搜索排序**：基于 display_name 进行操作
4. **灵活性高**：管理员可以自定义显示名称

### ⚠️ 注意事项

1. **display_name 不一定是真实姓名**：
   - 是管理员输入的"易识别名称"
   - 可以是真实姓名，也可以是昵称、工号等

2. **open-data 组件需要企微环境**：
   - 在企微客户端内有效
   - 在普通浏览器会降级显示 display_name

3. **首次使用需要管理员初始化**：
   - 员工OAuth授权后，display_name 为空
   - 管理员需要在"成员管理"中手动设置

---

## 用户体验流程

### 员工视角
1. 在企微中打开应用 → OAuth授权
2. 看到自己的名片 → 显示**真实姓名**（open-data渲染）
3. 联系方式需要管理员设置后才显示

### 管理员视角
1. 打开"成员管理" → 看到成员列表（按UserID前缀识别）
2. 点击"编辑" → 输入"对外显示名称"、手机号等
3. 保存后 → 员工名片显示这些信息

### 最终效果
- **企微内**：显示真实姓名（企微保护隐私）
- **管理后台**：显示 display_name（管理员可识别）
- **数据安全**：真实姓名不存储在您的数据库中

---

**这个方案是否符合您的需求？我可以立即开始实施。**

