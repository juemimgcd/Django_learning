# Django 7 天学习路线（后端主线版）

基于 Django 6.0 官方中文文档整理：

- 文档首页：https://docs.djangoproject.com/zh-hans/6.0/
- 适合对象：已有完整 Python 基础、HTTP 基础，并有 FastAPI 后端项目经验
- 学习目标：7 天内把 Django 的后端核心能力跑通，并完成一个小型笔记系统后端

## 这份路线的定位

这份路线是偏后端的，不是传统的“Django 全栈页面开发路线”。

也就是说，这 7 天里你会优先学习这些内容：

- `project` 和 `app`
- URL 分发
- Django 视图函数
- ORM、模型、迁移
- Admin 后台
- JSON 接口
- 认证、权限、Session
- 中间件
- 测试
- 安全、部署、性能优化

而下面这些内容，这条路线只要求你“知道有、能看懂基础用法”，不作为主线投入：

- Django 模板
- 服务端渲染页面
- 表单页面开发
- CSS、页面样式

## 学习原则

- 不按 Web 初学者节奏学习，而是按“后端工程师理解 Django”的方式学习
- 不把 Django 当成 FastAPI 的替代品，而是理解它自己的设计哲学
- 优先掌握 Django 原生能力，再考虑 Django REST Framework
- 用一个小项目贯穿 7 天，避免每天换 demo
- 每天都要写一点代码，不只停留在读文档

## 贯穿 7 天的小项目

项目名称：`StudyNotes`

项目定位：一个学习笔记系统的后端服务

核心功能：

- 用户登录、登出
- 当前用户信息查询
- 笔记 CRUD JSON 接口
- 标签和评论的基础关联查询
- 草稿与发布状态管理
- 基于作者身份的访问控制
- Django Admin 后台管理
- 查询过滤、搜索、分页基础
- 中间件日志
- 自动化测试
- 部署检查与查询优化

## 每天固定学习时间

建议每天投入 `4 小时`，连续 7 天，总计约 `28 小时`。

| 时间段 | 时长 | 内容 |
| --- | --- | --- |
| 文档阅读 | 60 分钟 | 阅读当天对应的 Django 官方文档 |
| 跟敲实验 | 90 分钟 | 跑通当天知识点的最小示例 |
| 项目开发 | 90 分钟 | 把当天内容落到 `StudyNotes` 项目 |
| 复盘总结 | 30 分钟 | 记录命令、概念、踩坑和与 FastAPI 的差异 |

## Day 1：项目骨架、配置与最小请求处理

- 学习时长：4 小时
- 学习目标：理解 Django 项目结构、配置、URL 分发和最简单的视图函数
- 官方文档：
  - 教程第 1 部分：https://docs.djangoproject.com/zh-hans/6.0/intro/tutorial01/
  - Django 配置：https://docs.djangoproject.com/zh-hans/6.0/topics/settings/
  - URL 调度器：https://docs.djangoproject.com/zh-hans/6.0/topics/http/urls/
  - 编写视图：https://docs.djangoproject.com/zh-hans/6.0/topics/http/views/

### 时间安排

- 09:00-10:00：阅读 `startproject`、`startapp`、`runserver`
- 10:00-11:30：创建项目 `studynotes` 和 app `notes`
- 14:00-15:30：编写 `health` 和 `ping` 接口
- 15:30-16:00：总结 `project`、`app`、`manage.py` 的职责

### 项目任务

- 创建 Django 项目和 `notes` app
- 跑通开发服务器
- 实现以下路由：
  - `/`
  - `/health/`
  - `/api/ping/`

### 当日产出

- 项目可以启动
- 能清楚解释 `settings.py`、`urls.py`、`views.py` 的作用
- 理解 Django 如何从 URL 找到视图并返回响应

### 你今天要理解的核心差异

- FastAPI 通常更快进入接口定义
- Django 更强调“项目约定 + 全局配置 + 内建能力”

## Day 2：ORM、迁移与 Admin 后台

