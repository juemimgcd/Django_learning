# Day 4 任务清单：把认证、Session 和作者权限真正接到接口里

## 今天的目标

Day 3 你已经把 Django 原生 JSON 接口写出来了。  
今天开始，我们要让这些接口“不是谁都能随便调”。

今天的主线非常明确：

> 把 Django 自带的认证系统接到接口层，让你的 API 开始具备“登录后才能操作”和“只有作者本人才能修改”的能力。

今天结束后，你应该做到这些事：

- 知道 Django 内建认证系统是怎么工作的
- 知道 `authenticate()`、`login()`、`logout()` 分别做什么
- 知道 `request.user` 是怎么来的
- 会写登录、登出、当前用户信息接口
- 会让创建、更新、删除笔记接口带上权限控制
- 能理解 `401` 和 `403` 的区别

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 45 分钟 | 看 Django 认证、Session、权限文档 |
| 接口实现 | 90 分钟 | 实现登录、登出、当前用户信息接口 |
| 权限接入 | 60 分钟 | 把创建、更新、删除接口接入登录态和作者权限 |
| 联调测试 | 45 分钟 | 用 PowerShell 带 Session 测试接口 |

---

## 今天的官方文档入口

- Django 中的用户认证：https://docs.djangoproject.com/zh-hans/6.0/topics/auth/
- 使用 Django 的验证系统：https://docs.djangoproject.com/zh-hans/6.0/topics/auth/default/
- 会话框架：https://docs.djangoproject.com/zh-hans/6.0/topics/http/sessions/
- 自定义认证：https://docs.djangoproject.com/zh-hans/6.0/topics/auth/customizing/

今天的建议阅读顺序：

1. 先看“用户认证”总览
2. 再看 `authenticate`、`login`、`logout`
3. 再看 Session 是怎么保存登录态的
4. 自定义认证今天只做了解，不作为主任务

---

## 先看一下你当前项目的状态

根据你现在的项目：

- `notes/models.py` 已经有 `Note.author`
- `notes/views.py` 已经有 Day 3 的 CRUD 接口
- `notes/urls.py` 已经有 `/api/notes/...` 路由
- 你当前的创建接口还是靠前端传 `author_id`
- 更新接口目前也允许通过请求体修改 `author_id`

这说明：

- 你的接口已经能“操作数据”
- 但还没有真正的“用户身份意识”

所以今天最重要的改动就是：

- 让“谁在请求”这件事进入你的业务逻辑
- 让“谁能改哪些数据”开始有规则

---

## 今天你必须先理解的 7 个概念

## 1. Django 的认证系统不是额外插件，而是框架核心能力

Django 默认自带：

- 用户模型
- 登录登出逻辑
- Session 支持
- 权限和组
- Admin 集成

这和 FastAPI 很不一样。

FastAPI 通常更像：

- 框架本身负责接口
- 认证、权限、Token 往往由你组合额外组件

而 Django 是一整套打包好的能力。

## 2. `authenticate()` 是什么

你可以先把它理解成：

> 帮你验证“用户名和密码对不对”。

如果认证成功，它会返回一个用户对象。  
如果失败，返回 `None`。

它本身不会登录，只负责“核验身份”。

## 3. `login()` 是什么

`login(request, user)` 的作用是：

> 把这个用户写进当前会话，让后续请求都知道“这个人已经登录了”。

也就是说：

- `authenticate()`：核对账号密码
- `login()`：建立登录态

这两个动作不是同一件事。

## 4. `logout()` 是什么

`logout(request)` 的作用是：

- 清掉当前会话里的登录信息
- 让用户恢复成未登录状态

## 5. `request.user` 是什么

一旦用户登录成功，Django 在后续请求里就会把当前用户放到：

```python
request.user
```

如果没登录，一般就是 `AnonymousUser`。

所以你在接口里可以写：

```python
if not request.user.is_authenticated:
    ...
```

这就是 Django 最常见的登录判断方式之一。

## 6. 什么是 Session

你可以先把 Session 理解成：

> Django 用来记住“这个请求是谁发来的”的机制。

典型流程是：

