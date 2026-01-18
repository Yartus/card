# OAuth2授权获取成员信息完整方案

> **版本**: v1.0  
> **更新**: 2025-01-14  
> **目标**: 解决第三方应用无法获取成员对外显示名称和头像的问题

---

## 1. 问题背景

### 当前困境
**应用类型**: 普通第三方应用（电子名片）  
**企业微信限制**: 第三方普通应用调用 `user/get` 接口时：
- ❌ `name` 字段返回 `userid`（代码），而非真实姓名
- ❌ `avatar` 字段无法获取（返回空）
- ❌ `mobile`、`position`、`email` 等敏感字段无法获取

### 官方解决方案
根据企业微信官方文档（`/opt/qwcard/docs/0000企微接口.md` 第397-399行）：
> 从2022年6月20号20点开始，新创建的自建应用与代开发应用，调用该接口时，不再返回以下字段：头像、性别、手机、邮箱、企业邮箱、员工个人二维码、地址，**应用需要通过oauth2手工授权的方式获取管理员与员工本人授权的字段**。

**解决方案**: 通过 **OAuth2手工授权** 让员工授权后获取敏感信息

---

## 2. 方案设计

### 2.1 核心流程

```
员工首次访问 /wecom/card
    ↓
检测是否需要授权（成员信息不完整）
    ↓
是 → 引导OAuth2授权流程
    ↓
用户同意授权（授权可见范围：snsapi_privateinfo）
    ↓
回调接口获取授权code
    ↓
使用code调用 getuserdetail 接口
    ↓
获取完整信息：对外显示名称、头像、手机号、职位等
    ↓
更新Member表，标记已授权
    ↓
跳转到名片页面，显示正确信息
```

### 2.2 关键接口

#### OAuth2授权URL
```
https://open.weixin.qq.com/connect/oauth2/authorize?appid={SUITE_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=snsapi_privateinfo&state=STATE#wechat_redirect
```

**关键参数**:
- `scope=snsapi_privateinfo`: 获取成员敏感信息（需要用户授权）
- `redirect_uri`: 授权后回调地址

#### getuserdetail接口（获取授权成员信息）
```
POST https://qyapi.weixin.qq.com/cgi-bin/service/getuserdetail3rd?access_token=SUITE_ACCESS_TOKEN

{
  "user_ticket": "USER_TICKET"
}
```

**返回字段**:
```json
{
  "errcode": 0,
  "errmsg": "ok",
  "corpid": "wxf8b4f85f3a794e77",
  "userid": "ZhangSan",
  "name": "张三",  // ✅ 对外显示名称
  "avatar": "http://wx.qlogo.cn/xxx",  // ✅ 头像
  "mobile": "13800000000",  // ✅ 手机号
  "position": "产品经理",  // ✅ 职位
  "email": "zhangsan@example.com",
  "gender": "1",
  "qr_code": "https://open.work.weixin.qq.com/wwopen/userQRCode?vcode=xxx",
  "external_position": "高级产品经理"  // ✅ 对外职位
}
```

---

## 4. 用户体验优化

### 4.1 授权引导设计

**设计原则**:
- ✅ 清晰说明授权目的
- ✅ 列出需要获取的权限
- ✅ 强调隐私保护承诺
- ✅ 提供"暂不授权"选项

**弹窗内容**:
```
🔐 需要您的授权

为了正确显示您的名片信息，我们需要获取您的：

👤 对外显示名称
📷 头像
📱 手机号码
💼 职位信息

这些信息将仅用于生成您的企业名片，我们承诺保护您的隐私。

[同意授权] [暂不授权]
```

### 4.2 授权时机

**首次访问**:
1. 员工首次打开 `/wecom/card`
2. 检测成员信息不完整
3. 自动弹出授权引导
4. 用户同意后跳转企微OAuth
5. 授权完成后自动返回，显示完整名片

**后续访问**:
- 已授权用户直接显示名片
- 无需重复授权
- 信息自动保持更新

### 4.3 异常处理

**用户拒绝授权**:
```
❌ 您取消了授权

没有授权将无法显示完整的名片信息。

[重新授权] [返回首页]
```

**授权失败**:
```
⚠️ 授权过程出现错误

可能的原因：
- 网络连接不稳定
- 企业微信服务暂时不可用
- 权限配置有误

[重试] [联系管理员]
```

---

## 5. 安全与隐私

### 5.1 数据安全

**传输安全**:
- ✅ 全程HTTPS加密传输
- ✅ OAuth2标准流程，不涉及密码
- ✅ Token有效期限制（12小时）

**存储安全**:
- ✅ 敏感信息加密存储
- ✅ 遵循企业微信数据使用规范
- ✅ 不对外泄露用户信息

### 5.2 隐私保护

**数据使用范围**:
- ✅ 仅用于生成员工名片
- ✅ 仅在企业内部流转
- ✅ 不用于其他商业用途

**用户权利**:
- ✅ 随时可以撤销授权
- ✅ 可以要求删除个人信息
- ✅ 可以查看数据使用记录

---

## 6. 测试验证

### 6.1 测试流程

**步骤1：准备测试账号**
1. 准备一个普通员工账号（未配置对外信息）
2. 确保该员工在应用可见范围内
3. 清空该员工在Member表中的记录（模拟首次访问）

**步骤2：测试OAuth授权流程**
```sql
-- 清空测试员工的授权状态
UPDATE members 
SET oauth_authorized = FALSE, 
    name = NULL, 
    avatar_url = NULL,
    mobile = NULL
WHERE userid = 'test_user_001';
```

**步骤3：访问名片页面**
1. 使用测试员工账号访问 `/wecom/card`
2. 应该自动弹出授权引导弹窗
3. 点击"同意授权"
4. 跳转到企业微信OAuth授权页面
5. 同意授权后自动返回
6. 名片页面显示完整信息

**步骤4：验证数据**
```sql
-- 检查员工信息是否更新
SELECT 
    userid,
    name,
    avatar_url,
    mobile,
    position,
    oauth_authorized,
    oauth_authorized_at
FROM members
WHERE userid = 'test_user_001';
```

