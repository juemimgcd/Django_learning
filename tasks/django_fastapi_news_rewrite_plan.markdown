# Django 重写 `fastapi_news_application` 计划书

## 目标

使用 Django + DRF 重写参考项目 `fastapi_news_application`，并尽量保留它的核心业务边界：

- 用户注册、登录、个人信息、修改密码
- 新闻分类、新闻分页列表、新闻详情、相关推荐
- 服务端持久化 Token
- 统一响应结构
- 列表分页返回 `items / total / page / pageSize / hasMore`

今天先做两个模块：

1. `users`
2. `news`

今天不追求一次把整个 FastAPI 项目全部搬完，而是先把最核心的用户和新闻主链路搭起来。

---

## 推荐总原则

这次重写建议遵守这几条：

1. 不要继续往现在的 `notes` 学习项目里硬塞完整资讯系统。
2. 推荐新开一个 Django 项目，或者至少新开独立 apps：`users`、`news`、`common`。
3. 外部 API 契约第一版尽量贴近原 FastAPI 项目，方便你后面对照和迁移。
4. 内部代码结构继续用你现在已经顺手的分层：
   - `models.py`
   - `serializers.py`
   - `services.py`
   - `views.py`
   - `urls.py`
5. 响应格式统一，不要有的接口裸返回，有的接口再包一层。

一句话：

> 外部尽量兼容原项目，内部用 Django/DRF 的清晰分层重写。

---

## 参考项目拆解

你给的 FastAPI 项目，今天和我们最相关的几块是：

### 用户模块

- `routers/users.py`
- `crud/users.py`
- `models/users.py`
- `schemas/users.py`

用户模块当前提供的能力：

- `POST /api/user/register`
- `POST /api/user/login`
- `GET /api/user/info`
- `PUT /api/user/update`
- `PUT /api/user/password`

并且它不是 JWT，而是：

- 服务端持久化 Token
- 登录时记录 `user_login_log`

---

### 新闻模块

- `routers/news.py`
- `crud/news.py`
- `models/news.py`

新闻模块今天最值得先复刻的是：

- `GET /api/news/categories`
- `GET /api/news/list`
- `GET /api/news/detail`

其中分页逻辑很关键：

- router 负责拿 `page / pageSize`
- 计算 `offset`
- 调 `get_news_list(...)`
- 调 `get_news_total(...)`
- 再包装：
  - `items`
  - `total`
  - `page`
  - `pageSize`
  - `hasMore`

这条思路，我们已经在 `notes` 项目里练过一版，可以直接沿用。

---

## Django 对应架构

推荐项目结构：

```text
news_backend/
├─ manage.py
├─ config/
│  ├─ settings.py
│  ├─ urls.py
│  └─ ...
├─ common/
│  ├─ responses.py
│  ├─ authentication.py
│  └─ permissions.py
├─ users/
│  ├─ models.py
│  ├─ serializers.py
│  ├─ services.py
│  ├─ views.py
│  ├─ urls.py
│  └─ tests.py
└─ news/
   ├─ models.py
   ├─ serializers.py
   ├─ services.py
   ├─ views.py
   ├─ urls.py
   └─ tests.py
```

各层职责：

- `models.py`
  负责数据结构
- `serializers.py`
  负责输入校验和输出结构
- `services.py`
  负责 ORM 和业务动作
- `views.py`
  负责请求编排，尽量贴近 FastAPI 的 router 职责
- `urls.py`
  负责接口挂载
- `common/responses.py`
  负责统一成功响应
- `common/authentication.py`
  负责 Token 认证

---

## 关键设计决策

这次重写有 3 个必须早点定下来的点。

### 1. 用户模型从第一天就自定义

推荐：

- 基于 `AbstractUser` 自定义用户模型

原因：

- 原 FastAPI 项目用户字段不止 `username/password`
- 还有：
  - `nickname`
  - `avatar`
  - `gender`
  - `bio`
  - `phone`

Django 里用户模型越晚改越麻烦，所以这里不要拖。

---

### 2. Token 也按原项目走服务端持久化

推荐：

- 自己建 `UserToken` 表
- 自己写 DRF `Authentication` 类

而不是第一版先上 JWT。

原因：

- 原项目就是数据库持久化 Token
- 这样最容易贴近原始业务
- 登录、续签、失效控制都更接近原实现

---

### 3. 第一版保留原 API 路径风格

推荐：

- 暂时保留原项目路径习惯

例如：

- `POST /api/user/register`
- `POST /api/user/login`
- `GET /api/user/info`
- `PUT /api/user/update`
- `PUT /api/user/password`
- `GET /api/news/categories`
- `GET /api/news/list`
- `GET /api/news/detail?id=1`