1. 用户登录成功
2. Django 在服务器端保存会话信息
3. 客户端保存一个 Session Cookie
4. 后续请求带上这个 Cookie
5. Django 就知道这是同一个用户

这也是为什么今天测试接口时，你不能只发一次登录请求就完事，而是要保存会话。

## 7. `401` 和 `403` 的区别

这两个状态码很容易混。

你今天要先这样理解：

- `401 Unauthorized`：你还没登录，或者登录态无效
- `403 Forbidden`：你已经登录了，但你没有权限做这件事

举例：

- 没登录就创建笔记：`401`
- 登录了，但想删别人的笔记：`403`

这个区分很重要，因为它体现的是“权限语义”。

---

## 今天要完成的接口

今天建议你完成这 3 个新接口：

- `POST /api/login/`
- `POST /api/logout/`
- `GET /api/me/`

并修改 Day 3 已有接口：

- `POST /api/notes/create/`
- `PATCH /api/notes/<id>/update/`
- `DELETE /api/notes/<id>/delete/`

最终目标是让这些规则成立：

- 未登录用户不能创建、更新、删除笔记
- 已登录用户创建笔记时，作者自动取 `request.user`
- 已登录用户只能修改或删除自己的笔记

---

## 今天推荐的整体思路

为了让代码不乱，今天建议你在 `notes/views.py` 里增加一些小的辅助函数。

比如：

- 一个统一返回错误 JSON 的函数
- 一个统一判断是否登录的函数
- 一个统一判断是否是作者本人的函数

这样做的好处是：

- 视图函数更短
- 权限判断逻辑更集中
- 以后 Day 5、Day 6 扩展更方便

---

## 任务 1：先增加几个通用辅助函数

### 1.1 推荐加一个统一错误返回函数

```python
def json_error(message, status=400):
    return JsonResponse({"error": message}, status=status)
```

### 为什么这个小函数值得写

因为从今天开始，你会频繁返回这种错误：

- 未登录
- 权限不足
- 用户名密码错误
- 方法不支持

如果每次都重复写一大段 `JsonResponse({"error": ...}, status=...)`，代码会越来越碎。

---

## 任务 2：实现登录接口

### 2.1 推荐导入

在 `notes/views.py` 顶部加入：

```python
from django.contrib.auth import authenticate, login, logout
```

### 2.2 推荐代码

```python
@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return json_error("method not allowed", 405)

    payload = parse_json_body(request)
    if payload is None:
        return json_error("invalid json", 400)

    username = payload.get("username", "").strip()
    password = payload.get("password", "")

    if not username:
        return json_error("username is required", 400)
    if not password:
        return json_error("password is required", 400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return json_error("invalid credentials", 401)

    login(request, user)
    return JsonResponse(
        {
            "message": "login success",
            "user": {
                "id": user.id,
                "username": user.username,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            },
        },
        status=200,
    )
```

### 2.3 这里你要看懂什么

#### `authenticate(...)`

检查用户名和密码对不对。

#### `login(request, user)`

不是返回 token，而是建立 Session 登录态。

#### 为什么登录成功后不只是返回 `"ok"`

因为后端接口最好给出一些有信息量的返回，比如：

- 当前用户 ID
- 用户名
- 是否是 staff

这样测试时也更容易观察。

---

## 任务 3：实现登出接口

### 3.1 推荐代码

```python
@csrf_exempt
def api_logout(request):
    if request.method != "POST":
        return json_error("method not allowed", 405)

    if not request.user.is_authenticated:
        return json_error("authentication required", 401)

    logout(request)
    return JsonResponse({"message": "logout success"}, status=200)
```

### 3.2 这里你要理解的事情

登出接口不是“删数据库里的用户”，也不是“销毁账号”。

它做的只是：

- 清掉这次会话里的登录信息

这也是为什么登出之后再去访问受保护接口，通常就会返回 `401`。

---

## 任务 4：实现当前用户信息接口

### 4.1 推荐代码

```python
def api_me(request):
    if not request.user.is_authenticated:
        return json_error("authentication required", 401)

    user = request.user
    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        },
        status=200,
    )
```

### 4.2 为什么这个接口很有价值