### 6.2 测试检查点

| 检查点 | 预期结果 | 实际结果 |
|--------|---------|---------|
| 授权弹窗显示 | ✅ 弹窗正常显示 | |
| OAuth跳转 | ✅ 跳转到企微授权页 | |
| 授权回调 | ✅ 成功返回名片页面 | |
| 名称显示 | ✅ 显示中文名字（对外显示名称） | |
| 头像显示 | ✅ 显示正确头像 | |
| 数据库更新 | ✅ oauth_authorized=TRUE | |
| 后续访问 | ✅ 不再弹出授权，直接显示 | |

### 6.3 边界测试

**测试场景1：用户取消授权**
- 操作：点击企微授权页面的"取消"
- 预期：返回名片页面，显示"您取消了授权"提示

**测试场景2：授权超时**
- 操作：授权页面停留超过5分钟
- 预期：显示授权超时提示，引导重新授权

**测试场景3：网络异常**
- 操作：授权过程中断网
- 预期：显示网络错误提示，提供重试选项

---

## 7. 部署清单

### 7.1 后端修改

**文件清单**:
```
/opt/qwcard/app/routes/wecom.py
├── [修改] get_my_card() - 添加OAuth检测逻辑
├── [新增] generate_oauth_url() - 生成OAuth授权URL
└── [新增] oauth_callback() - 处理OAuth回调

/opt/qwcard/app/models.py
└── [修改] Member模型 - 新增oauth相关字段
```

**数据库迁移**:
```sql
-- 执行以下SQL脚本
ALTER TABLE members
ADD COLUMN oauth_authorized BOOLEAN DEFAULT FALSE COMMENT '是否已OAuth授权',
ADD COLUMN oauth_authorized_at DATETIME COMMENT 'OAuth授权时间',
ADD COLUMN user_ticket VARCHAR(512) COMMENT '用户票据',
ADD INDEX idx_oauth_authorized (oauth_authorized);
```

### 7.2 前端修改

**文件清单**:
```
/opt/qwcard/pages/wecom/card.vue
├── [修改] template - 添加授权弹窗
├── [修改] data - 添加needOAuth、oauthUrl
├── [修改] mounted - 检查OAuth回调
├── [修改] loadCard - 检测need_oauth标记
├── [新增] handleOAuthAuthorize() - 处理授权
└── [新增] handleOAuthCancel() - 取消授权
```

### 7.3 环境配置

**检查清单**:
- ✅ WECOM_SUITE_ID 配置正确
- ✅ WECOM_SUITE_SECRET 配置正确
- ✅ 回调域名 zjemail.cn 已配置
- ✅ JWT_SECRET 已配置
- ✅ Redis 服务正常运行
- ✅ MySQL 数据库连接正常

### 7.4 部署步骤

```bash
# 1. 备份数据库
mysqldump -u wecard -p wecard > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 执行数据库迁移
mysql -u wecard -p wecard < /opt/qwcard/migrations/add_oauth_fields.sql

# 3. 拉取最新代码
cd /opt/qwcard
git pull origin main

# 4. 重启服务
ps aux | grep -E "gunicorn.*wsgi" | grep -v grep | head -1 | awk '{print $2}' | xargs kill -HUP

# 5. 验证服务状态
curl http://127.0.0.1:5001/healthz
# 预期返回: {"status":"ok"}

# 6. 查看日志
tail -f /var/log/gunicorn.log | grep -E "OAuth|授权"
```

---

## 8. 监控与维护

### 8.1 关键指标

**授权转化率**:
```sql
-- 统计授权情况
SELECT 
    COUNT(*) as total_members,
    SUM(CASE WHEN oauth_authorized = TRUE THEN 1 ELSE 0 END) as authorized_count,
    ROUND(SUM(CASE WHEN oauth_authorized = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as authorization_rate
FROM members
WHERE is_active = TRUE;
```

**授权时间分布**:
```sql
-- 按日期统计授权数量
SELECT 
    DATE(oauth_authorized_at) as auth_date,
    COUNT(*) as auth_count
FROM members
WHERE oauth_authorized = TRUE
GROUP BY DATE(oauth_authorized_at)
ORDER BY auth_date DESC
LIMIT 30;
```

### 8.2 日志监控

**关键日志**:
```bash
# 监控OAuth授权流程
tail -f /var/log/gunicorn.log | grep "OAuth"

# 关键日志格式：
# 📱 OAuth授权回调: code=xxx, state=oauth_member_info
# 📥 getuserinfo3rd返回: {...}
# 📥 getuserdetail3rd返回: {...}
# ✅ OAuth授权成功: userid=xxx, name=xxx
# ❌ OAuth授权处理失败: ...
```

### 8.3 告警规则

**授权失败率过高**:
```
IF (授权失败数 / 授权尝试数) > 10% IN last 1 hour
THEN 发送告警通知
```

**授权转化率过低**:
```
IF 授权转化率 < 80% IN last 7 days
THEN 提示优化授权流程
```

---

## 9. 常见问题

### Q1: 用户看到的是什么授权界面？
**A**: 企业微信官方的OAuth授权页面，类似这样：
```
企业微信

[您的应用名称] 申请获得以下权限：

✓ 访问您的成员信息（姓名、头像、手机号、职位）

同意授权后，该应用将获得您的成员信息。

[同意]  [取消]
```

### Q2: 授权后信息会自动更新吗？
**A**: 会的。每次用户访问时，如果检测到信息过期（如超过30天），会自动触发后台更新，无需用户重新授权。

### Q3: 用户可以撤销授权吗？
**A**: 可以。用户可以在企业微信中进入"应用管理"，找到您的应用，点击"取消授权"。撤销后下次访问会重新引导授权。

### Q4: OAuth授权和之前的认证有什么区别？
**A**: 
- **之前的认证**：只验证用户身份（谁在访问）
- **OAuth授权**：额外获取用户敏感信息（姓名、头像、手机号等）
- 两者配合使用，共同完成身份验证和信息获取

