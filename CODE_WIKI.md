# 渊博家教平台 - Code Wiki 文档

## 1. 项目概述

### 1.1 项目定位
本项目是一个**家教服务平台**，旨在连接家长（需求方）和教师（服务方），实现家教需求发布、教师抢单、订单管理和评价反馈等核心功能。

### 1.2 技术栈

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | Flask | 3.0.0 | Web应用框架 |
| ORM | Flask-SQLAlchemy | 3.1.1 | 数据库映射 |
| 认证 | Flask-Login | 0.6.3 | 用户会话管理 |
| 表单 | Flask-WTF | 1.2.1 | 表单验证 |
| 管理后台 | Flask-Admin | 1.6.1 | 自动生成管理界面 |
| 数据库 | SQLite | - | 轻量级嵌入式数据库 |
| 密码 | Werkzeug | 3.0.1 | 密码哈希 |

### 1.3 项目结构

```
tutor_platform/
├── app/                              # 应用核心目录
│   ├── __init__.py                   # 应用工厂函数
│   ├── auth.py                       # 用户认证模块
│   ├── admin.py                      # 后台管理路由
│   ├── admin_views.py                # Flask-Admin 视图配置
│   ├── models.py                     # 数据库模型定义
│   ├── routes.py                     # 前端业务路由
│   ├── forms.py                      # 表单定义
│   ├── utils.py                      # 工具函数
│   ├── static/                       # 静态资源
│   └── templates/                    # HTML模板
├── config.py                         # 配置文件
├── run.py                            # 启动入口
├── requirements.txt                  # 依赖清单
└── tutor.db                         # SQLite数据库文件
```

---

## 2. 整体架构

### 2.1 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   家长端      │  │   教师端      │  │     管理后台         │  │
│  │ (发布需求)    │  │ (抢单/教学)   │  │ (审核/管理)          │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼──────────────────────┼─────────────┘
          │                 │                      │
┌─────────▼─────────────────▼──────────────────────▼─────────────┐
│                        路由层 (Routes)                          │
│  auth.py          routes.py          admin.py                  │
│  ───────          ──────────          ────────                  │
│  登录/注册        业务逻辑           管理功能                    │
└─────────────────────────┬──────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│                        业务层 (Business)                         │
│  models.py         forms.py         utils.py                    │
│  ────────          ────────         ───────                    │
│  数据模型           表单验证          工具函数                   │
└─────────────────────────┬──────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│                        数据层 (Database)                        │
│                    SQLite (tutor.db)                           │
│  users | tutor_profiles | job_orders | applications | reviews  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心业务流程

#### 流程一：教师入驻流程
```
教师注册 → 提交简历 → 管理员审核 → 审核通过 → 可登录抢单
```

#### 流程二：家教需求流程
```
家长发布需求 → 教师抢单 → 家长选择 → 订单完成 → 家长评价
```

---

## 3. 模块职责说明

### 3.1 应用工厂模块 (`app/__init__.py`)

**职责**: 负责Flask应用的初始化、配置加载、扩展注册和蓝图注册。

**核心函数**:
- `create_app(config_class=Config)`: 创建并配置Flask应用实例

**关键配置**:
- 数据库连接初始化 (`db.init_app`)
- 用户登录管理器 (`login_manager.init_app`)
- 蓝图注册（auth、main、admin）
- Flask-Admin 初始化
- 数据库表自动创建

### 3.2 数据模型模块 (`app/models.py`)

**职责**: 定义数据库表结构和业务实体关系。

**实体模型**:

| 模型 | 表名 | 说明 |
|------|------|------|
| User | users | 用户账号表（统一账号，角色区分） |
| TutorProfile | tutor_profiles | 教师简历表（与User一对一） |
| JobOrder | job_orders | 家教需求订单表 |
| Application | applications | 抢单线索表 |
| Review | reviews | 评价表 |

**关系设计**:

```
User (1) ──── (*) JobOrder    (家长发布需求)
User (1) ──── (*) Application (教师抢单)
User (1) ──── (1) TutorProfile (教师简历)
TutorProfile (1) ──── (*) Application (教师抢单记录)
TutorProfile (1) ──── (*) Review (教师评价)
JobOrder (1) ──── (*) Application (需求抢单)
```

### 3.3 用户认证模块 (`app/auth.py`)

**职责**: 处理用户登录、注册和退出功能。

**路由列表**:

