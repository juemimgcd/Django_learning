# DRF 7 天学习路线（承接当前 Django 后端项目）

基于 Django REST framework 官方文档整理：

- 官方文档首页：https://www.django-rest-framework.org/
- 快速开始：https://www.django-rest-framework.org/tutorial/quickstart/
- 适合对象：已经完成当前这套 Django Core 7 天路线，已经会原生 Django JSON 接口、认证、权限、中间件、测试
- 学习目标：在现有 `StudyNotes` 项目基础上，把“手写 JSON API”升级成“更标准、更省力、更像现代 API 项目”的 DRF API

## 这份路线和前 7 天是什么关系

前 7 天你学的是 Django Core：

- 项目结构
- ORM
- 原生视图函数
- Session 认证
- 权限控制
- 中间件
- 测试和部署基础

这 7 天你要学的是 DRF：

- 用 `Serializer` 替代手写序列化
- 用 `Request` / `Response` 替代原生请求响应处理
- 用 `APIView`、`GenericAPIView`、`ViewSet` 降低样板代码
- 用 DRF 的认证、权限、过滤、分页、测试和异常处理，把接口做得更工程化

一句话说清楚：

> Django Core 负责打地基，DRF 负责把你的 API 层真正工程化。

## 学习原则

- 不推倒重来，而是在当前 `StudyNotes` 项目上平滑演进
- 学习期间建议保留现有原生 Django 接口，同时新增一套 DRF 路由做对照
- 优先理解 DRF 帮你省掉了什么，再理解它为什么这么设计
- 每天都要做一点实操，不只停留在读文档

## 项目推进方式

建议在当前项目里采用“双轨学习”方式：

- 原来的原生 Django 接口继续保留在 `/api/...`
- 新增一套 DRF 接口放在 `/drf/...`

这样做的好处是：

- 你能直观看到“原生 Django API”和“DRF API”的差异
- 出问题时不容易把前面的学习成果一起打断
- 更适合你这种已经有 FastAPI 经验、想对比框架设计的人

## 每天固定学习时间

建议仍然按 `4 小时` 来安排。

| 时间段 | 时长 | 内容 |
| --- | --- | --- |
| 文档阅读 | 60 分钟 | 阅读当天对应的 DRF 官方文档 |
| 跟敲实验 | 90 分钟 | 跑通当天核心概念 |
| 项目改造 | 90 分钟 | 把当天能力接到 `StudyNotes` 项目里 |
| 复盘总结 | 30 分钟 | 对比原生 Django API 和 DRF API 的差异 |

## Day 8：DRF 入门、`Request/Response` 与第一个 `Serializer`

- 学习目标：在当前项目中接入 DRF，理解 `Request`、`Response`、`@api_view` 和 `Serializer`
- 官方文档：
  - 快速开始：https://www.django-rest-framework.org/tutorial/quickstart/
  - 教程 1：Serialization：https://www.django-rest-framework.org/tutorial/1-serialization/
  - 教程 2：Requests and responses：https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
  - Serializer API Guide：https://www.django-rest-framework.org/api-guide/serializers/
  - Views API Guide：https://www.django-rest-framework.org/api-guide/views/

### 当天任务

- 安装并接入 `djangorestframework`
- 在 `INSTALLED_APPS` 中加入 `rest_framework`
- 新建 `notes/serializers.py`
- 写第一个响应序列化器和请求序列化器
- 新增一套 DRF 函数式接口：
  - `GET /drf/notes/`
  - `GET /drf/notes/<id>/`
  - `POST /drf/notes/`
- 理解 `request.data` 和你之前手写 `parse_json_body` 的区别

### 你今天要理解的核心差异

- 原生 Django API：你自己解析请求体、自己转 JSON
- DRF：框架帮你标准化请求解析、校验和响应输出

## Day 9：`ModelSerializer`、校验流程与 `APIView`

- 学习目标：掌握 `Serializer` 和 `ModelSerializer` 的分工，并把函数式 DRF 视图升级成 `APIView`
- 官方文档：
  - 教程 3：Class-based Views：https://www.django-rest-framework.org/tutorial/3-class-based-views/
  - APIView API Guide：https://www.django-rest-framework.org/api-guide/views/
  - Serializers API Guide：https://www.django-rest-framework.org/api-guide/serializers/
  - Validators API Guide：https://www.django-rest-framework.org/api-guide/validators/

### 当天任务

- 为 `Note`、`Tag`、`Comment` 设计读写分离的序列化器
- 用 `APIView` 改写：
  - 列表/创建接口
  - 详情/更新/删除接口
- 理解：
  - `serializer.is_valid()`
  - `serializer.validated_data`
  - `serializer.errors`
  - `serializer.save()`

### 你今天要理解的核心差异

- FastAPI 用 Pydantic 直接包请求和响应
- DRF 用 `Serializer` 统一承担“校验 + 转换 + 输出”的职责

## Day 10：泛型视图、`mixins` 与真正减少样板代码