- 学习时长：4 小时
- 学习目标：掌握 Django 模型、QuerySet、迁移机制和 Admin
- 官方文档：
  - 教程第 2 部分：https://docs.djangoproject.com/zh-hans/6.0/intro/tutorial02/
  - 模型：https://docs.djangoproject.com/zh-hans/6.0/topics/db/models/
  - 执行查询：https://docs.djangoproject.com/zh-hans/6.0/topics/db/queries/
  - 迁移：https://docs.djangoproject.com/zh-hans/6.0/topics/migrations/
  - Admin site：https://docs.djangoproject.com/zh-hans/6.0/ref/contrib/admin/

### 时间安排

- 09:00-10:00：阅读模型、查询和迁移相关文档
- 10:00-11:30：设计 `Tag`、`Note`、`Comment` 三个模型
- 14:00-15:00：执行迁移并在 shell 中练习查询
- 15:00-16:00：注册 Admin，创建超级用户并录入测试数据

### 项目任务

- 创建以下模型：
  - `Tag`
  - `Note`
  - `Comment`
- 给 `Note` 增加字段：
  - `author`
  - `title`
  - `content`
  - `status`
  - `tags`
  - `created_at`
  - `updated_at`
- 建立模型关联
- 将模型注册到 Admin

### 当日产出

- 可以通过 Admin 管理笔记、标签和评论
- 能独立执行 `makemigrations`、`migrate`
- 能使用 ORM 做基础查询

### 你今天要理解的核心差异

- Django ORM 和迁移不是外挂，而是框架核心能力
- 在 Django 中，模型不只是数据库表映射，也常常是业务表达中心

## Day 3：原生 Django 写 JSON CRUD 接口

- 学习时长：4 小时
- 学习目标：使用 Django 原生视图和 `JsonResponse` 写出一组可工作的 CRUD 接口
- 官方文档：
  - 编写视图：https://docs.djangoproject.com/zh-hans/6.0/topics/http/views/
  - URL 调度器：https://docs.djangoproject.com/zh-hans/6.0/topics/http/urls/
  - 请求和响应对象：https://docs.djangoproject.com/zh-hans/6.0/ref/request-response/
  - Django 便捷函数：https://docs.djangoproject.com/zh-hans/6.0/topics/http/shortcuts/
  - 执行查询：https://docs.djangoproject.com/zh-hans/6.0/topics/db/queries/

### 时间安排

- 09:00-10:00：阅读请求响应、视图和查询文档
- 10:00-11:00：设计接口 URL 和返回 JSON 结构
- 14:00-15:30：实现笔记列表、详情、创建、更新、删除接口
- 15:30-16:00：用 PowerShell 或 Postman 调通接口

### 项目任务

- 实现以下接口：
  - `GET /api/notes/`
  - `GET /api/notes/<id>/`
  - `POST /api/notes/create/`
  - `PATCH /api/notes/<id>/update/`
  - `DELETE /api/notes/<id>/delete/`
- 手写最基础的对象序列化逻辑
- 学会从 `request.body` 读取 JSON
- 返回合理状态码：
  - `200`
  - `201`
  - `400`
  - `404`
  - `405`

### 当日产出

- 项目具备最基础的 JSON API
- 能解释 `JsonResponse` 的作用
- 能解释为什么 ORM 对象不能直接返回成 JSON

### 你今天要理解的核心差异

- FastAPI 会帮你自动做很多请求体解析和数据校验
- Django 原生接口更接近“你自己控制请求处理流程”

## Day 4：认证、权限与接口访问控制

- 学习时长：4 小时
- 学习目标：掌握 Django 内建认证系统，并把认证和权限接到接口层
- 官方文档：
  - Django 中的用户认证：https://docs.djangoproject.com/zh-hans/6.0/topics/auth/
  - 使用 Django 的验证系统：https://docs.djangoproject.com/zh-hans/6.0/topics/auth/default/
  - 会话框架：https://docs.djangoproject.com/zh-hans/6.0/topics/http/sessions/
  - 自定义认证：https://docs.djangoproject.com/zh-hans/6.0/topics/auth/customizing/