| 路由 | 方法 | 功能 |
|------|------|------|
| `/auth/login` | GET/POST | 用户登录 |
| `/auth/register/tutor` | GET/POST | 教师注册 |
| `/auth/register/parent` | GET/POST | 家长注册 |
| `/auth/logout` | GET | 退出登录 |

**认证流程**:
1. 验证用户名密码
2. 检查账号状态（是否禁用）
3. 教师需审核通过才能登录
4. 使用Flask-Login管理会话

### 3.4 前端业务模块 (`app/routes.py`)

**职责**: 处理用户端（家长、教师）的业务逻辑。

**路由分类**:

| 类别 | 路由 | 功能 | 权限 |
|------|------|------|------|
| 首页 | `/` | 首页展示 | 公开 |
| 师资 | `/teachers` | 教师列表 | 公开 |
| 师资 | `/teacher/<id>` | 教师详情 | 公开 |
| 需求 | `/orders` | 需求列表 | 公开 |
| 需求 | `/order/<id>` | 需求详情 | 公开 |
| 发单 | `/order/new` | 发布需求 | 家长 |
| 抢单 | `/order/<id>/apply` | 申请抢单 | 教师 |
| 选择 | `/application/<id>/accept` | 选择教师 | 家长 |
| 订单 | `/my-orders` | 我的订单 | 家长 |
| 抢单 | `/my-applications` | 我的抢单 | 教师 |
| 个人 | `/profile` | 个人中心 | 登录用户 |
| 评价 | `/review/<id>` | 评价教师 | 家长 |

### 3.5 后台管理模块 (`app/admin.py`)

**职责**: 提供管理员对平台的管理功能。

**路由列表**:

| 路由 | 功能 |
|------|------|
| `/manage/` | 仪表盘 |
| `/manage/users` | 用户列表 |
| `/manage/users/<id>/toggle` | 启用/禁用用户 |
| `/manage/users/<id>/delete` | 删除用户 |
| `/manage/teachers` | 教师列表 |
| `/manage/teacher/<id>` | 教师详情 |
| `/manage/teacher/<id>/approve` | 审核通过 |
| `/manage/teacher/<id>/reject` | 拒绝审核 |
| `/manage/orders` | 需求列表 |
| `/manage/order/<id>` | 需求详情 |
| `/manage/applications` | 抢单列表 |
| `/manage/reviews` | 评价列表 |

**权限控制**:
- 使用 `@admin_required` 装饰器限制访问
- 管理员账号不可删除或禁用

### 3.6 Flask-Admin 模块 (`app/admin_views.py`)

**职责**: 提供自动生成的管理后台界面。

**视图配置**:

| 视图类 | 管理对象 | 功能 |
|--------|----------|------|
| UserAdmin | User | 用户管理 |
| TutorProfileAdmin | TutorProfile | 教师审核（支持行内编辑） |
| JobOrderAdmin | JobOrder | 需求管理 |
| ApplicationAdmin | Application | 抢单管理 |
| ReviewAdmin | Review | 评价管理 |

**安全特性**:
- 自定义 `SecureModelView` 基类
- 自动重定向未授权用户到登录页

### 3.7 表单模块 (`app/forms.py`)

**职责**: 定义表单验证规则。

**表单列表**:

| 表单类 | 用途 | 关键字段 |
|--------|------|----------|
| LoginForm | 登录 | username, password |
| TutorRegisterForm | 教师注册 | 含简历信息 |
| ParentRegisterForm | 家长注册 | username, email, password |
| JobOrderForm | 发布需求 | subject, grade, budget, location |
| ApplicationForm | 抢单申请 | message, proposed_rate |
| ReviewForm | 评价 | rating, content |
| ProfileForm | 个人信息编辑 | 教师简历字段 |

### 3.8 工具模块 (`app/utils.py`)

**职责**: 提供通用工具函数。

**函数列表**:

| 函数 | 功能 |
|------|------|
| `init_admin_user()` | 初始化管理员账号（首次运行自动创建） |

---

## 4. 关键类与函数详解

### 4.1 User 类

**位置**: `app/models.py`

**核心属性**:

| 属性 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String(80) | 用户名（唯一） |
| email | String(120) | 邮箱（唯一） |
| password_hash | String(255) | 密码哈希 |
| role | String(20) | 角色：admin/tutor/parent |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |

**核心方法**:

| 方法 | 说明 |
|------|------|
| `set_password(password)` | 设置密码（自动哈希） |
| `check_password(password)` | 验证密码 |
| `is_tutor()` | 判断是否教师 |
| `is_parent()` | 判断是否家长 |
| `is_admin()` | 判断是否管理员 |

