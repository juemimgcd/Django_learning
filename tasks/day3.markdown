# Day 3 任务清单：把 Django 当后端来用，写笔记 CRUD JSON 接口

## 今天的目标

你这个判断是对的。

如果主要目标是学 Django 的后端能力，那么模板、页面渲染、样式这些内容都不应该占 Day 3 的大头。

所以今天我们把 Day 3 改成更适合你的一条主线：

> 不做页面 CRUD，直接用 Django 原生能力写一组笔记的 JSON 接口。

今天结束后，你应该做到这些事：

- 知道 Django 视图函数如何处理不同的 HTTP 方法
- 会用 `JsonResponse` 返回 JSON
- 会读取请求体里的 JSON 数据
- 会写最基础的接口级 CRUD
- 会返回合理的状态码
- 会用 PowerShell 测试接口

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 45 分钟 | 看 Django 视图、请求响应、URL 和查询相关文档 |
| 接口设计 | 45 分钟 | 先把今天要写的 URL 和返回格式想清楚 |
| 编码实现 | 90 分钟 | 写列表、详情、新增、更新、删除接口 |
| 联调测试 | 60 分钟 | 用 PowerShell 调接口，验证状态码和返回值 |

---

## 今天的官方文档入口

今天不再以模板和页面为主，而是优先看这些章节：

- 编写视图：https://docs.djangoproject.com/zh-hans/6.0/topics/http/views/
- URL 调度器：https://docs.djangoproject.com/zh-hans/6.0/topics/http/urls/
- 请求和响应对象：https://docs.djangoproject.com/zh-hans/6.0/ref/request-response/
- Django 便捷函数：https://docs.djangoproject.com/zh-hans/6.0/topics/http/shortcuts/
- 执行查询：https://docs.djangoproject.com/zh-hans/6.0/topics/db/queries/

如果你想知道官方教程为什么会去讲模板，也可以快速扫一眼：

- 教程第 3 部分：https://docs.djangoproject.com/zh-hans/6.0/intro/tutorial03/
- 教程第 4 部分：https://docs.djangoproject.com/zh-hans/6.0/intro/tutorial04/

但对你来说，这两部分只需要知道“Django 默认也支持全栈页面开发”就够了，今天不把精力花在这上面。

---

## 今天开始前，你当前项目已经具备什么

根据你现在的项目状态：

- `notes/models.py` 已经有 `Tag`、`Note`、`Comment`
- `notes/admin.py` 已经注册好了后台模型
- `notes/views.py` 目前还是最简单的 `HttpResponse` / `JsonResponse`
- `notes/urls.py` 目前也还是 Day 1 的基础版本

这非常适合今天继续往下推进。

因为今天我们要做的事，核心不是改数据库，而是：

- 让视图真正处理业务逻辑
- 让 URL 真正承载接口语义
- 让 Django 返回结构化 JSON

所以今天大概率：

- 不需要新增模板
- 不需要新增静态文件
- 如果模型不改，一般也不需要重新迁移

---

## 今天你必须先理解的 6 个概念

## 1. Django 视图不只是“页面函数”

很多人第一次学 Django 时，会把视图理解成“返回 HTML 的函数”。

其实更准确一点的说法是：

> Django 视图是接收请求、处理业务、返回响应的函数。

这个响应可以是：

- HTML
- JSON
- 纯文本
- 重定向
- 文件下载

你现在主要学后端，所以今天我们把重点放在 JSON 响应。

## 2. `JsonResponse` 是什么

`JsonResponse` 是 Django 自带的一个响应类，用来返回 JSON 数据。

比如：

```python
return JsonResponse({"message": "pong"})
```

返回给客户端的就是 JSON，而不是普通字符串。

你可以把它理解成 Django 里最基础的 API 返回方式。

## 3. `request.method` 是什么

在 Django 里，每个请求对象都有一个 `method` 属性。

常见值包括：

- `GET`
- `POST`
- `PUT`
- `PATCH`
- `DELETE`

所以一个视图函数完全可以根据不同方法做不同事。

比如：

- `GET /api/notes/`：获取列表
- `POST /api/notes/`：创建数据

## 4. 为什么 ORM 对象不能直接返回成 JSON

这是 Day 3 非常关键的一点。

你从数据库查出来的 `Note`，本质上是一个 Python 对象，不是 JSON。

所以你不能直接这样写：

```python
return JsonResponse(note)
```

这样通常会报错。

你需要先把对象转换成普通的 Python 数据结构，比如：

- `dict`
- `list`
- 字符串、数字、布尔值

这一步通常叫“序列化”。