- 学习目标：掌握 `GenericAPIView`、`mixins` 和通用类视图，把 DRF 代码写得更简洁
- 官方文档：
  - Generic views：https://www.django-rest-framework.org/api-guide/generic-views/
  - Mixins：https://www.django-rest-framework.org/api-guide/generic-views/#mixins

### 当天任务

- 学习 `GenericAPIView` 的工作方式
- 理解 `ListCreateAPIView`、`RetrieveUpdateDestroyAPIView`
- 把 Day 9 的 `APIView` 升级成泛型视图
- 学会使用这些钩子：
  - `get_queryset()`
  - `get_serializer_class()`
  - `perform_create()`
  - `perform_update()`
- 让创建接口默认绑定 `request.user`

### 你今天要理解的核心差异

- `APIView` 让 DRF 可用
- 泛型视图让 DRF 真正开始省代码

## Day 11：`ViewSet`、`Router` 与 DRF 路由体系

- 学习目标：掌握 `ViewSet` 和 `Router`，理解 DRF 如何进一步把路由和视图组织得更标准
- 官方文档：
  - 教程 6：ViewSets and Routers：https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/
  - ViewSets API Guide：https://www.django-rest-framework.org/api-guide/viewsets/
  - Routers API Guide：https://www.django-rest-framework.org/api-guide/routers/

### 当天任务

- 使用 `ModelViewSet` 改写 `Note` 接口
- 使用 `DefaultRouter` 自动生成路由
- 为 `Tag` 或 `Comment` 增加一个简单 `ViewSet`
- 练习至少一个自定义 action，例如：
  - `mine`
  - `publish`

### 你今天要理解的核心差异

- 之前是“你自己配路由”
- 今天开始是“你定义资源，Router 帮你生成一套标准路由”

## Day 12：DRF 的认证、权限与对象级权限

- 学习目标：掌握 DRF 的认证类和权限类，把当前项目的权限逻辑迁移到 DRF 体系
- 官方文档：
  - Authentication：https://www.django-rest-framework.org/api-guide/authentication/
  - Permissions：https://www.django-rest-framework.org/api-guide/permissions/

### 当天任务

- 配置默认认证类和权限类
- 学习这些内建权限：
  - `AllowAny`
  - `IsAuthenticated`
  - `IsAuthenticatedOrReadOnly`
- 写一个自定义对象级权限，例如：
  - `IsOwnerOrReadOnly`
- 把“只有作者本人可修改”的逻辑迁移到 DRF 权限类

### 你今天要理解的核心差异

- 原生 Django：你在视图里自己写 `if request.user...`
- DRF：把权限规则提炼成权限类，让权限成为框架级配置

## Day 13：过滤、搜索、排序、分页

- 学习目标：掌握 DRF 的列表接口工程化能力，让资源查询更标准
- 官方文档：
  - Filtering：https://www.django-rest-framework.org/api-guide/filtering/
  - Pagination：https://www.django-rest-framework.org/api-guide/pagination/

### 当天任务

- 接入 `django-filter`
- 为 `NoteViewSet` 增加：
  - 精确过滤
  - 搜索
  - 排序
- 配置全局或局部分页

### 你今天要理解的核心差异

- 原生 Django 时代你手写查询参数和分页逻辑
- DRF 时代你开始使用标准化过滤和分页机制

## Day 14：异常处理、测试、Schema 与项目收尾

- 学习目标：补齐 DRF 的异常处理、测试和 API 描述能力，完成一轮 DRF 化收尾
- 官方文档：
  - Exceptions：https://www.django-rest-framework.org/api-guide/exceptions/
  - Testing：https://www.django-rest-framework.org/api-guide/testing/
  - Schemas：https://www.django-rest-framework.org/api-guide/schemas/

### 当天任务

- 用 `APITestCase` 或 `APIClient` 为 DRF 接口写测试
- 学会 `force_authenticate()`
- 尝试统一异常响应格式
- 生成一个基础 schema 或 schema 入口
- 对当前项目做一次 DRF 化收尾：
  - 明确旧接口和新接口如何取舍
  - 整理 README
  - 总结迁移收获

### 你今天要理解的核心差异

- DRF 不只是“更好写接口”
- 它还提供了一套更完整的 API 工程化工具链

## 这 7 天结束后的验收标准

- 你能解释 `Serializer` 和 `ModelSerializer` 的区别
- 你能解释 `APIView`、泛型视图、`ViewSet` 的差异
- 你能用 DRF 权限类接管接口访问控制
- 你能给接口加标准化的过滤、搜索和分页
- 你能用 DRF 的测试工具写基础接口测试
- 你能把当前 `StudyNotes` 项目的核心接口迁移到 DRF 风格

## DRF 学完之后下一步学什么

DRF 学完后，如果你继续沿着 API 后端方向走，建议再按这个顺序补：

1. JWT 认证
2. 接口版本管理
3. 更正式的异常处理中间件或统一响应格式
4. Redis / Celery / 缓存
5. Docker 与正式部署
6. OpenAPI 文档和前后端协作规范

## 一句总结

这 7 天不是为了再学一个“新框架”，而是为了让你在已经理解 Django Core 的基础上，真正学会 Django 生态里最核心的 API 工程化方案。