### 4.2 TutorProfile 类

**位置**: `app/models.py`

**核心属性**:

| 属性 | 类型 | 说明 |
|------|------|------|
| user_id | Integer | 关联用户ID |
| real_name | String(50) | 真实姓名 |
| phone | String(20) | 手机号 |
| id_card | String(18) | 身份证号 |
| avatar | String(200) | 头像路径 |
| bio | Text | 个人简介 |
| education | String(100) | 学历 |
| experience | Integer | 教龄（年） |
| subjects | String(200) | 擅长科目（逗号分隔） |
| hourly_rate | Integer | 时薪 |
| location | String(100) | 所在地区 |
| status | String(20) | 状态：pending/approved/rejected |

**核心方法**:

| 方法 | 说明 |
|------|------|
| `get_subjects_list()` | 返回科目列表（字符串转列表） |
| `avg_rating()` | 计算平均评分 |

### 4.3 JobOrder 类

**位置**: `app/models.py`

**核心属性**:

| 属性 | 类型 | 说明 |
|------|------|------|
| parent_id | Integer | 发布家长ID |
| subject | String(50) | 科目 |
| grade | String(50) | 年级 |
| description | Text | 需求描述 |
| location | String(100) | 上课地点 |
| budget | Integer | 预算（元/小时） |
| schedule | String(200) | 时间安排 |
| duration | Integer | 每次课时（小时） |
| contact_phone | String(20) | 家长联系方式 |
| status | String(20) | 状态：open/filled |

### 4.4 Application 类

**位置**: `app/models.py`

**核心属性**:

| 属性 | 类型 | 说明 |
|------|------|------|
| job_order_id | Integer | 关联需求ID |
| tutor_id | Integer | 关联教师用户ID |
| tutor_profile_id | Integer | 关联教师简历ID |
| message | Text | 推荐留言 |
| proposed_rate | Integer | 报价（元/小时） |
| status | String(20) | 状态：pending/accepted/rejected |
| admin_note | Text | 管理员跟进备注 |

**约束**: 同一教师对同一需求只能抢单一次（唯一约束 `uq_job_tutor`）

### 4.5 Review 类

**位置**: `app/models.py`

**核心属性**:

| 属性 | 类型 | 说明 |
|------|------|------|
| tutor_profile_id | Integer | 被评价教师 |
| student_id | Integer | 评价家长 |
| rating | Integer | 评分（1-5星） |
| content | Text | 评价内容 |

---

## 5. 依赖关系

### 5.1 依赖清单

```txt
Flask==3.0.0              # Web框架核心
Flask-SQLAlchemy==3.1.1   # 数据库ORM
Flask-Login==0.6.3        # 用户认证会话
Flask-WTF==1.2.1          # 表单处理
Flask-Admin==1.6.1        # 管理后台
WTForms==3.1.1            # 表单验证
Werkzeug==3.0.1           # 密码哈希
email-validator==2.1.0    # 邮箱验证
Pillow==10.1.0            # 图片处理
```

### 5.2 模块依赖关系

```
run.py
  └── app/__init__.py
        ├── config.py
        ├── app/models.py
        │     └── app/__init__.py (db)
        ├── app/auth.py
        │     ├── app/models.py
        │     └── app/forms.py
        ├── app/routes.py
        │     ├── app/models.py
        │     └── app/forms.py
        ├── app/admin.py
        │     └── app/models.py
        └── app/admin_views.py
              └── app/models.py
```

---

## 6. 配置说明

### 6.1 配置文件 (`config.py`)

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| SECRET_KEY | dev-secret-key-change-in-production | 会话密钥 |
| SQLALCHEMY_DATABASE_URI | sqlite:///tutor.db | 数据库连接 |
| SQLALCHEMY_TRACK_MODIFICATIONS | False | 禁用修改追踪 |
| UPLOAD_FOLDER | app/static/uploads | 上传目录 |
| MAX_CONTENT_LENGTH | 16MB | 最大上传大小 |
| POSTS_PER_PAGE | 10 | 默认分页大小 |
| ADMIN_USERNAME | admin | 管理员用户名 |
| ADMIN_PASSWORD | admin123 | 管理员密码 |
| ADMIN_EMAIL | admin@tutor.com | 管理员邮箱 |

### 6.2 环境变量支持

```bash
# 生产环境建议通过环境变量配置
export SECRET_KEY=your-secret-key
export DATABASE_URL=sqlite:///tutor.db
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=your-admin-password
```