虽然它看起来简单，但它非常适合拿来验证：

- 你的登录到底有没有成功
- Session 是否真的被带上了
- `request.user` 是否已经可用

几乎每个带登录态的后端系统，都会有一个类似“当前用户信息”的接口。

---

## 任务 5：先写两个权限辅助函数

今天建议你别把权限判断散落在每个接口里，而是先抽两个小函数。

### 5.1 登录判断辅助函数

```python
def require_authenticated_user(request):
    if not request.user.is_authenticated:
        return json_error("authentication required", 401)
    return None
```

### 5.2 作者判断辅助函数

```python
def require_note_owner(request, note):
    if note.author_id != request.user.id:
        return json_error("permission denied", 403)
    return None
```

### 为什么这两个函数很重要

因为从今天开始，权限逻辑会越来越多。

如果你一开始就把它们拆清楚，后面代码会更稳。

---

## 任务 6：修改创建接口，让作者自动来自当前登录用户

### 6.1 这是今天最关键的业务调整

Day 3 你的创建接口是这样的思路：

- 客户端传 `author_id`
- 后端根据这个 ID 找用户

今天开始，这个思路要变掉。

因为这存在一个明显问题：

- 用户 A 完全可以伪造 `author_id`
- 然后冒充别人创建数据

所以从 Day 4 开始，正确思路是：

- 用户先登录
- Django 通过 Session 知道当前用户是谁
- 创建笔记时直接用 `request.user`

### 6.2 推荐改法

```python
@csrf_exempt
def api_note_create(request):
    if request.method != "POST":
        return json_error("method not allowed", 405)

    auth_error = require_authenticated_user(request)
    if auth_error:
        return auth_error

    payload = parse_json_body(request)
    if payload is None:
        return json_error("invalid json", 400)

    title = payload.get("title", "").strip()
    content = payload.get("content", "").strip()
    status_value = payload.get("status", Note.STATUS_DRAFT)
    tag_ids = payload.get("tag_ids", [])

    if not title:
        return json_error("title is required", 400)
    if not content:
        return json_error("content is required", 400)
    if status_value not in {Note.STATUS_DRAFT, Note.STATUS_PUBLISHED}:
        return json_error("invalid status", 400)

    note = Note.objects.create(
        author=request.user,
        title=title,
        content=content,
        status=status_value,
    )

    if tag_ids:
        tags = Tag.objects.filter(id__in=tag_ids)
        note.tags.set(tags)

    note = (
        Note.objects.select_related("author")
        .prefetch_related("tags")
        .get(pk=note.pk)
    )
    return JsonResponse(serialize_note(note), status=201)
```

### 6.3 这里你要真正理解的事情

从今天开始：

- 客户端不再决定“作者是谁”
- 后端根据登录态自己决定作者是谁

这才是权限设计里更正常的做法。

---

## 任务 7：修改更新接口，只允许作者本人修改

### 7.1 推荐改法

```python
@csrf_exempt
def api_note_update(request, pk):
    if request.method not in {"PUT", "PATCH"}:
        return json_error("method not allowed", 405)

    auth_error = require_authenticated_user(request)
    if auth_error:
        return auth_error

    payload = parse_json_body(request)
    if payload is None:
        return json_error("invalid json", 400)

    note = get_object_or_404(Note, pk=pk)

    owner_error = require_note_owner(request, note)
    if owner_error:
        return owner_error

    if "title" in payload:
        title = payload.get("title", "").strip()
        if not title:
            return json_error("title cannot be empty", 400)
        note.title = title

    if "content" in payload:
        content = payload.get("content", "").strip()
        if not content:
            return json_error("content cannot be empty", 400)
        note.content = content

    if "status" in payload:
        status_value = payload["status"]
        if status_value not in {Note.STATUS_DRAFT, Note.STATUS_PUBLISHED}:
            return json_error("invalid status", 400)
        note.status = status_value

    note.save()

    if "tag_ids" in payload:
        tags = Tag.objects.filter(id__in=payload["tag_ids"])
        note.tags.set(tags)

    note = (
        Note.objects.select_related("author")
        .prefetch_related("tags")
        .get(pk=note.pk)
    )
    return JsonResponse(serialize_note(note), status=200)
```