### 时间安排

- 09:00-10:00：阅读认证、Session 和权限文档
- 10:00-11:00：实现登录、登出和当前用户信息接口
- 14:00-15:00：让创建笔记使用当前登录用户，而不是手动传 `author_id`
- 15:00-16:00：限制只有作者本人可以更新和删除自己的笔记

### 项目任务

- 实现以下接口：
  - `POST /api/login/`
  - `POST /api/logout/`
  - `GET /api/me/`
- 在创建笔记时自动使用 `request.user`
- 对修改、删除接口增加登录限制
- 增加“只有作者本人可修改或删除自己笔记”的判断
- 继续完善 Admin 展示：
  - `list_display`
  - `search_fields`
  - `list_filter`

### 当日产出

- 项目具备基础的用户认证和访问控制
- 能区分 `401`、`403`、`404` 在权限语义中的差异
- 能理解 Django 的 Session 认证机制

### 你今天要理解的核心差异

- Django 的认证、权限、Session 和 Admin 是一套一起设计的系统
- FastAPI 里这套东西通常要靠更多手工组合

## Day 5：请求对象、中间件、查询参数与异步边界

- 学习时长：4 小时
- 学习目标：理解 `HttpRequest`、中间件职责，以及如何让接口支持过滤、搜索和分页基础
- 官方文档：
  - 请求和响应对象：https://docs.djangoproject.com/zh-hans/6.0/ref/request-response/
  - 中间件：https://docs.djangoproject.com/zh-hans/6.0/topics/http/middleware/
  - 异步支持：https://docs.djangoproject.com/zh-hans/6.0/topics/async/

### 时间安排

- 09:00-10:00：阅读请求响应、中间件和异步支持
- 10:00-11:00：编写一个请求日志或请求耗时中间件
- 14:00-15:00：给笔记列表接口加查询参数支持
- 15:00-16:00：实现一个简单异步视图，并理解 Django async 的边界

### 项目任务

- 编写一个请求日志中间件
- 输出请求路径、方法、耗时，最好带一个 `request_id`
- 让 `GET /api/notes/` 支持基础查询参数：
  - `status`
  - `author_id`
  - `tag_id`
  - `keyword`
- 支持最基础分页：
  - `page`
  - `page_size`
- 增加一个简单的异步接口，感受 Django 对 async 视图的支持

### 当日产出

- 能解释 `request.GET`、`request.headers`、`request.body` 的差异
- 能看懂中间件在请求链中的位置
- 能理解 Django 的异步支持“能用，但不是完全 async-first”

### 你今天要理解的核心差异

- Django 支持 async，但 ORM 和整体生态并不是完全以 async 为核心设计
- 你的 FastAPI 经验会有帮助，但不能直接套一模一样的心智模型

## Day 6：测试、安全与接口稳健性

- 学习时长：4 小时
- 学习目标：补齐 Django 后端开发中的测试意识和安全意识
- 官方文档：
  - 测试概览：https://docs.djangoproject.com/zh-hans/6.0/topics/testing/
  - 编写并运行测试：https://docs.djangoproject.com/zh-hans/6.0/topics/testing/overview/
  - 安全概览：https://docs.djangoproject.com/zh-hans/6.0/topics/security/
  - CSRF 保护：https://docs.djangoproject.com/zh-hans/6.0/ref/csrf/

### 时间安排

- 09:00-10:00：阅读测试和安全相关文档
- 10:00-11:30：为模型、接口和权限编写测试
- 14:00-15:00：补无效 JSON、无权限访问、资源不存在等失败测试
- 15:00-16:00：回头审视接口中使用 `csrf_exempt` 的地方，理解风险和适用边界

### 项目任务

- 至少编写以下测试：
  - 模型测试
  - 列表接口测试
  - 创建接口测试
  - 登录限制测试
  - 作者权限测试
  - 非法 JSON 测试
- 阅读并理解 CSRF 的作用
- 明确哪些接口在学习阶段使用了简化方案，哪些在真实项目里需要加强