---

## 7. 运行方式

### 7.1 开发环境运行

```bash
# 进入项目目录
cd tutor_platform

# 安装依赖
pip install -r requirements.txt

# 运行应用
python run.py

# 访问地址
# 前端首页: http://localhost:5000
# 管理后台: http://localhost:5000/manage
# Flask-Admin: http://localhost:5000/admin
```

### 7.2 首次运行

首次运行时系统会自动：
1. 创建SQLite数据库文件 `tutor.db`
2. 创建所有数据表
3. 创建管理员账号（admin/admin123）

### 7.3 管理员登录

```
用户名: admin
密码: admin123
```

---

## 8. 数据库表结构

### 8.1 users 表

| 字段 | 类型 | 约束 |
|------|------|------|
| id | INTEGER | PRIMARY KEY |
| username | VARCHAR(80) | UNIQUE, NOT NULL |
| email | VARCHAR(120) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| role | VARCHAR(20) | NOT NULL |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### 8.2 tutor_profiles 表

| 字段 | 类型 | 约束 |
|------|------|------|
| id | INTEGER | PRIMARY KEY |
| user_id | INTEGER | FOREIGN KEY, UNIQUE, NOT NULL |
| real_name | VARCHAR(50) | NOT NULL |
| phone | VARCHAR(20) | - |
| id_card | VARCHAR(18) | - |
| avatar | VARCHAR(200) | - |
| bio | TEXT | - |
| education | VARCHAR(100) | - |
| experience | INTEGER | DEFAULT 0 |
| subjects | VARCHAR(200) | - |
| hourly_rate | INTEGER | DEFAULT 0 |
| location | VARCHAR(100) | - |
| status | VARCHAR(20) | DEFAULT 'pending' |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### 8.3 job_orders 表

| 字段 | 类型 | 约束 |
|------|------|------|
| id | INTEGER | PRIMARY KEY |
| parent_id | INTEGER | FOREIGN KEY, NOT NULL |
| subject | VARCHAR(50) | NOT NULL |
| grade | VARCHAR(50) | NOT NULL |
| description | TEXT | NOT NULL |
| location | VARCHAR(100) | NOT NULL |
| budget | INTEGER | NOT NULL |
| schedule | VARCHAR(200) | NOT NULL |
| duration | INTEGER | DEFAULT 2 |
| contact_phone | VARCHAR(20) | - |
| status | VARCHAR(20) | DEFAULT 'open' |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### 8.4 applications 表

| 字段 | 类型 | 约束 |
|------|------|------|
| id | INTEGER | PRIMARY KEY |
| job_order_id | INTEGER | FOREIGN KEY, NOT NULL |
| tutor_id | INTEGER | FOREIGN KEY, NOT NULL |
| tutor_profile_id | INTEGER | FOREIGN KEY, NOT NULL |
| message | TEXT | NOT NULL |
| proposed_rate | INTEGER | - |
| status | VARCHAR(20) | DEFAULT 'pending' |
| admin_note | TEXT | - |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### 8.5 reviews 表

| 字段 | 类型 | 约束 |
|------|------|------|
| id | INTEGER | PRIMARY KEY |
| tutor_profile_id | INTEGER | FOREIGN KEY, NOT NULL |
| student_id | INTEGER | FOREIGN KEY, NOT NULL |
| rating | INTEGER | NOT NULL |
| content | TEXT | NOT NULL |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

---

## 9. 安全注意事项

1. **密码安全**: 使用 Werkzeug 进行密码哈希存储，禁止明文存储
2. **权限控制**: 管理员路由使用 `@admin_required` 装饰器保护
3. **敏感信息**: 身份证号和手机号在管理后台显示时进行脱敏处理（中间用星号隐藏）
4. **SQL注入**: 使用 SQLAlchemy ORM，避免原生SQL拼接
5. **表单验证**: 所有用户输入通过 WTForms 进行验证
6. **会话安全**: 使用 Flask-Login 管理用户会话，自动处理 session

---

## 10. 扩展建议

1. **图片上传**: 支持教师头像上传功能
2. **消息通知**: 实现站内消息或邮件通知
3. **支付功能**: 集成在线支付接口
4. **课程管理**: 添加课程预约和时间管理
5. **数据统计**: 增加数据可视化报表
6. **移动端适配**: 优化移动端访问体验
7. **邮件服务**: 配置SMTP发送注册通知和审核结果