今天我们先不用 Django REST Framework，而是手动做最基础的序列化，这样你会更清楚 Django 原生是怎么工作的。

## 5. 为什么今天要自己处理 JSON 请求体

因为 Django 原生并不会像 FastAPI 那样自动帮你把请求体解析成 Pydantic 对象。

所以今天你要主动理解这一步：

- 客户端提交 JSON
- 你在 Django 里读取 `request.body`
- 再把它解析成 Python 字典

这也是 Django 和 FastAPI 体验差异很明显的地方。

## 6. 状态码不是可有可无

今天你不只是“把数据返回出来”，还要开始建立后端接口意识。

至少先熟悉这些状态码：

- `200 OK`：请求成功
- `201 Created`：创建成功
- `400 Bad Request`：请求参数有问题
- `404 Not Found`：资源不存在
- `405 Method Not Allowed`：方法不支持

这会让你的接口看起来更像一个真正的后端服务。

---

## 今天要完成的接口

围绕 `StudyNotes` 项目，今天建议你完成下面 5 个接口：

- `GET /api/notes/`：获取笔记列表
- `GET /api/notes/<id>/`：获取某篇笔记详情
- `POST /api/notes/`：创建笔记
- `PATCH /api/notes/<id>/`：更新笔记
- `DELETE /api/notes/<id>/`：删除笔记

保留之前 Day 1 的：

- `/health/`
- `/api/ping/`

这样你今天结束后，项目就会开始具备真正的“后端接口形态”。

---

## 今天推荐的返回格式

为了让接口更清晰，今天建议统一使用这种风格：

### 列表接口

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "title": "Django ORM 笔记",
      "author": "admin",
      "status": "published",
      "tags": ["Python", "Django"],
      "created_at": "2026-03-23T10:00:00+08:00"
    }
  ]
}
```

### 详情接口

```json
{
  "id": 1,
  "title": "Django ORM 笔记",
  "content": "这里是正文",
  "author": "admin",
  "status": "published",
  "tags": ["Python", "Django"],
  "comments": [
    {
      "id": 1,
      "author_name": "Alice",
      "content": "写得不错"
    }
  ]
}
```

### 失败响应

```json
{
  "error": "title is required"
}
```

你今天不用追求和 DRF 一样标准化，但至少要让返回值：

- 有结构
- 易读
- 稳定

---

## 任务 1：先准备一些测试数据

如果你 Day 2 已经在 Admin 后台建过数据，那今天可以直接用。

如果还没有，建议先在后台准备：

- 1 个超级用户
- 2 个标签
- 2 篇笔记
- 1 到 2 条评论

这样你今天在写列表和详情接口时，能马上看到结果。

---

## 任务 2：先学会把模型对象转成 JSON 可用的数据

今天最关键的一步之一，就是自己写一个最简单的“序列化函数”。

### 2.1 为什么要先写这个

因为无论是列表接口还是详情接口，你最后都要做这件事：

- 从数据库拿到 `Note`
- 转成字典
- 再交给 `JsonResponse`

所以今天先把这个公共逻辑抽出来，会让后面清晰很多。

### 2.2 推荐代码

你可以在 `notes/views.py` 里先写两个辅助函数：

```python
import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Note, Tag
```

然后写：

```python
def serialize_note(note, include_comments=False):
    data = {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "author": note.author.username,
        "author_id": note.author_id,
        "status": note.status,
        "tags": [tag.name for tag in note.tags.all()],
        "tag_ids": [tag.id for tag in note.tags.all()],
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat(),
    }

    if include_comments:
        data["comments"] = [
            {
                "id": comment.id,
                "author_name": comment.author_name,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
            }
            for comment in note.comments.all()
        ]

    return data


def parse_json_body(request):
    if not request.body:
        return {}

    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None
```

### 2.3 这两段代码你要看懂什么

#### `serialize_note()`

作用就是：

- 把 Django ORM 对象转成普通字典
- 这样 `JsonResponse` 才能正常返回

#### `isoformat()`

时间对象不能随便直接返回给前端。

把它转成字符串格式会更稳妥，也更常见。

#### `parse_json_body()`

作用就是：

- 从 `request.body` 里解析 JSON
- 如果请求体为空，返回空字典
- 如果 JSON 格式不合法，返回 `None`

这个小函数能让你后面的视图代码干净很多。

---

## 任务 3：先实现列表接口和详情接口

建议先做读接口，因为这部分最容易跑通，也最适合验证序列化逻辑。

### 3.1 列表接口

在 `notes/views.py` 中加入：

```python
def api_note_list(request):
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)

    notes = (
        Note.objects.select_related("author")
        .prefetch_related("tags")
        .all()
    )

    data = {
        "count": notes.count(),
        "results": [serialize_note(note) for note in notes],
    }
    return JsonResponse(data, status=200)
