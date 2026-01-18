# 成员OAuth授权说明

## 问题背景

企业微信第三方应用有两种获取成员信息的方式：

| 方式 | 能获取的信息 | 限制 |
|------|------------|------|
| **通讯录API** | ❌ 只能获取加密的open_userid | 无法获取真实姓名、手机号 |
| **OAuth授权** | ✅ 可获取真实姓名、手机号、头像等 | 需要员工主动授权 |

## 核心结论

**必须通过OAuth授权才能获取员工的真实姓名和手机号！**

## OAuth授权流程

### 员工操作步骤：

1. **打开名片页面**
   - 在企业微信工作台中点击应用
   - 系统自动跳转到员工名片页面

2. **触发授权提示**
   - 如果系统检测到信息不完整（未授权）
   - 会弹出授权确认窗口

3. **点击授权**
   - 点击"确定"按钮
   - 跳转到企业微信OAuth授权页面

4. **完成授权**
   - 企业微信会询问是否允许获取信息
   - 点击"同意"
   - 系统自动获取姓名、手机号、头像等信息

### 管理员查看：

授权完成后，管理员可在"成员管理"页面看到：
- ✅ 真实姓名
- ✅ 手机号码
- ✅ 头像
- ✅ OAuth状态标记为"已授权"

## 技术说明

### OAuth获取的信息（真实数据）

```json
{
  "userid": "womKtScgAAEkyZS7yXhQkhLqeCvf7ehQ",  // 加密ID
  "open_userid": "womKtScgAAEkyZS7yXhQkhLqeCvf7ehQ",
  "name": "彭洋",           // ✅ 真实姓名
  "mobile": "18658198258",  // ✅ 真实手机号
  "avatar": "https://...",  // ✅ 真实头像
  "position": "产品经理",   // ✅ 职位
  "email": "peng@example.com"
}
```

### 通讯录API获取的信息（加密数据）

```json
{
  "userid": "womKtScgAAEkyZS7yXhQkhLqeCvf7ehQ",  // 加密ID
  "name": "womKtScgAAEkyZS7yXhQkhLqeCvf7ehQ",    // ❌ 仍然是加密ID
  "mobile": "",             // ❌ 空
  "avatar": "默认头像"      // ❌ 通用头像
}
```

## 重要注意事项

### ⚠️ 不要用通讯录同步覆盖OAuth数据

- 通讯录API返回的是加密格式
- OAuth授权返回的是真实信息
- **OAuth数据优先级最高**
- 已经移除了错误的同步脚本

### ✅ 正确的数据优先级

```
1. OAuth授权数据（最高优先级）
   ↓ 如果没有
2. 管理员手动编辑
   ↓ 如果没有
3. 系统默认值
```

## 当前状态

- ✅ 已删除错误的通讯录同步脚本
- ✅ 已将所有成员标记为"未授权"
- ✅ 员工重新访问名片时会触发OAuth授权
- ✅ OAuth回调逻辑正确，会保存真实信息

## 后续操作

### 管理员需要做的：

**通知所有员工：**
> "请在企业微信工作台中打开【浙里有邮数字名片】应用，
> 系统会请求授权，点击'同意'即可。
> 授权后您的真实姓名和联系方式才能正确显示。"

### 验证授权成功：

管理员在"成员管理"页面查看：
- ✅ 姓名列显示真实姓名（不是长串字符）
- ✅ 手机号列显示真实手机号
- ✅ OAuth状态显示"已授权"

## 技术实现

### 检测逻辑 (`/api/v1/wecom/card/my`)

```python
# 检测是否需要OAuth授权
if not member.oauth_authorized or not member.name or member.name == member.userid:
    return {
        'need_oauth': True,
        'oauth_url': 'https://...'
    }
```

### 回调逻辑 (`/api/v1/wecom/oauth/callback`)

```python
# 获取OAuth数据
user_info = fetch_oauth_user_info(code, tenant)

# 保存真实信息
member.name = user_info['name']          # 真实姓名
member.mobile = user_info['mobile']      # 真实手机号
member.avatar_url = user_info['avatar']  # 真实头像
member.oauth_authorized = True           # 标记已授权
```

---

**更新时间**: 2025-11-16
**相关文档**: `/opt/qwcard/docs/1、系统认识cc4.5.md`