原因：

- 这样最容易一一对照 FastAPI 项目
- 你后面如果要前端联调，也更轻松

等第一版稳定后，再决定要不要进一步 REST 化。

---

## 今天的范围：只做 `users` + `news`

今天明确只做这两块。

### 今天要做

#### `users`

- 用户模型
- Token 模型
- 登录日志模型
- 注册接口
- 登录接口
- 获取当前用户信息接口
- 更新用户信息接口
- 修改密码接口
- Token 认证链路

#### `news`

- 分类模型
- 新闻模型
- 分类列表接口
- 新闻分页列表接口
- 新闻详情接口
- 相关推荐接口
- 浏览量递增逻辑

---

### 今天不做

- 收藏模块
- 浏览历史模块
- AI 推荐模块
- 管理端统计模块
- Redis 缓存
- Docker / Compose
- Alembic 对应的 Django 管理命令迁移之外的工程化补充
- `NewsEmbedding`

一句话：

> 今天先走通“用户能登录 + 能看新闻列表和详情”这条主链路。

---

## 今天的模块设计

## 一、`users` 模块

### 1. 模型设计

推荐建 3 张表：

#### `User`

基于 `AbstractUser` 扩展这些字段：

- `nickname`
- `avatar`
- `gender`
- `bio`
- `phone`

其中：

- `username` 保留唯一
- `phone` 可空但唯一

---

#### `UserToken`

字段建议：

- `user`
- `token`
- `expires_at`
- `created_at`

用途：

- 登录后签发 Token
- 同一用户重复登录时更新 Token

这点对应原项目的 `create_token(...)`。

---

#### `UserLoginLog`

字段建议：

- `user`
- `login_date`
- `login_at`

并加联合唯一约束：

- `(user, login_date)`

用途：

- 记录每日登录
- 以后支持连续登录统计

---

### 2. serializer 设计

建议至少拆这几类：

- `UserRegisterSerializer`
- `UserLoginSerializer`
- `UserInfoSerializer`
- `UserUpdateSerializer`
- `UserChangePasswordSerializer`
- `UserAuthResponseSerializer`

另外建议从第一版开始就处理别名：

- `oldPassword -> old_password`
- `newPassword -> new_password`
- `userInfo -> user_info`

这样更容易贴近原 FastAPI 项目输入输出风格。

---

### 3. service 设计

建议拆这些函数：

- `get_user_by_username(...)`
- `create_user(...)`
- `authenticate_user(...)`
- `create_or_refresh_token(...)`
- `get_user_by_token(...)`
- `record_user_login(...)`
- `update_user(...)`
- `change_user_password(...)`

service 层负责：

- ORM 查询
- 密码哈希
- Token 刷新
- 登录日志记录

不负责：

- `Response`
- HTTP 状态码

---

### 4. view / router 设计

建议接口：

- `POST /api/user/register`
- `POST /api/user/login`
- `GET /api/user/info`
- `PUT /api/user/update`
- `PUT /api/user/password`

view 层职责：

- 用 serializer 校验输入
- 调 service
- 用 `success_response(...)` 统一包装

---

### 5. 今天 `users` 的交付标准

- [ ] 能注册
- [ ] 能登录并拿到 Token
- [ ] Token 能认证当前用户
- [ ] 能获取当前用户信息
- [ ] 能更新个人资料
- [ ] 能修改密码
- [ ] 登录当天写入或更新登录日志

---

## 二、`news` 模块

### 1. 模型设计

今天先做 2 张主表。

#### `Category`

字段建议：

- `name`
- `sort_order`

---

#### `News`

字段建议：

- `title`
- `description`
- `content`
- `image`
- `author`
- `category`
- `views`
- `publish_time`

并对这些字段考虑索引：

- `category`
- `publish_time`

这点对应原项目里的新闻列表和详情查询热点。

---

### 2. serializer 设计

建议至少拆这几类：

- `CategorySerializer`
- `NewsListSerializer`
- `NewsDetailSerializer`
- `NewsListQuerySerializer`
- `RelatedNewsSerializer`

查询参数建议直接兼容原项目：

- `categoryId`
- `page`
- `pageSize`

内部再映射成：

- `category_id`
- `page`
- `page_size`

---

### 3. service 设计

建议拆这些函数：

- `list_categories(skip=0, limit=20)`
- `list_news(category_id, skip, limit)`
- `get_news_total(category_id)`
- `get_news_detail(news_id)`
- `increase_news_views(news_id)`
- `get_related_news(category_id, news_id, limit=5)`

今天分页逻辑直接按原 FastAPI 项目思路来：

