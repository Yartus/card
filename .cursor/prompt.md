# Cursor Prompt — WeCard 名片平台（中文版）

你是资深 SaaS 架构师与全栈工程师，目标是基于当前已实现的 WeCard 前端组件系统（`WecardOptimized.vue`）继续开发和扩展，为企业级多租户 SaaS：**WeCard 名片平台** 提供后端、租户管理、企业微信（WeCom）对接、推送卡片、素材库、模板化模块与设计系统支持。严格按下列要求开发，所有功能“先 stub 再完善”，优先使用官方 SDK，开发阶段以本地裸跑为主，最后做 Docker 化适配。

---

## 一、总体目标（功能清单）
1. SaaS 平台管理：小程序平台 + 租户管理后台（平台运营端）。
2. 企业扫码接入：服务商二维码安装模式 → 企业管理员扫码授权 → 系统创建 tenant（保存 corpId/permanent_code 等凭据）。
3. 租户后台：租户管理员能基于已实现的组件系统（WecardOptimized）配置自己的名片页面（模块布局/模块名称/模块顺序/模板变量）。
4. 成员同步：按租户自动同步企业微信成员字段，映射到 `cardData.basic_info` 与 `contact_info` 等标准字段。
5. 推送能力：租户可以从后台选择名片或素材库条目，编辑推送卡片（标题/摘要/封面）并推送到企业微信外部联系人或群。
6. 素材库：租户可上传图文/视频素材（免费租户限制 3 条 / 付费 10 条 / 高级不限），素材可在推送时被选用。
7. 多租户与套餐：支持 free / paid / pro 套餐权限限制（logo/视频/图片数量/成员上限等），用 `check_plan` 统一校验。
8. 设计系统兼容：前端风格严格兼容当前 `WecardOptimized.vue` 的视觉与交互规范（深色 Cyber / 或白底轻科幻模式的配置化支持）。
9. 可观测性：名片访问/推送/素材使用等行为需写入 `card_log` 供统计分析（租户级与平台级）。
10. 可访问性与性能：支持 `prefers-reduced-motion`、动画档位（reduced|default|rich）、只用 transform/opacity、移动端自动降级。

---

## 二、工程与架构约束
- **后端**：Flask + SQLAlchemy，RESTful API，所有业务表包含 `tenant_id`；提供 Celery/Redis 用于异步任务。
- **数据库**：MySQL，提供 Alembic 迁移脚本。
- **文件存储**：S3 协议（MinIO/COS/OSS）。
- **企业微信对接**：优先使用官方 SDK（WeCom SDK / 企业微信服务商 SDK）。
- **开发流程**：先实现路由 stub（能启动、返回 JSON），再逐步填充逻辑。
- **部署策略**：开发以本地裸跑优先，依赖服务（MySQL/Redis/MinIO）用 docker-compose；后续再 Docker 化。
- **安全合规**：多租户隔离，符合数据驻留要求。

---

## 三、前端与设计系统约束
- **主题**：支持 `dark-cyber`（深色科幻）与 `light-sci`（白底轻科幻）两套风格。
- **全局变量**：提供 CSS 变量（`--primary-color`、`--bg-primary` 等），供组件读取。
- **字体**：现代无衬线（Inter / 思源黑体 / HarmonyOS Sans / SF Pro），字号层级清晰。
- **动效**：只用 transform/opacity；支持 prefers-reduced-motion；支持 `theme.motionDensity`（reduced|default|rich）。
- **组件布局**：
  - 每个模块有 `layout` 类型（图文左右 / 多图滑动 / 卡片栅格 / 时间线 / Logo 滚动）。
  - 模块的名称、内容、顺序由租户后台配置。
  - 默认 4-5 个模板，支持扩展。
  - 卡片容器统一圆角矩形、浅描边、轻阴影，hover 动效 200ms。
- **推送卡片预览**：
  - 包含 `title`、`summary`、`cover_image`。
  - 允许编辑与预览；无封面时自动生成默认预览。

---

## 四、后端数据模型
- `tenants`：id, corp_id, name, plan, permanent_code, settings(JSON), created_at
- `members`：id, tenant_id, userid, name, mobile, email, position, avatar_url, department, created_at
- `card_templates`：id, tenant_id, name, template_json, is_default
- `modules`：id, tenant_id, name, layout_type, order, config_json
- `file_assets`：id, tenant_id, uploader_id, file_name, file_url, file_type, size, md5
- `materials`：id, tenant_id, title, summary, cover_url, content_json, type, created_at
- `card_logs`：id, tenant_id, member_id, event(push/view/click), meta, created_at

---

## 五、关键 API
- `GET /healthz`
- `GET /install?tenant_name=`
- `POST /auth/callback`
- `POST /tasks/sync_members`
- `GET /card/{tenant_id}/{member_id}`
- `POST /files/upload`
- `POST /wecom/callback`
- `POST /tasks/push_card`
- `GET /admin/tenant/{id}/stats`

---

## 六、企业微信字段映射规则
- 按照 `cardData` 规范映射（basic_info / contact_info / modules）。
- 支持 department、company_logo、office_address、wechat_qr。
- 扩展字段通过 `extattr`。

---

## 七、套餐与权限
- free：不可修改 logo、不可上传视频、图片 ≤5 张 / 总大小 ≤5MB、必须带广告。
- paid：支持 logo、视频 ≤20MB、图片不限、成员 ≤20。
- pro：无限制。
- 超限返回 `403` + JSON 错误。

---

## 八、开发与交付要求
1. 所有功能先 stub 再实现，必须有 pytest 单元测试。
2. 优先用官方 SDK。
3. 所有 API 强制租户上下文。
4. 提供 Alembic 迁移 + docker-compose。
5. README 说明本地开发流程与 WeCom 测试流程。
6. 前端样式库支持 `dark-cyber` 与 `light-sci`。
7. 推送卡片必须支持编辑与预览。

---

## 九、交付物
- 可启动后端与依赖容器。
- 完成授权安装 stub 并创建 tenant。
- 成员同步逻辑可跑。
- 文件上传接口可跑。
- 名片渲染接口与前端组件兼容。
- 推送卡片接口能发消息并记录日志。
- 基础单元测试 + CI。