### Q5: 如果用户一直不授权会怎样？
**A**: 用户可以选择"暂不授权"，但名片会显示不完整（userid代替姓名，无头像），影响使用体验。建议在授权引导中说明授权的必要性。

### Q6: 授权信息会过期吗？
**A**: `user_ticket` 有效期较短（通常几分钟），但我们会将获取到的成员信息存储到数据库，后续访问直接使用存储的信息，不会过期。如需更新信息，可以触发重新授权。

### Q7: 多久需要重新授权一次？
**A**: 理论上授权一次即可永久使用。但为了数据准确性，建议每隔30-90天检测一次信息是否有更新，如有变化提示用户重新授权。

---

## 10. 优化建议

### 10.1 短期优化（立即实施）

**1. 添加授权提示图标**
在名片顶部显示授权状态：
```
✅ 已授权 | ⚠️ 信息不完整，建议授权
```

**2. 记录授权失败原因**
在Member表添加字段：
```sql
ADD COLUMN oauth_fail_reason VARCHAR(255) COMMENT '授权失败原因';
```

**3. 添加授权统计页面**
供管理员查看：
- 授权人数 / 总人数
- 授权转化率
- 失败原因统计

### 10.2 中期优化（1-2周）

**1. 自动刷新机制**
当检测到成员信息在企微后台有更新时，自动触发后台更新：
```python
# 定时任务：每天凌晨检查并更新
@scheduler.task('cron', hour=3)
def refresh_member_info():
    # 查找30天未更新的已授权成员
    # 使用 user_ticket 静默刷新信息
    pass
```

**2. 授权引导优化**
- 添加动画效果
- 使用更友好的文案
- 提供授权示例截图

**3. 灰度发布**
先对20%的员工启用OAuth授权，观察效果后再全量发布。

### 10.3 长期优化（1-3月）

**1. 智能授权提醒**
- 检测到信息不完整时，发送企微消息提醒
- 在管理员工作台显示未授权员工列表

**2. 授权数据分析**
- 授权路径分析
- 放弃原因分析
- A/B测试不同授权文案

**3. 合规性审计**
- 定期检查数据使用合规性
- 生成隐私保护报告
- 提供用户数据导出功能

---

## 11. 总结

### 核心要点

1. **问题根源**: 第三方普通应用无法直接获取员工的对外显示名称、头像等敏感信息
2. **解决方案**: 通过OAuth2手工授权让员工主动授权
3. **关键接口**: `getuserinfo3rd` + `getuserdetail3rd`
4. **用户体验**: 首次访问时弹出授权引导，授权后永久生效
5. **数据安全**: 全程HTTPS加密，遵循企微数据使用规范

### 实施优先级

| 优先级 | 任务 | 预计工时 |
|--------|------|---------|
| P0 | 数据库迁移（添加oauth字段） | 0.5h |
| P0 | 后端接口开发（oauth_callback） | 3h |
| P0 | 前端授权弹窗开发 | 2h |
| P1 | 测试验证（各种场景） | 2h |
| P1 | 部署上线 | 1h |
| P2 | 监控告警配置 | 1h |
| P3 | 优化迭代 | 持续 |

**总计**: 约10小时可完成核心功能开发和部署

### 预期效果

**实施前**:
- ❌ 名片显示 userid（如：ZhangSan）
- ❌ 无头像显示
- ❌ 用户体验差

**实施后**:
- ✅ 名片显示真实姓名（如：张三）
- ✅ 显示正确头像
- ✅ 显示完整联系方式
- ✅ 授权转化率预计 > 85%
- ✅ 用户体验提升明显

---

**文档维护**: WeCard开发组  
**技术支持**: 企业微信OAuth2授权机制  
**最后更新**: 2025-01-14  
**文档版本**: v1.0


## 3. 技术实施

### 3.1 数据库设计

#### Member表新增字段
```sql
ALTER TABLE members
ADD COLUMN oauth_authorized BOOLEAN DEFAULT FALSE COMMENT '是否已OAuth授权',
ADD COLUMN oauth_authorized_at DATETIME COMMENT 'OAuth授权时间',
ADD COLUMN user_ticket VARCHAR(512) COMMENT '用户票据（用于刷新）',
ADD COLUMN INDEX idx_oauth_authorized (oauth_authorized);
```

### 3.2 后端实现

#### 3.2.1 检测是否需要授权
**文件**: `/opt/qwcard/app/routes/wecom.py`

在 `get_my_card` 接口中添加检测逻辑：

```python
@bp.route('/card/my', methods=['GET'])
def get_my_card():
    """获取当前用户的名片数据"""
    # ... 现有认证逻辑 ...
    
    # 查询成员信息
    member = Member.query.filter_by(tenant_id=tenant_id, userid=userid).first()
    
    # ✅ 检测是否需要OAuth授权
    needs_oauth = False
    if not member:
        needs_oauth = True
    elif not member.oauth_authorized:
        # 检查关键字段是否完整
        if (not member.name or member.name == userid or 
            not member.avatar_url or 
            not member.mobile):
            needs_oauth = True
    
    # ✅ 如果需要授权，返回特殊标记
    if needs_oauth:
        return jsonify({
            'success': False,
            'need_oauth': True,
            'oauth_url': generate_oauth_url(redirect_uri='/wecom/oauth/callback'),
            'message': '需要授权以获取您的完整信息'
        })
    
    # ... 返回名片数据 ...
```

#### 3.2.2 生成OAuth授权URL
```python
def generate_oauth_url(redirect_uri, state='oauth_member_info'):
    """
    生成OAuth2授权URL
    
    Args:
        redirect_uri: 授权回调地址（相对路径）
        state: 状态标识
    
    Returns:
        完整的OAuth授权URL
    """
    base_url = 'https://open.weixin.qq.com/connect/oauth2/authorize'
    
    # 构建完整的回调URL
    full_redirect_uri = f'{request.url_root.rstrip("/")}{redirect_uri}'
    
    params = {
        'appid': WECOM_CONFIG['suite_id'],
        'redirect_uri': quote(full_redirect_uri),
        'response_type': 'code',
        'scope': 'snsapi_privateinfo',  # ✅ 关键：获取敏感信息
        'state': state
    }
    
    oauth_url = f"{base_url}?{urlencode(params)}#wechat_redirect"
    
    return oauth_url
```