### 当日产出

- 项目具备基础自动化测试
- 能解释为什么“接口能跑”不等于“接口可靠”
- 能理解 Django 默认提供了哪些安全机制

### 你今天要理解的核心差异

- Django 原生自带很多安全机制，但你必须知道什么时候在绕过它们
- 这和只关注“功能能不能通”的开发习惯不一样

## Day 7：部署、性能优化与项目收尾

- 学习时长：4 小时
- 学习目标：理解 Django 项目从本地开发走向可交付状态时需要关注的关键项
- 官方文档：
  - 部署概览：https://docs.djangoproject.com/zh-hans/6.0/howto/deployment/
  - 部署清单：https://docs.djangoproject.com/zh-hans/6.0/howto/deployment/checklist/
  - 性能和优化：https://docs.djangoproject.com/zh-hans/6.0/topics/performance/
  - 优化数据库访问：https://docs.djangoproject.com/zh-hans/6.0/topics/db/optimization/
  - 教程第 8 部分：https://docs.djangoproject.com/zh-hans/6.0/intro/tutorial08/

### 时间安排

- 09:00-10:00：阅读部署和优化文档
- 10:00-11:00：梳理开发与生产配置差异
- 14:00-15:00：优化一个存在 N+1 风险的查询
- 15:00-16:00：整理 README、接口说明和后续扩展方向

### 项目任务

- 明确以下生产配置概念：
  - `DEBUG=False`
  - `ALLOWED_HOSTS`
  - 数据库连接配置
  - 环境变量管理
- 运行部署检查：
  - `python manage.py check --deploy`
- 使用 `select_related()` 或 `prefetch_related()` 做一次查询优化
- 为项目补一份接口说明和功能说明

### 当日产出

- 得到一个结构完整、可继续扩展的 Django 小型后端项目
- 能说清楚本地开发和生产部署的关键差异
- 能解释至少一个查询优化点

### 你今天要理解的核心差异

- Django 的“写接口”只是起点
- 真正的后端项目还要考虑配置、安全、性能和交付

## 每日复盘模板

每天结束后，用 10 到 15 分钟写下以下内容：

```md
### Day X 复盘

- 今天学到的 Django 核心概念：
- 今天写出的功能：
- 遇到的问题：
- 我是如何解决的：
- 今天 Django 和 FastAPI 最大的差异：
- 明天开始前我要先复习的内容：
```

## 这 7 天你真正要建立的能力

7 天结束后，你至少应该做到这些事：

- 你能解释 Django 中 `project` 和 `app` 的区别
- 你能独立设计模型并完成迁移
- 你能用 Django 原生视图写出一组基础 JSON API
- 你能接入 Django 自带的认证、Session 和权限控制
- 你能看懂并编写基础中间件
- 你能为模型和接口写基础测试
- 你知道 Django 默认的安全能力有哪些
- 你能完成最基本的部署检查和查询优化

## 7 天结束后的验收标准

- 你拥有一个可以运行的 `StudyNotes` 后端项目
- 项目至少具备：模型、迁移、Admin、JSON API、认证权限、测试
- 你知道 Django 和 FastAPI 在请求处理、认证方式、内建能力上的主要差异
- 你知道什么时候该继续用 Django 原生能力，什么时候该引入 Django REST Framework

## 学完之后的下一步

如果这 7 天路线完成得比较顺，建议继续按下面这条顺序往下走：

1. 把 `StudyNotes` 的接口风格进一步标准化
2. 引入 Django REST Framework，学习序列化器、APIView、权限类
3. 补缓存、日志、文件上传、异步任务
4. 再回头系统阅读 Django 参考文档
5. 如果将来要前后端分离，再把 Django 当成纯后端服务使用

## 一句总结

这条路线不是为了把你培养成“会写 Django 模板页面的人”，而是为了让你在已有 FastAPI 经验的基础上，真正理解 Django 作为“自带大量基础设施的后端框架”是怎么工作的。