### 7.2 今天建议你顺手做一个简化

既然已经接入登录态，那就不要再允许客户端通过更新接口修改 `author_id` 了。

这样做的好处是：

- 权限逻辑更清楚
- 数据归属不容易乱
- 你的接口语义更稳定

---

## 任务 8：修改删除接口，只允许作者本人删除

### 8.1 推荐改法

```python
@csrf_exempt
def api_note_delete(request, pk):
    if request.method != "DELETE":
        return json_error("method not allowed", 405)

    auth_error = require_authenticated_user(request)
    if auth_error:
        return auth_error

    note = get_object_or_404(Note, pk=pk)

    owner_error = require_note_owner(request, note)
    if owner_error:
        return owner_error

    note.delete()
    return JsonResponse({"message": "deleted"}, status=200)
```

### 8.2 这段逻辑的权限顺序很重要

推荐顺序是：

1. 先看有没有登录
2. 再看资源存不存在
3. 再看是不是作者本人
4. 最后才执行删除

这样你的接口逻辑会更清晰，也更容易排错。

---

## 任务 9：更新 `notes/urls.py`

今天建议把下面 3 个路由补上：

```python
path("api/login/", views.api_login, name="api_login"),
path("api/logout/", views.api_logout, name="api_logout"),
path("api/me/", views.api_me, name="api_me"),
```