#### 3.2.3 OAuth回调处理
**新增接口**: `/api/v1/wecom/oauth/callback`

```python
@bp.route('/oauth/callback', methods=['GET'])
def oauth_callback():
    """
    OAuth2授权回调接口
    处理用户授权后的回调，获取完整成员信息
    """
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return jsonify({'error': '授权失败，缺少code参数'}), 400
    
    print(f'📱 OAuth授权回调: code={code[:10]}..., state={state}', file=sys.stderr, flush=True)
    
    try:
        # 1. 使用code获取用户详细信息
        suite_access_token = get_suite_access_token()
        if not suite_access_token:
            raise Exception('获取suite_access_token失败')
        
        # 2. 调用 getuserinfo3rd 获取 user_ticket
        user_info_url = f'https://qyapi.weixin.qq.com/cgi-bin/service/getuserinfo3rd?suite_access_token={suite_access_token}&code={code}'
        resp = requests.get(user_info_url, timeout=10)
        user_info_data = resp.json()
        
        print(f'📥 getuserinfo3rd返回: {user_info_data}', file=sys.stderr, flush=True)
        
        if user_info_data.get('errcode') != 0:
            raise Exception(f"getuserinfo3rd失败: {user_info_data}")
        
        user_ticket = user_info_data.get('user_ticket')
        corp_id = user_info_data.get('CorpId')
        userid = user_info_data.get('userid') or user_info_data.get('UserId')
        
        if not user_ticket:
            raise Exception('未获取到user_ticket，可能用户未授权敏感信息')
        
        # 3. 使用 user_ticket 调用 getuserdetail 获取完整信息
        detail_url = f'https://qyapi.weixin.qq.com/cgi-bin/service/getuserdetail3rd?access_token={suite_access_token}'
        detail_resp = requests.post(detail_url, json={'user_ticket': user_ticket}, timeout=10)
        detail_data = detail_resp.json()
        
        print(f'📥 getuserdetail3rd返回: {detail_data}', file=sys.stderr, flush=True)
        
        if detail_data.get('errcode') != 0:
            raise Exception(f"getuserdetail失败: {detail_data}")
        
        # 4. 更新Member表
        tenant = Tenant.query.filter_by(corp_id=corp_id).first()
        if not tenant:
            raise Exception(f'未找到企业: {corp_id}')
        
        member = Member.query.filter_by(tenant_id=tenant.id, userid=userid).first()
        if not member:
            member = Member(tenant_id=tenant.id, userid=userid)
            db.session.add(member)
        
        # ✅ 更新完整信息
        member.name = detail_data.get('name') or userid  # 对外显示名称
        member.avatar_url = detail_data.get('avatar', '')
        member.mobile = detail_data.get('mobile', '')
        member.email = detail_data.get('email', '')
        member.position = detail_data.get('external_position') or detail_data.get('position', '')
        member.gender = detail_data.get('gender')
        member.qr_code = detail_data.get('qr_code', '')
        
        # ✅ 标记已授权
        member.oauth_authorized = True
        member.oauth_authorized_at = datetime.now()
        member.user_ticket = user_ticket
        
        db.session.commit()
        
        print(f'✅ OAuth授权成功: userid={userid}, name={member.name}', file=sys.stderr, flush=True)
        
        # 5. 生成JWT token
        token = generate_jwt_token({
            'tenant_id': tenant.id,
            'corp_id': corp_id,
            'userid': userid,
            'role': 'user',
            'is_admin': False
        })
        
        # 6. 重定向到名片页面，携带token
        redirect_url = f'/wecom/card?token={token}&oauth_success=1'
        
        return redirect(redirect_url)
        
    except Exception as error:
        print(f'❌ OAuth授权处理失败: {error}', file=sys.stderr, flush=True)
        return jsonify({
            'error': 'OAuth授权失败',
            'message': str(error)
        }), 500
```

### 3.3 前端实现

#### 3.3.1 修改 card.vue
**文件**: `/opt/qwcard/pages/wecom/card.vue`