- view 里算 `offset = (page - 1) * page_size`
- service 里负责：
  - `skip`
  - `limit`
  - 查询当前页数据
- 单独再查总数
- view 最后包装：
  - `items`
  - `total`
  - `page`
  - `pageSize`
  - `hasMore`

---

### 4. view / router 设计

建议接口：

- `GET /api/news/categories`
- `GET /api/news/list`
- `GET /api/news/detail`

#### 分类列表

支持：

- `skip`
- `limit`

#### 新闻列表

支持：

- `categoryId`
- `page`
- `pageSize`

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "pageSize": 10,
    "hasMore": false
  }
}
```

#### 新闻详情

建议保持和原项目接近：

- 传 `id`
- 返回：
  - `detail`
  - `related`

同时在读取详情后：

- 浏览量 `views + 1`

---

### 5. 今天 `news` 的交付标准

- [ ] 分类列表能返回
- [ ] 新闻列表支持 `categoryId + page + pageSize`
- [ ] 列表响应结构统一
- [ ] 详情接口能返回新闻详情
- [ ] 详情接口能返回同分类相关推荐
- [ ] 查看详情时能增加浏览量

---

## 今天推荐的实现顺序

建议严格按这个顺序推进，不要乱跳：

1. 新建 Django 项目或独立 app 目录
2. 先定 `AUTH_USER_MODEL`
3. 写 `users/models.py`
4. 写 `news/models.py`
5. 先做迁移并跑通数据库
6. 写 `common/responses.py`
7. 写 `users/services.py`
8. 写 `users/serializers.py`
9. 写 `users/authentication.py`
10. 写 `users/views.py + users/urls.py`
11. 写 `news/services.py`
12. 写 `news/serializers.py`
13. 写 `news/views.py + news/urls.py`
14. 写 `users/tests.py`
15. 写 `news/tests.py`

为什么先模型再接口：

- 因为这次不是学习 demo
- 是在重写一个真实业务项目

边界先定清楚，后面才不会反复推翻。

---

## 今天的测试范围

### `users`

- 注册成功
- 用户名重复注册失败
- 登录成功
- 密码错误登录失败
- 携带 Token 获取用户信息成功
- 未认证访问用户信息失败
- 修改资料成功
- 修改密码成功

### `news`

- 分类列表成功
- 新闻列表按分类分页成功
- `pageSize` 非法时报 400
- 详情存在返回成功
- 详情不存在返回 404
- 查看详情后浏览量增加
- 相关推荐不包含当前新闻

---

## 这一阶段先不追求的点

先明确，不然很容易第一天就做散：

- 今天先不接 Redis 缓存
- 今天先不接 AI embedding
- 今天先不做后台统计接口
- 今天先不做 Docker
- 今天先不做异步任务

这些都重要，但不是今天的主线。

---

## 今天结束时，你应该拿到什么

如果今天推进顺利，晚上理想结果应该是：

1. 一个新的 Django 项目骨架
2. `users` app 可用
3. `news` app 可用
4. Token 认证跑通
5. 新闻列表分页结构跑通
6. 用户和新闻的基础测试跑通

如果这 6 条完成，这次重写就算真正开了一个好头。

---

## 下一阶段预告

等今天 `users + news` 稳定后，下一阶段建议顺序：

1. `favorites`
2. `history`
3. `admin analytics`
4. `cache`
5. `recommendation`
6. 部署和工程化

---

## 一句总结

这次 Django 重写不应该再走“先随便写通，再天天推翻”的路，而应该从第一天就把：

> 自定义用户、服务端 Token、新闻分页、统一响应、service 分层

这几个核心骨架一次定稳。

---

## 参考来源

- [项目仓库 README](https://github.com/juemimgcd/fastapi_news_application)
- [users 路由](https://raw.githubusercontent.com/juemimgcd/fastapi_news_application/refs/heads/master/routers/users.py)
- [users CRUD](https://raw.githubusercontent.com/juemimgcd/fastapi_news_application/refs/heads/master/crud/users.py)
- [users 模型](https://raw.githubusercontent.com/juemimgcd/fastapi_news_application/refs/heads/master/models/users.py)
- [news 路由](https://raw.githubusercontent.com/juemimgcd/fastapi_news_application/refs/heads/master/routers/news.py)
- [news CRUD](https://raw.githubusercontent.com/juemimgcd/fastapi_news_application/refs/heads/master/crud/news.py)
- [news 模型](https://raw.githubusercontent.com/juemimgcd/fastapi_news_application/refs/heads/master/models/news.py)
- [统一响应](https://github.com/juemimgcd/fastapi_news_application/blob/master/utils/response.py)