```

### 3.2 为什么这里要用 `select_related` 和 `prefetch_related`

你今天先不用把它想得太复杂，只要先记住：

- `author` 是外键，适合 `select_related`
- `tags` 是多对多，适合 `prefetch_related`

这样做的目的是减少不必要的数据库查询。

这是 Django 后端里非常值得尽早形成的习惯。

### 3.3 详情接口

继续加入：

```python
def api_note_detail(request, pk):
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)

    note = get_object_or_404(
        Note.objects.select_related("author").prefetch_related("tags", "comments"),
        pk=pk,
    )
    return JsonResponse(serialize_note(note, include_comments=True), status=200)
```

### 3.4 这里你必须理解的点

#### `get_object_or_404`

如果主键存在，就返回对象。  
如果不存在，就返回 404。

这比你自己写一堆 `try/except` 更简洁。

#### 为什么详情接口要 `include_comments=True`

因为列表接口通常只返回“概要信息”，详情接口才适合返回更完整内容。

这是一种很常见的后端设计习惯。

---

## 任务 4：实现创建接口

今天先不引入 DRF，也先不引入复杂校验器，我们就用 Django 原生方式把主线跑通。

### 4.1 推荐代码

```python
@csrf_exempt
def api_note_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    payload = parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "invalid json"}, status=400)

    title = payload.get("title", "").strip()
    content = payload.get("content", "").strip()
    status_value = payload.get("status", Note.STATUS_DRAFT)
    author_id = payload.get("author_id")
    tag_ids = payload.get("tag_ids", [])

    if not title:
        return JsonResponse({"error": "title is required"}, status=400)
    if not content:
        return JsonResponse({"error": "content is required"}, status=400)
    if not author_id:
        return JsonResponse({"error": "author_id is required"}, status=400)
    if status_value not in {Note.STATUS_DRAFT, Note.STATUS_PUBLISHED}:
        return JsonResponse({"error": "invalid status"}, status=400)

    User = get_user_model()
    try:
        author = User.objects.get(pk=author_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "author not found"}, status=404)

    note = Note.objects.create(
        author=author,
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

### 4.2 为什么这里用了 `@csrf_exempt`

因为你今天是在做纯 JSON 接口，并且大概率用 PowerShell、Postman 或脚本来测试。

在这种学习阶段，如果先不接前端页面，也不走 Django 模板表单，那 CSRF 会先成为一个干扰项。

所以今天先用 `@csrf_exempt`，目的是：

- 让你专注在 Django 原生接口处理流程
- 先把请求和响应这条主线学通

但你要记住：

- 这只是学习阶段的简化
- 真实项目里不能无脑这么用

Day 6 学安全时你会再回头补这部分。

### 4.3 这段代码里你要看懂什么

#### `payload.get(...)`

从解析后的 JSON 里取值。

#### `.strip()`

去掉前后空格，避免用户传了全是空白字符的标题。

#### `get_user_model()`

通过 Django 推荐方式拿到当前项目的用户模型。

#### `note.tags.set(tags)`

多对多关系常用这个方法来整体设置。

---

## 任务 5：实现更新接口

更新接口比创建接口多一个核心点：

- 你要先找到旧对象
- 再决定哪些字段要改

### 5.1 推荐代码

```python
@csrf_exempt
def api_note_update(request, pk):
    if request.method not in {"PUT", "PATCH"}:
        return JsonResponse({"error": "method not allowed"}, status=405)

    payload = parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "invalid json"}, status=400)

    note = get_object_or_404(Note, pk=pk)

    if "title" in payload:
        title = payload.get("title", "").strip()
        if not title:
            return JsonResponse({"error": "title cannot be empty"}, status=400)
        note.title = title

    if "content" in payload:
        content = payload.get("content", "").strip()
        if not content:
            return JsonResponse({"error": "content cannot be empty"}, status=400)
        note.content = content

    if "status" in payload:
        status_value = payload["status"]
        if status_value not in {Note.STATUS_DRAFT, Note.STATUS_PUBLISHED}:
            return JsonResponse({"error": "invalid status"}, status=400)
        note.status = status_value

    if "author_id" in payload:
        User = get_user_model()
        try:
            note.author = User.objects.get(pk=payload["author_id"])
        except User.DoesNotExist:
            return JsonResponse({"error": "author not found"}, status=404)

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

### 5.2 为什么今天推荐 `PATCH`

因为 `PATCH` 更符合“部分更新”的语义。

比如你只想改标题，就不需要把全部字段都重新传一遍。

这对你有 FastAPI 背景来说会比较自然。

---

## 任务 6：实现删除接口

删除接口本身并不复杂，但它是你今天完成 CRUD 闭环的最后一步。

### 6.1 推荐代码

```python
@csrf_exempt
def api_note_delete(request, pk):
    if request.method != "DELETE":
        return JsonResponse({"error": "method not allowed"}, status=405)

    note = get_object_or_404(Note, pk=pk)
    note.delete()
    return JsonResponse({"message": "deleted"}, status=200)
```

### 6.2 这里要记住的事情

删除成功后，很多接口会返回：

- 一个简单消息
- 或者直接返回空内容

今天为了方便观察，返回一段 JSON 消息就可以。

---

## 任务 7：更新 `notes/urls.py`

把 `notes/urls.py` 改成下面这样：

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.health, name="home"),
    path("health/", views.health, name="health"),
    path("api/ping/", views.ping, name="ping"),
    path("api/notes/", views.api_note_list, name="api_note_list"),
    path("api/notes/create/", views.api_note_create, name="api_note_create"),
    path("api/notes/<int:pk>/", views.api_note_detail, name="api_note_detail"),
    path("api/notes/<int:pk>/update/", views.api_note_update, name="api_note_update"),
    path("api/notes/<int:pk>/delete/", views.api_note_delete, name="api_note_delete"),
]
```

### 为什么这里没有强行做成最严格 REST 风格

因为你现在是在学 Django 原生处理流程，不是在学 REST 规范考试题。

这套写法的好处是：

- URL 语义清晰
- 容易调试
- 对刚从 Day 1 过渡上来的项目最友好

等你后面引入 Django REST Framework 时，再把路由风格做得更标准化也完全来得及。

如果你更想练 REST 风格，也可以改成：

- `POST /api/notes/`
- `PATCH /api/notes/<id>/`
- `DELETE /api/notes/<id>/`

但今天不强求。

---

## 任务 8：整理一个可直接使用的 `notes/views.py` 结构

为了让你不容易写乱，今天建议把 `notes/views.py` 至少整理成这种结构：

```python
import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Note, Tag


def health(request):
    return HttpResponse("OK")


def ping(request):
    return JsonResponse({"message": "pong"})


def parse_json_body(request):
    ...


def serialize_note(note, include_comments=False):
    ...


def api_note_list(request):
    ...


def api_note_detail(request, pk):
    ...


@csrf_exempt
def api_note_create(request):
    ...


@csrf_exempt
def api_note_update(request, pk):
    ...


@csrf_exempt
def api_note_delete(request, pk):
    ...
```

### 为什么要这样分块

这样你以后再看这份文件时，会很清楚：

- 上面是基础导入
- 中间是公共辅助函数
- 下面才是具体接口

这是很简单但很有价值的代码组织习惯。

---

## 任务 9：用 PowerShell 测试接口

你现在是 Windows + PowerShell 环境，所以今天推荐你用 `Invoke-RestMethod` 测试。

它比在 PowerShell 里硬写 `curl` 转义更舒服。

## 9.1 测试列表接口

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/api/notes/
```

## 9.2 测试详情接口

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/api/notes/1/
```

## 9.3 测试创建接口

```powershell
$body = @{
    author_id = 1
    title = "Django Day 3 API 笔记"
    content = "今天开始把 Django 当后端框架来用。"
    status = "published"
    tag_ids = @(1, 2)
} | ConvertTo-Json -Depth 3

Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:8000/api/notes/create/ `
    -ContentType "application/json" `
    -Body $body
```

## 9.4 测试更新接口

```powershell
$body = @{
    title = "Django Day 3 API 笔记（已更新）"
    status = "draft"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Patch `
    -Uri http://127.0.0.1:8000/api/notes/1/update/ `
    -ContentType "application/json" `
    -Body $body
```

## 9.5 测试删除接口

```powershell
Invoke-RestMethod -Method Delete -Uri http://127.0.0.1:8000/api/notes/1/delete/
```

### 你今天重点不是把命令背下来

而是要观察这些事情：

- 接口是否返回 JSON
- 状态码是否合理
- 数据库里的数据是否真的变了
- 错误输入时，是否有明确报错

---

## 今天你必须真正理解的 3 条请求链路

## 1. 列表/详情读取链路

- 客户端发 GET 请求
- Django 视图查询 ORM
- ORM 对象转成字典
- `JsonResponse` 返回 JSON

## 2. 创建/更新写入链路

- 客户端发 POST 或 PATCH 请求
- Django 读取 `request.body`
- Django 把 JSON 解析成 Python 字典
- 视图校验字段
- ORM 写入数据库
- 返回新的 JSON 数据

## 3. 删除链路

- 客户端发 DELETE 请求
- Django 找到对象
- ORM 删除数据
- 返回删除结果

只要你把这 3 条链路吃透，Day 3 的后端主线就算打通了。

---

## 今天不需要做什么

为了让 Day 3 聚焦在 Django 后端，你今天先不要展开这些内容：

- 不需要写模板页面
- 不需要写 `forms.py`
- 不需要搞 CSS 或页面样式
- 不需要上 Django REST Framework
- 不需要做用户登录权限控制，Day 4 再做

今天的任务很明确：

> 先把 Django 原生的后端请求处理流程跑顺。

---

## 常见报错和排查方法

## 1. `Object of type Note is not JSON serializable`

这几乎就是在提醒你：

- 你把 ORM 对象直接塞进 `JsonResponse` 了

解决方法：

- 先转成字典
- 再返回

## 2. `JSONDecodeError`

通常说明：

- 客户端传的不是合法 JSON
- 或请求体格式不对

先检查：

- `Content-Type` 是否是 `application/json`
- 请求体是不是合法 JSON

## 3. `Method Not Allowed`

通常说明：

- 你接口里只允许某些方法
- 但你测试时用了别的方法

比如：

- 创建接口只允许 `POST`
- 你却用了 `GET`

这类报错是正常的，不一定是代码坏了。

## 4. 更新或删除时报 404

通常说明：

- 这个主键对应的数据不存在

先去 Admin 或数据库里确认一下这条数据到底还在不在。

## 5. 创建接口报 `author not found`

说明你传的 `author_id` 在数据库里不存在。

解决方法：

- 去 `/admin/` 确认用户 ID
- 或在 shell 里查一下用户

---

## 今天的交付标准

今天结束前，你至少应该完成这些事：

- [ ] 理解 `JsonResponse` 的作用
- [ ] 理解 `request.method` 和 `request.body`
- [ ] 在 `notes/views.py` 中写出序列化辅助函数
- [ ] 实现 `GET /api/notes/`
- [ ] 实现 `GET /api/notes/<id>/`
- [ ] 实现 `POST /api/notes/create/`
- [ ] 实现 `PATCH /api/notes/<id>/update/`
- [ ] 实现 `DELETE /api/notes/<id>/delete/`
- [ ] 更新 `notes/urls.py`
- [ ] 用 PowerShell 成功调通至少 3 个接口
- [ ] 能看懂成功和失败时的返回 JSON

只要这些都完成，Day 3 就算达标。

---

## 今天结束后，项目结构通常不会新增很多文件

今天和之前最大的不同是：

- 你不会新增一堆模板
- 你主要会修改已有的 `views.py` 和 `urls.py`

通常至少会涉及：

```text
notes/
├─ views.py
└─ urls.py
```

这也正好符合你当前“以后端为主”的学习目标。

---

## 今日复盘问题

今天结束后，试着不用看文档，自己回答这些问题：

1. Django 里为什么不能把 ORM 对象直接返回成 JSON？
2. `JsonResponse` 和 `HttpResponse` 的主要区别是什么？
3. `request.body` 里拿到的是什么？为什么还要再解析一次？
4. 为什么列表接口和详情接口的返回数据通常不会完全一样？
5. `select_related` 和 `prefetch_related` 大概分别适合什么关系？
6. 为什么今天先不急着上 Django REST Framework？

如果你能比较顺畅地回答这些问题，说明你今天学到的已经不是“会抄代码”，而是真正开始理解 Django 后端是怎么工作的。

---

## 可选加分任务

如果你今天状态还不错，可以多做两个小增强：

### 加分任务 1：只返回已发布的笔记

把列表接口改成默认只返回：

- `status="published"` 的笔记

这样你会更贴近真实业务查询。

### 加分任务 2：支持按标签过滤

例如支持这种请求：

```text
/api/notes/?tag_id=1
```

这能帮你提前体验 Django 查询条件是怎么一点点加上去的。

---

## 一句总结今天学了什么

今天你真正学会的不是“多写了几个接口”，而是：

> 你开始用 Django 原生能力去处理真正的后端请求了，已经从“会跑项目”进入“会写接口”的阶段。

这一步打通之后，Day 4 再去做认证和权限，你会明显更顺手。