所以最终大致会变成：

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.health, name="home"),
    path("health/", views.health, name="health"),
    path("api/ping/", views.ping, name="ping"),
    path("api/login/", views.api_login, name="api_login"),
    path("api/logout/", views.api_logout, name="api_logout"),
    path("api/me/", views.api_me, name="api_me"),
    path("api/notes/", views.api_note_list, name="api_note_list"),
    path("api/notes/create/", views.api_note_create, name="api_note_create"),
    path("api/notes/<int:pk>/", views.api_note_detail, name="api_note_detail"),
    path("api/notes/<int:pk>/update/", views.api_note_update, name="api_note_update"),
    path("api/notes/<int:pk>/delete/", views.api_note_delete, name="api_note_delete"),
]
```

---

## 任务 10：用 PowerShell 测试登录态

今天和 Day 3 最大的不同是：

- 你不能再只发一次请求看结果
- 你要开始保存 Session

在 PowerShell 里，推荐这么测。

### 10.1 登录并保存 Session

```powershell
$loginBody = @{
    username = "admin"
    password = "你的密码"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:8000/api/login/ `
    -ContentType "application/json" `
    -Body $loginBody `
    -SessionVariable session
```

### 10.2 用同一个 Session 调当前用户接口

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri http://127.0.0.1:8000/api/me/ `
    -WebSession $session
```

### 10.3 用同一个 Session 创建笔记

```powershell
$body = @{
    title = "Day 4 登录态笔记"
    content = "现在创建接口会自动使用当前登录用户。"
    status = "published"
    tag_ids = @(1, 2)
} | ConvertTo-Json -Depth 3

Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:8000/api/notes/create/ `
    -ContentType "application/json" `
    -Body $body `
    -WebSession $session
```

### 10.4 用另一个用户测试 `403`

如果你创建了第二个普通用户，可以：

- 先让用户 A 创建一篇笔记
- 再用用户 B 登录
- 尝试修改或删除用户 A 的笔记

这时你应该看到：

- `403 permission denied`

### 10.5 测试登出

```powershell
Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:8000/api/logout/ `
    -WebSession $session
```

然后再次请求：

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri http://127.0.0.1:8000/api/me/ `
    -WebSession $session
```

你应该看到：

- `401 authentication required`

---

## 今天你必须真正理解的 3 条身份链路

## 1. 登录链路

- 客户端提交用户名和密码
- Django 用 `authenticate()` 验证账号密码
- Django 用 `login()` 建立 Session
- 后续请求开始拥有登录态

## 2. 当前用户识别链路

- 客户端带上 Session Cookie
- Django 在请求过程中恢复当前用户
- 你通过 `request.user` 获取这个用户

## 3. 权限判断链路

- 先判断用户是否登录
- 再判断资源是否存在
- 再判断用户是否有权限操作资源
- 最后才允许修改或删除

只要你把这 3 条链路吃透，Day 4 的核心就算真正掌握了。

---

## 今天不推荐你做的事

为了让 Day 4 聚焦，你今天先不要展开这些内容：

- 不需要上 JWT
- 不需要急着换成 DRF 权限类
- 不需要自定义用户模型
- 不需要做复杂角色系统

今天你最需要学的是 Django 自带认证系统的基本工作方式。

这一步如果不理解，后面很多高级方案你会“会抄不会懂”。

---

## 常见报错和排查方法

## 1. `request.user` 一直是匿名用户

通常说明：

- 你登录请求成功了
- 但后续请求没有带上 Session

最常见原因是：

- 你没有用 `-SessionVariable`
- 或后续请求忘了传 `-WebSession $session`

## 2. 登录一直失败

通常说明：

- 用户名写错
- 密码写错
- 根本没有这个用户

先去 Admin 后台确认：

- 用户是否存在
- 用户名是不是你以为的那个

## 3. 创建接口返回 `401`

说明：

- 你还没登录
- 或你的登录态没有被正确带过去

## 4. 修改接口返回 `403`

说明：

- 你已经登录了
- 但当前笔记不是你创建的

这不是坏事，反而说明你的权限判断开始生效了。

## 5. 登录成功但登出后还能访问受保护接口

这通常说明：

- 你没有真的用同一个 Session 在测
- 或代码里 `logout()` 没走到

先看：

- 请求方法是不是 `POST`
- 后续请求是不是还带着旧会话

---

## 今天的交付标准

今天结束前，你至少应该完成这些事：

- [ ] 理解 `authenticate()`、`login()`、`logout()` 的作用
- [ ] 实现 `POST /api/login/`
- [ ] 实现 `POST /api/logout/`
- [ ] 实现 `GET /api/me/`
- [ ] 创建接口改为自动使用 `request.user`
- [ ] 更新接口增加登录限制
- [ ] 删除接口增加登录限制
- [ ] 更新和删除接口增加作者本人权限判断
- [ ] 用 PowerShell 成功保存 Session 并调用受保护接口
- [ ] 至少验证一次 `401`
- [ ] 至少验证一次 `403`

只要这些都完成，Day 4 就算达标。

---

## 今天结束后，项目里通常会改动哪些位置

今天主要会改这些文件：

```text
notes/
├─ views.py
└─ urls.py
```

如果你顺手优化 Admin，也可能会再碰一下：

```text
notes/admin.py
```

但今天最核心的战场一定是：

- `views.py`
- `urls.py`

---

## 今日复盘问题

今天结束后，试着不用看文档，自己回答这些问题：

1. `authenticate()` 和 `login()` 到底有什么区别？
2. Django 为什么能在后续请求里知道当前用户是谁？
3. `request.user` 在没登录时通常是什么？
4. `401` 和 `403` 的区别是什么？
5. 为什么创建笔记时不应该继续让前端传 `author_id`？
6. 为什么今天用 PowerShell 测试时要保留 Session？

如果你能比较顺畅地回答这些问题，说明你已经不是只会“调通接口”，而是真正开始理解 Django 的认证和权限模型了。

---

## 可选加分任务

如果你今天状态不错，可以多做两个增强：

### 加分任务 1：把 `request.user` 也加进 `serialize_note()` 的调试输出中

不是长期设计，只是为了帮助你验证：

- 创建出来的笔记作者到底是不是当前登录用户

### 加分任务 2：让 `GET /api/notes/` 只返回当前登录用户自己的笔记

例如新增一个接口：

- `GET /api/my-notes/`

这会帮你更早体会“用户域数据”这种很常见的业务需求。

---

## 一句总结今天学了什么

今天你真正学会的不是“又多了 3 个接口”，而是：

> 你开始让 Django 的接口真正具备用户身份意识了，项目也第一次有了“谁能做什么”的规则。

这一关打通之后，你的 Django 项目才算真正从“能 CRUD”走向“有权限边界的后端服务”。