```vue
<template>
  <div class="wecom-card-view">
    <!-- 授权引导弹窗 -->
    <div v-if="needOAuth" class="oauth-modal">
      <div class="oauth-content">
        <div class="oauth-icon">🔐</div>
        <h2>需要您的授权</h2>
        <p class="oauth-desc">
          为了正确显示您的名片信息，我们需要获取您的：
        </p>
        <ul class="oauth-permissions">
          <li><span class="icon">👤</span> 对外显示名称</li>
          <li><span class="icon">📷</span> 头像</li>
          <li><span class="icon">📱</span> 手机号码</li>
          <li><span class="icon">💼</span> 职位信息</li>
        </ul>
        <p class="oauth-tip">
          这些信息将仅用于生成您的企业名片，我们承诺保护您的隐私。
        </p>
        <button class="oauth-btn" @click="handleOAuthAuthorize">
          同意授权
        </button>
        <button class="oauth-btn-cancel" @click="handleOAuthCancel">
          暂不授权
        </button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>正在加载名片...</p>
    </div>

    <!-- 名片内容 -->
    <div v-else-if="cardData" class="card-wrapper">
      <WecardOptimized
        :card-data="cardData"
        :card-id="cardId"
        :theme="cardTheme"
        :show-options="{
          showContactDetails: true,
          showBusinessSection: true,
          showSocialLinks: true,
          showSaveButton: true
        }"
        :is-wecom-env="isWecomEnv"
        :contact-visibility="cardData.contact_visibility || {}"
        :logo-config="cardData.logo_config || {}"
        :header-background="cardData.header_background || {}"
        :show-share-panel="false"
        @track-event="handleTrackEvent"
        @analytics-event="handleAnalyticsEvent"
      />
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <div class="error-card">
        <span class="error-icon">⚠️</span>
        <h3>{{ error }}</h3>
        <p v-if="errorDetail">{{ errorDetail }}</p>
        <button class="retry-btn" @click="loadCard">重试</button>
      </div>
    </div>
  </div>
</template>

<script>
import WecardOptimized from '@/components/WecardOptimized.vue'

export default {
  name: 'WecomCardView',
  
  components: {
    WecardOptimized
  },
  
  data() {
    return {
      isLoading: true,
      cardData: null,
      cardId: null,
      cardTheme: 'light',
      error: null,
      errorDetail: null,
      isWecomEnv: false,
      needOAuth: false,      // ✅ 是否需要OAuth授权
      oauthUrl: ''           // ✅ OAuth授权URL
    }
  },
  
  async mounted() {
    console.log('🎴 企微名片页面加载')
    
    // 检测是否在企微环境
    this.isWecomEnv = /wxwork/i.test(navigator.userAgent)
    
    // ✅ 检查是否是OAuth回调返回
    const oauthSuccess = this.$route.query.oauth_success
    const token = this.$route.query.token
    
    if (oauthSuccess === '1' && token) {
      console.log('✅ OAuth授权成功，保存token')
      this.$wecomAuth.setToken(token)
      // 清除URL参数
      this.$router.replace({ query: {} })
    }
    
    // 处理OAuth认证
    const code = this.$route.query.code
    
    if (code) {
      console.log('📱 检测到OAuth code，开始验证用户身份...')
      try {
        const { data } = await this.$axios.get('/api/v1/wecom/auth/verify_user', {
          params: {
            code,
            target: 'card',
            allow_non_admin: true
          }
        })
        
        if (data.success) {
          this.$wecomAuth.setToken(data.token)
          this.$wecomAuth.setUserInfo(data.user)
          console.log('✅ 认证成功:', data.user)
          
          // 清除URL中的code参数
          this.$router.replace({ query: {} })
        } else {
          throw new Error(data.message || '认证失败')
        }
      } catch (error) {
        console.error('❌ 认证失败:', error)
        this.error = '认证失败'
        this.errorDetail = error.response?.data?.message || error.message
        this.isLoading = false
        return
      }
    }
    
    // 检查token
    if (!this.$wecomAuth.isAuthenticated()) {
      console.log('⚠️ 未检测到token，发起OAuth授权')
      if (!code) {
        await this.redirectToAuth()
        return
      }
    }
    
    // 验证token有效性
    const isValid = await this.$wecomAuth.verifyToken()
    if (!isValid) {
      console.log('⚠️ Token已失效，重新认证')
      this.$wecomAuth.clearAuth()
      await this.redirectToAuth()
      return
    }
    
    // 加载名片数据
    await this.loadCard()
  },
  
  methods: {
    async loadCard() {
      this.isLoading = true
      this.error = null
      this.errorDetail = null
      
      try {
        console.log('📋 加载用户名片数据...')
        
        // 调用后端API获取当前用户的名片数据
        const { data } = await this.$axios.get('/api/v1/wecom/card/my')
        
        // ✅ 检查是否需要OAuth授权
        if (data.need_oauth) {
          console.log('⚠️ 需要OAuth授权')
          this.needOAuth = true
          this.oauthUrl = data.oauth_url
          this.isLoading = false
          return
        }
        
        if (data.success) {
          this.cardData = data.card_data
          this.cardId = data.card_id
          this.cardTheme = data.theme || 'light'
          console.log('✅ 名片数据加载成功')
        } else {
          throw new Error(data.message || '加载名片失败')
        }
      } catch (error) {
        console.error('❌ 加载名片失败:', error)
        
        if (error.response?.status === 401) {
          // Token失效，重新认证
          this.$wecomAuth.clearAuth()
          await this.redirectToAuth()
        } else if (error.response?.status === 404) {
          this.error = '名片不存在'
          this.errorDetail = '管理员还没有为您配置名片，请联系管理员'
        } else {
          this.error = '加载名片失败'
          this.errorDetail = error.response?.data?.message || error.message
        }
      } finally {
        this.isLoading = false
      }
    },
    
    // ✅ 处理OAuth授权
    handleOAuthAuthorize() {
      console.log('📱 用户点击授权，跳转到OAuth授权页面')
      if (this.oauthUrl) {
        window.location.href = this.oauthUrl
      } else {
        this.$toast?.error('授权链接无效，请刷新重试')
      }
    },
    
    // ✅ 取消授权
    handleOAuthCancel() {
      console.log('⚠️ 用户取消授权')
      this.needOAuth = false
      this.error = '您取消了授权'
      this.errorDetail = '没有授权将无法显示完整的名片信息，如需继续请刷新页面重新授权'
    },
    
    async redirectToAuth() {
      const redirectUri = window.location.origin + this.$route.path
      const authUrl = await this.$wecomAuth.getAuthUrl(redirectUri)
      window.location.href = authUrl
    },
    
    handleTrackEvent(eventData) {
      console.log('📊 追踪事件:', eventData)
    },
    
    handleAnalyticsEvent(eventData) {
      console.log('📈 分析事件:', eventData)
    }
  }
}
</script>

<style lang="scss" scoped>
/* OAuth授权弹窗 */
.oauth-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.oauth-content {
  background: #ffffff;
  border-radius: 16px;
  padding: 32px 24px;
  max-width: 400px;
  width: 100%;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.oauth-icon {
  font-size: 64px;
  margin-bottom: 16px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.oauth-content h2 {
  font-size: 24px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 12px 0;
}

.oauth-desc {
  font-size: 14px;
  color: #595959;
  margin: 0 0 20px 0;
  line-height: 1.6;
}

.oauth-permissions {
  list-style: none;
  padding: 0;
  margin: 0 0 20px 0;
  text-align: left;
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px 20px;
}

.oauth-permissions li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  font-size: 14px;
  color: #262626;
}

.oauth-permissions li .icon {
  font-size: 20px;
  flex-shrink: 0;
}

.oauth-tip {
  font-size: 12px;
  color: #8c8c8c;
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.oauth-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.oauth-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.oauth-btn:active {
  transform: translateY(0);
}

.oauth-btn-cancel {
  width: 100%;
  padding: 12px;
  background: transparent;
  color: #8c8c8c;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.oauth-btn-cancel:hover {
  border-color: #667eea;
  color: #667eea;
}

/* 其他样式保持不变 */
.wecom-card-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #ffffff;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #1890ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  p {
    margin-top: 16px;
    color: #666;
    font-size: 14px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.card-wrapper {
  max-width: 100%;
  margin: 0 auto;
  background: #ffffff;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background: #f5f5f5;
}

.error-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  
  .error-icon {
    font-size: 48px;
    display: block;
    margin-bottom: 16px;
  }
  
  h3 {
    margin: 0 0 12px 0;
    color: #262626;
    font-size: 20px;
    font-weight: 600;
  }
  
  p {
    margin: 0 0 24px 0;
    color: #8c8c8c;
    font-size: 14px;
    line-height: 1.6;
  }
  
  .retry-btn {
    padding: 10px 24px;
    background: #1890ff;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      background: #40a9ff;
    }
    
    &:active {
      background: #096dd9;
    }
  }
}
</style>

企业通讯录是企业的重要敏感数据，第三方将不再直接获取到授权企业的通讯录数据（接口将不再返回人名与部门名）。第三方页面若需要展示用户的通讯录信息，可使用如下的 open-data 组件，以提供更加安全良好的体验。

相关概念可以参考微信小程序的 open-data 组件。
常见问题可参考 FAQ
2. 浏览器方案
2.1 环境要求
企业微信APP需 2.8.10 及以上版本
2.2 使用方法
1. 通过企业微信登录应用管理后台

在非微信、企业微信内置浏览器中使用 open-data 时，需要通过企业微信管理端跳转（应用详情页中的“业务设置--前往服务商后台”）或第三方登录授权进行登录。

需要注意，通过上述方法登录跳转的目标域名要和使用 open-data 的页面域名保持一致。

在开发过程中，我们可以在 open-data 调试页面中查看当前浏览器登录的应用信息。

2. 引入 open-data SDK

有两种方式引入 SDK：

直接在页面上引入以下SDK：
<script src="https://res.wx.qq.com/open/js/jweixin-1.2.0.js" referrerpolicy="origin"></script>
<script src="https://open.work.weixin.qq.com/wwopen/js/jwxwork-1.0.0.js" referrerpolicy="origin"></script>


sdk 内容是动态返回的，请严格按照上面的方式引入，不要保存到项目本地后打包引入

referrerpolicy 声明为 origin 是为了让 sdk 能够顺利识别关键域名，不能去掉


通过 npm 安装 @wecom/jssdk
具体使用方法请参考 npm 包的文档上关于 OpenData 的说明；
其中，初始化通讯录组件的必要流程为：
ww.register({
	...
	getAgentConfigSignature: async () => {
		// signature
	}
})
ww.initOpenData({
	success() {
		// ready
	}
})
3. 进行 agentConfig

如果是使用 @wecom/jssdk，参照对应文档注册 agentConfig 签名方法即可，不需要自行执行 wx.agentConfig；
无论是微信、企业微信的内置浏览器还是第三方浏览器，都需要通过wx.agentConfig登记第三方应用的身份信息。

需要注意，在第三方浏览器中调用 wx.agentConfig 前不需要进行 wx.config。而在企业微信客户端的页面上，进行 agentConfig 的调用，必须要等 wx.config 完成后才调用（即 wx.config 的成功回调）。

注意：进行agentConfig之前要确保用户已经通过企业微信登录应用的页面，即用户已经通过企业微信管理端跳转（应用详情页中的“业务设置--前往服务商后台”）或第三方登录授权进入到应用的页面。

4. 绑定 open-data 元素

上述步骤完成后，我们就可以通过 WWOpenData.bind 方法对页面上的元素进行绑定，完成后 SDK 将在绑定的元素上渲染出对应的开放数据：

<!-- 注意：这里的 openid 是 userid 和 departmentid 的统称 -->
<ww-open-data type="userName" openid="{{openid}}"></ww-open-data>
<script>
	WWOpenData.bind(document.querySelector('ww-open-data'))
</script>
open-data 元素上的属性请参考[2.5 元素属性](#17172/2.5 元素属性)章节。
在支持 custom elements 的浏览器中，SDK 会自动对 <ww-open-data> 元素进行绑定。
2.3 API 列表
WWOpenData.bind(el: Element)

绑定 open-data 元素，在获取数据后，SDK 将在元素内渲染出对应的开放数据。

WWOpenData.bindAll(nodeList: NodeList | Array<Element>)

批量绑定 open-data 元素，参考 WWOpenData.bind。

注意：为了保证在所有环境下表现正常，一旦 open-data 元素的内容发生了变化，必须调用 WWOpenData.bind 接口重新绑定一次

WWOpenData.on(event: string, callback: Function)

为兼容旧版本终端，使用前需要判断函数是否存在

添加事件监听函数，事件列表参考[2.4 事件列表](#17172/2.4 事件列表)。

WWOpenData.off(event: string, callback: Function)

为兼容旧版本终端，使用前需要判断函数是否存在

移除事件监听函数。

WWOpenData.checkSession(params: CheckSessionParams)

为兼容旧版本终端，使用前需要判断函数是否存在

检查登录态信息。

if (WWOpenData.checkSession) {
	WWOpenData.checkSession({
		success() {
			console.log('有登录态')
		},
		fail() {
			console.error('登录态过期')
		}
	})
}
WWOpenData.initCanvas()

启动 canvas 支持功能

WWOpenData.prefetch(params: PrefetchParams)

预加载通讯录数据

if (WWOpenData.prefetch) {
	WWOpenData.prefetch({ items }, (err, data) => {
		if (err) {
			// 错误处理
		}
		// 数据处理
	})
}
注意：出于安全设计和浏览器策略，prefetch 接口必须在 https 的网页下调用，否则会报运行错误

 

2.4 事件列表
error

当 SDK 获取数据失败时触发。

update

当 open-data 元素渲染内容发生变更时触发。

2.5 元素属性
页面通过 open-data 元素上的属性控制需要渲染的内容：

属性	类型	必填	说明
type	string	是	开放数据类型
openid	string	是	数据ID，根据type取值而定
corpid	string	否	企业ID，用户所属的企业 corpid
假设有“上下游”或“教育局校互联”企业 A 和 B, 开发者需要在页面同时渲染 A和B的通讯录数据，这时可以通过填入特定企业的 corpid，去指定要渲染的企业数据
type 的合法值

值	说明
userName	用户名称
userAlias	用户别名
userAliasOrName	用户别名或名称，优先展示别名
departmentName	部门名称
若 type=userName，此时 openid 对应 userid
若 type=userAlias，此时 openid 对应 userid。如果用户没有别名，将返回传入的openid
若 type=userAliasOrName，此时openid对应userid。如果用户有别名，将返回用户别名；否则将返回用户名称
若 type=departmentName，此时 openid 对应 departmentid
每 20ms 最多绑定 1000 个 open-data 元素，超出的部分将被忽略
如果用户或部门不合法，将返回传入的openid
2.6 前端框架适配
若页面使用了 vue、react 等前端框架，可在框架提供的钩子函数中调用 WWOpenData.bind 进行绑定：

Vue

<template>
	<ww-open-data :type="type" :openid="openid" />
</template>

<script>
export default {
	props: ['type', 'openid'],
	mounted() {
		WWOpenData.bind(this.$el)
	}
}
</script>
React

import React, { useRef, useLayoutEffect } from 'react'

export default function WWOpenDataCom({ type, openid }) {
	const ref = useRef(null)
	useLayoutEffect(() => {
		WWOpenData.bind(ref.current)
	})
	return <ww-open-data ref={ref} type={type} openid={openid} />
}
2.7 示例代码
<html>
<body>
	<ww-open-data type="userName" openid="{{openid}}"></ww-open-data>
	<script src="//res.wx.qq.com/open/js/jweixin-1.2.0.js"></script>
	<script src="//open.work.weixin.qq.com/wwopen/js/jwxwork-1.0.0.js"></script>
	<script>
		(async () => {
			if (/MicroMessenger/i.test(navigator.userAgent)) {
				await config(configParams)
			}
			await agentConfig(agentConfigParams)
			// 注意: 在企业微信平台下，只有 agentConfig 成功回调后，WWOpenData 才会注入到 window 对象上面
			WWOpenData.bindAll(document.querySelectorAll('ww-open-data'))
		})()
		function config(config) {
			return new Promise((resolve, reject) => {
				wx.config(config)
				wx.ready(resolve)
				wx.error(reject)
			})
		}
		function agentConfig(config) {
			return new Promise((success, fail) => {
				wx.agentConfig({ ...config, success, fail })
			})
		}
	</script>
</body>
</html>
更加完整的示例程序，可以参考 open-data 控件 demo。

 

3. 小程序方案
3.1 环境要求
企业微信APP需 2.8.9 及以上版本
微信上小程序基础库版本需 1.9.6 及以上版本
开发者工具中不要在企业微信小程序模式下运行插件
注意：当前小程序通讯录展示插件不支持显示头像

3.2 使用方法
(1) 开发者在小程序管理后台申请使用插件，添加路径：设置 ->第三方服务 -> 插件管理 -> 添加插件，搜索并添加插件ID： wx5917c8c26f85c588，无需审核确认。
(2) 开发者在小程序app.json 文件中添加对插件的引用

"plugins": {
	"contactPlugin": {
		"version": "2.1.0",
		"provider": "wx5917c8c26f85c588"
	}
}
(3) 开发者在具体引用插件的页面文件json文件中，添加对组件的引用，例如：

"usingComponents": {
	"ww-open-data":"plugin://contactPlugin/ww-open-data"
}
(4) 在 wxml 中调用 ww-open-data 组件展示用户信息：

<ww-open-data
  type="{{type}}"
  corpid="{{corpid}}"
  openid="{{openid}}"
  bindupdate="onDataUpdate"
/>
参数说明：

属性	类型	必填	说明	最低版本
type	string	是	开放数据类型	1.0.0
corpid	string	是	用户所属的企业corpid	1.0.0
openid	string	是	数据ID，根据type取值而定	1.0.0
bindupdate	eventhandle	否	当组件展示的数据发生变更时触发，event.detail = { type, corpid, openid, hasData }	2.1.0
type 与 openid 属性参考[2.5 元素属性](#17172/2.4 元素属性)
假设有上下游企业 A 和 B, 开发者需要在页面同时渲染 A和B的通讯录数据，这时可以通过填入特定企业的 corpid，去指定要渲染的企业数据
 

3.3 开发调试
在开发者工具开发调试，需要用企业微信扫码运行时，需要在“添加编译模式”里的启动参数添加如下参数：debug_extinfo=true&debug_plugin=true，才能正常调起授权登录。添加方法请参考下图：



3.4 示例程序
开发者可参考 open-data 小程序 demo。

 

4. canvas 支持方案
4.1 作用
支持三方应用在 canvas 中安全渲染通讯录数据
支持 echarts、antv g2 等第三方图形库，在 canvas 渲染模式下，正确渲染通讯录数据
4.2 使用方式
1 . 在完成了 WWOpenData 的初始化后，调用 initCanvas 方法

if (WWOpenData.initCanvas) {
	WWOpenData.initCanvas()
}
 

2 . 调用 WWOpenData 的 prefetch 方法，将需要在图形显示的名称，进行预获取。可以参考以下代码

const result = await new Promise((resolve, reject) => {
	WWOpenData.prefetch({ items }, (err, data) => {
		if (err) {
			return reject(err)
		}
		resolve(data)
	})
})
其中，items 和 result 的格式分别是：

items: [
	{
		type: string, // userType
		id: string, // openid
		corpid: string, // corpid (非必须)
	}
]

result: [
	{
		type: string,
		id: string,
		data: string, // 重要，这里的数据需要传入到 canvas 图形库中
	}
]
3 . 到了这一步，已经完备了 canvas 展示通讯录数据的将， result 返回的 data，开发者可以理解成是 加密过的通讯录数据，接下来，开发者只需要把这些加密过的通讯录数据，当成正常的数据，放到 canvas 的接口 或者 第三方图形库的接口上，进行渲染即可。

4 . 一般情况下，为了避免页面受到 xss 攻击时，泄漏图片数据，默认情况下，渲染过通讯录信息的 canvas，是禁止使用 toDataUrl 导出图片的。如果确实有这样的需求，服务商可以在渲染 canvas 前，调用 WWOpenData.enableCanvasSharing 这个 api，调用后，渲染出来的 canvas 就能通过 toDataUrl 导出图片。与之相对，WWOpenData.disableCanvasSharing 这个 api 可以重新禁止 canvas 导出图片。

 

5. 发送应用消息支持id转译
应用在下发消息时，可以在内容中以模板参数语法包含id，企业微信在下发时会将其替换为成员名或部门名，目前支持文本/文本卡片/图文/图文（mpnews）这四种消息类型，参数使用说明具体参见“发送应用消息”，注意需要在原接口参数上添加 enable_id_trans 字段且置为1，才能开启转译.

6. 人名或部门名搜索方案
通过通讯录搜索接口，可以根据名字或拼音搜索出对应的userid或部门id。

7. 包含人名部门名的文件导出方案
先调用“异步通讯录id转译”接口提交转译任务，然后通过“获取异步任务结果”获取最终下载文件的url，注意该url仅能在有用户登录态的浏览器打开以下载文件，详情参见“通讯录ID转译”。

注意：随着外部浏览器的安全策略升级，为了更好的用户体验，推荐服务商拿到 文件 url 后，使用 ww-open-data-export-button 组件提供下载服务。
详情参见："会话展示组件" 中的 ww-open-data-export-button 组件 以及 相关初始化流程。

 

8. 通讯录用户排序方案
通过通讯录userid排序，可以根据姓名拼音升序或者降序排列。

9. 分享转发方案
目前仅支持H5的分享转发，通过 分享接口 指定 enableIdTrans置为1，开启转译。支持的ID转译模版语法在文档最末尾有说明。

 

FAQ
页面使用了 iframe，iframe 内找不到 WWOpenData
解决方法：针对应用页面使用了 iframe 的情况，可以通过 window.parent 的方式往最外层的 webview 访问 WWOpenData 对象。
agentConfig 签名一直报错
注意点：agentConfig 的签名参数 和 wx.config 是不一样的，参考文档
第三方浏览器，其他浏览器工作正常，safari 工作不正常
解答：由于 Safari 浏览器对 cors 策略的处理和其他浏览器不一样，在第三方浏览器上，请务必按照文档完成 wx.agentConfig 的处理
关于 jWeixin sdk 版本的处理，请注意：在企业微信上，必须引入的是 1.2.0 版本的 jWeixin sdk，在微信 或者 其他第三方浏览器，可以引入其他版本的 jWeixin sdk
单页面应用，在 windows 客户端可以渲染，但是在 iOS 客户端不能渲染
解答：由于目前 windows 客户端 和 iOS 存在差异，为了保证各个端运行正确，请严格保证如下标准：如果单页面应用使用了 browser history 作为路由，请保证每次 url 变更后，都正常完成 wx.config 和 wx.agentConfig 初始化。
页面在浏览器，在 iOS，Mac，Android 上面的企业微信都表现正常，但是在 windows 企业微信下，会偶发不能渲染通讯录控件内容
解答：由于 企业微信的 windows 客户端浏览器内核不支持 customElements，每次更新了 open-data 元素后，需要用 bind 或者 bindAll 接口对目标元素进行一次更新，这样才能保证 open-data 元素实时渲染正确的数据。遇到上面的情况，请检查一下页面代码，看看有没有可能出现时序问题：先执行了 bind，然后才渲染出对应的 open-data 元素
如何自定义显示内容，比如表单需要显示“提交人+提交日期+业务类型”？
将需要替换通讯录名称的文本替换为ww-open-data标签引用，其它保留不变。比如，
<ww-open-data type="userName" openid="{{openid}}"></ww-open-data>+提交日期+业务类型

通讯录展示组件，是否可以一次性显示多个名称？
组件的每个ww-open-data标签引用对应到一个通讯录名称，显示多个名称，则引用多个ww-open-data。比如，显示完整的部门路径，只需要将路径的部门id依次引用即可。
第三方管理端，如何实现成员搜索？
调用接口：通讯录搜索，传入搜索的关键词，获取搜索结果的userid/departmentid。
再调用通讯录展示组件，显示出搜索的成员名称/部门名称。
如何实现搜索后的结果按拼音排序？
调用接口：通讯录userid排序，支持指定的用户列表按拼音升序/降序，返回的结果为排序后的列表。
第三方管理端，导入业务数据文件（如打卡记录），包括了通讯录名称，如何识别？
如果业务数据文件中记录中有唯一字段标识，则可以直接对应关联；
如果通过通讯录名称关联用户，调用 通讯录搜索 接口，获取搜索结果的userid/departmentid，对应关联到用户
第三方管理端，支持导出业务数据文件（如打卡列表），需要包含通讯录名称，如何实现？
解决方案参考：通讯录ID转译。以模板参数填入数据文件中，并上传至企业微信后台，数据文件中的模板参数就会替换为通讯录名称，并获取到一个文件访问地址。
该文件访问地址，需要用户通过企业微信登录至第三方管理端，才可下载。
页面请求数据报错403

通常是由于用户未登录至第三方业务页面导致，可以访问 open-data 调试页面 查看登录信息。
注意，在单点登录的场景（包括有扫码登录，应用安装完成跳转，以及从企业微信Web管理端业务跳转），在指定的redirect_uri的域名，才会有登录用户身份。
比如，扫码登录后跳转到域名A，在域名B下使用组件，是会报错403的。
已删除的成员或部门，是否能通过通讯录组件展示名字
可以。对于同一个userid或部门ID，企业微信仅展示最后一个删除的成员或部门的名字；删除之后再重新添加相同的userid或部门ID，则只展示新成员或新部门的名字。（注：部门名仅支持展示2021年10月1号之后删除的部门）