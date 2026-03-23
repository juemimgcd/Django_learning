# Day 8 任务清单：接入 DRF，学会 `Request`、`Response` 和第一个 `Serializer`

## 今天的目标

前面 7 天你已经会用原生 Django 写 JSON 接口了。  
今天开始，我们不是重学一套新东西，而是要解决你已经感受到的那个痛点：

> 手写 `parse_json_body()`、手写 `serialize_note()`、手写很多状态码和校验逻辑，虽然能跑，但越来越费劲。

所以今天的主线非常明确：

> 在当前项目里接入 Django REST framework，写出第一批 DRF 风格接口，并真正理解 DRF 到底帮你省掉了什么。

今天结束后，你应该做到这些事：

- 能在当前项目里接入 `djangorestframework`
- 知道 `Request` 和 `Response` 是什么
- 知道 `request.data` 和 `request.body` 的区别
- 会写第一个 DRF `Serializer`
- 会用 `@api_view` 写 DRF 函数式接口
- 能把一部分原生 Django 接口平滑迁移到 DRF 风格

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 45 分钟 | 阅读 Quickstart、Serialization、Requests and responses |
| 环境接入 | 30 分钟 | 安装 DRF，修改 `INSTALLED_APPS` |
| 核心编码 | 120 分钟 | 新建 `serializers.py`，实现第一批 DRF 接口 |
| 联调复盘 | 45 分钟 | 对比原生 Django API 和 DRF API |

---

## 今天的官方文档入口

- 快速开始：https://www.django-rest-framework.org/tutorial/quickstart/
- 教程 1：Serialization：https://www.django-rest-framework.org/tutorial/1-serialization/
- 教程 2：Requests and responses：https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
- Serializer API Guide：https://www.django-rest-framework.org/api-guide/serializers/
- Views API Guide：https://www.django-rest-framework.org/api-guide/views/

建议阅读顺序：

1. 先看 Quickstart
2. 再看 Serialization
3. 再看 Requests and responses
4. 编码时回查 `Serializer` 和 `Views` API Guide

---

## 先看一下你当前项目处于什么状态

你当前项目已经有这些东西：

- 原生 Django JSON 接口
- `JsonResponse`
- 手写 `serialize_note()`
- 手写 `parse_json_body()`
- 登录、Session、权限判断
- 中间件和测试框架

这意味着你现在学习 DRF 会特别顺，因为你已经不是在学“什么是 API”，而是在学：

- DRF 如何把这些事情做得更标准、更省力

今天建议你保留原来的 `/api/...` 路由，同时新增一套 DRF 路由放在：

- `/drf/...`

这样你能对比学习，不会把之前的成果一下子打断。

---

## 今天你必须先理解的 7 个概念

## 1. DRF 不是替代 Django，而是建立在 Django 上

你可以先把 DRF 理解成：

> Django 的 API 层增强框架。

它并没有替换这些东西：

- Django 项目结构
- Django ORM
- Django 用户系统
- Django 中间件
- Django 测试体系

它增强的是：

- API 请求解析
- 数据校验
- 响应结构
- 认证权限
- 过滤分页
- API 工程化体验

## 2. `Request` 和 Django 原生 `HttpRequest` 的区别

你之前在原生 Django 里常做这种事：

```python
payload = parse_json_body(request)
```

而在 DRF 里，你更常做的是：

```python
payload = request.data
```

这意味着：

- 原生 Django：你自己管请求体解析
- DRF：框架帮你标准化解析

这就是 DRF 很重要的一个价值点。

## 3. `Response` 和 `JsonResponse` 的区别

你之前用的是：

```python
return JsonResponse({"message": "ok"})
```

DRF 里更常用的是：

```python
return Response({"message": "ok"})
```

你可以先这样理解：

- `JsonResponse` 是 Django 原生 JSON 响应
- `Response` 是 DRF 的 API 响应入口

它能更自然地和：

- 序列化器
- 渲染器
- 状态码工具

协同工作。

## 4. `Serializer` 是什么

如果你有 FastAPI 经验，可以先把它理解成：

> DRF 里最接近 Pydantic schema 的东西。

它可以做这些事：

- 校验输入数据
- 转换输出数据
- 把 ORM 对象变成 API 返回结构
- 把请求体数据变成可安全使用的 Python 数据

这就是为什么你之前觉得手写 `serialize_note()` 很麻烦，而 DRF 能让这件事好很多。

## 5. `@api_view` 是什么

这是 DRF 提供的函数式视图装饰器。

你可以先把它理解成：

> 让一个 Django 视图函数进入 DRF 的请求响应体系。

它的作用包括：

- 限制允许的 HTTP 方法
- 把 `HttpRequest` 包装成 DRF `Request`
- 支持 DRF 的 `Response`

对你现在这个阶段特别合适，因为它能让你平滑从原生 Django 过渡到 DRF。

## 6. 为什么今天先不急着上 `APIView`

因为今天的目标是：

- 先感受 DRF 的基础请求响应和序列化体系

如果今天同时上：

- `Serializer`
- `APIView`
- `ModelSerializer`
- 权限类

信息量会过大。

所以 Day 8 的节奏应该是：

- 先接入 DRF
- 先写函数式 DRF 接口

这样最稳。

## 7. 今天学 DRF 的正确心态是什么

不要把 DRF 看成：

- “我要把前面所有代码都推翻重写”

更好的心态是：

- “我已经会原生 Django API 了，现在要学更高级、更标准的 API 组织方式”

这样你会学得非常顺。

---

## 今天建议改哪些文件

今天大概率会涉及这些文件：

```text
studynotes/
└─ settings.py

notes/
├─ serializers.py
├─ views.py
└─ urls.py
```

如果你想把 DRF 路由拆清楚，也可以新增：

```text
notes/drf_urls.py
```

但第一天不强求。

---

## 任务 1：安装并接入 DRF

### 1.1 安装依赖

建议执行：

```powershell
pip install djangorestframework
```

### 1.2 修改 `INSTALLED_APPS`

在 `studynotes/settings.py` 中加入：

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "notes",
]
```

### 1.3 为什么这一步重要

因为 DRF 不是只装包就行。

把它加到 `INSTALLED_APPS` 里，Django 才会真正把它当成项目的一部分。

---

## 任务 2：先创建 `notes/serializers.py`

这是 DRF 学习第一天最重要的新文件。

### 2.1 为什么今天必须有这个文件

因为从今天开始，你不再想把“请求体校验”和“响应结构拼装”全部堆在 `views.py` 里。

你要开始学会把这些事交给：

- `Serializer`

### 2.2 推荐先写最基础的几个序列化器

今天建议先写：

- `TagSimpleSerializer`
- `CommentSimpleSerializer`
- `NoteListSerializer`
- `NoteDetailSerializer`
- `NoteCreateSerializer`

### 2.3 推荐示例

```python
from rest_framework import serializers

from .models import Comment, Note, Tag


class TagSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class CommentSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author_name", "content", "created_at"]


class NoteListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    tags = TagSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "author",
            "status",
            "tags",
            "created_at",
            "updated_at",
        ]


class NoteDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    tags = TagSimpleSerializer(many=True, read_only=True)
    comments = CommentSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "content",
            "author",
            "status",
            "tags",
            "comments",
            "created_at",
            "updated_at",
        ]


class NoteCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    status = serializers.ChoiceField(
        choices=Note.STATUS_CHOICES,
        required=False,
        default=Note.STATUS_DRAFT,
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
    )
```

### 2.4 为什么今天故意既写 `ModelSerializer`，又写普通 `Serializer`

因为你今天正好可以对比两种风格：

- `ModelSerializer`：更省力，特别适合模型读输出
- `Serializer`：更灵活，很像你在 FastAPI 里手写请求 schema 的感觉

这个对比特别适合你现在的背景。

---

## 任务 3：写第一批 DRF 函数式接口

今天建议先用函数式 DRF 视图，不要一口气上类视图。

### 3.1 推荐导入

在 `notes/views.py` 中加入：

```python
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
```

并导入你刚写的序列化器。

### 3.2 先写列表接口

```python
@api_view(["GET"])
def drf_note_list(request):
    notes = Note.objects.select_related("author").prefetch_related("tags").all()
    serializer = NoteListSerializer(notes, many=True)
    return Response(
        {
            "count": len(serializer.data),
            "results": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
```

### 3.3 再写详情接口

```python
@api_view(["GET"])
def drf_note_detail(request, pk):
    note = get_object_or_404(
        Note.objects.select_related("author").prefetch_related("tags", "comments"),
        pk=pk,
    )
    serializer = NoteDetailSerializer(note)
    return Response(serializer.data, status=status.HTTP_200_OK)
```

### 3.4 最后写创建接口

```python
@api_view(["POST"])
def drf_note_create(request):
    if not request.user.is_authenticated:
        return Response(
            {"error": "authentication required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    serializer = NoteCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data
    note = Note.objects.create(
        author=request.user,
        title=validated["title"],
        content=validated["content"],
        status=validated.get("status", Note.STATUS_DRAFT),
    )

    tag_ids = validated.get("tag_ids", [])
    if tag_ids:
        tags = Tag.objects.filter(id__in=tag_ids)
        note.tags.set(tags)

    response_serializer = NoteDetailSerializer(note)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
```

---

## 任务 4：给 DRF 接口补路由

今天建议先走最简单路线，直接把路由写到 `notes/urls.py`。

### 4.1 推荐新增路由

```python
path("drf/notes/", views.drf_note_list, name="drf_note_list"),
path("drf/notes/create/", views.drf_note_create, name="drf_note_create"),
path("drf/notes/<int:pk>/", views.drf_note_detail, name="drf_note_detail"),
```

### 4.2 为什么今天建议保留旧接口

因为你现在最适合的是“对照学习”。

这样你可以同时看到：

- 原生 Django 版本
- DRF 版本

你会很快体会到 DRF 带来的价值，而不是抽象地“知道它更高级”。

---

## 任务 5：今天必须真正看懂的 4 个 DRF 细节

## 5.1 `request.data`

你前面写的是：

- `request.body`
- `parse_json_body(request)`

今天你开始用：

- `request.data`

你要真正体会到这件事：

- DRF 帮你统一了请求体解析入口

## 5.2 `serializer = XxxSerializer(data=request.data)`

这表示：

- 我不是在序列化 ORM 对象
- 我是在校验客户端传进来的输入数据

## 5.3 `serializer = XxxSerializer(instance)`

这表示：

- 我要把模型对象转成 API 输出数据

## 5.4 `serializer.errors`

这是 DRF 很实用的地方。

如果数据校验失败，你不需要自己手写一堆字段错误结构，DRF 会帮你整理出错误信息。

---

## 任务 6：用 PowerShell 测试 DRF 接口

### 6.1 测试列表接口

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri http://127.0.0.1:8000/drf/notes/
```

### 6.2 测试详情接口

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri http://127.0.0.1:8000/drf/notes/1/
```

### 6.3 测试创建接口

先登录保存 Session：

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

再调 DRF 创建接口：

```powershell
$body = @{
    title = "First DRF Note"
    content = "This note is created by DRF."
    status = "published"
    tag_ids = @(1, 2)
} | ConvertTo-Json -Depth 3

Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:8000/drf/notes/create/ `
    -ContentType "application/json" `
    -Body $body `
    -WebSession $session
```

---

## 今天不需要做什么

为了让 Day 8 聚焦，你今天先不要展开这些内容：

- 不需要上 `APIView`
- 不需要上 `ViewSet`
- 不需要做 DRF 权限类
- 不需要做 DRF 分页和过滤
- 不需要把所有原生接口一次性删掉

今天最重要的是：

- 先把 DRF 的基础请求响应和序列化体系跑通

---

## 常见报错和排查方法

## 1. `ModuleNotFoundError: No module named 'rest_framework'`

通常说明：

- 你还没安装 DRF
- 或虚拟环境没激活

## 2. `request.data` 里拿不到值

通常说明：

- 请求体不是合法 JSON
- 或 `Content-Type` 没设成 `application/json`

## 3. 序列化器校验失败但你不知道哪里错

先打印或查看：

```python
serializer.errors
```

这是 DRF 非常关键的调试入口。

## 4. 创建接口 401

说明：

- 你没有带登录态

DRF 并不会自动替你跳过认证逻辑。

---

## 今天的交付标准

- [ ] 安装 `djangorestframework`
- [ ] 在 `INSTALLED_APPS` 中加入 `rest_framework`
- [ ] 创建 `notes/serializers.py`
- [ ] 写出至少 1 个读序列化器
- [ ] 写出至少 1 个写序列化器
- [ ] 实现 `GET /drf/notes/`
- [ ] 实现 `GET /drf/notes/<id>/`
- [ ] 实现 `POST /drf/notes/create/`
- [ ] 看懂 `request.data`
- [ ] 对比说出 DRF 和原生 Django API 的至少 3 点差异

只要这些都完成，Day 8 就算达标。

---

## 今日复盘问题

1. 为什么 DRF 要有 `Request` 和 `Response`，而不直接只用 Django 原生对象？
2. `request.data` 和 `request.body` 的区别是什么？
3. `Serializer` 在 DRF 里承担了什么角色？
4. 为什么 `serializer = XxxSerializer(data=request.data)` 和 `serializer = XxxSerializer(instance)` 是两种不同的用法？
5. 为什么今天建议保留旧的原生 Django 接口，而不是直接全部删掉？

如果你能比较顺畅地回答这些问题，说明你已经真正进入 DRF 学习状态了。

---

## 一句总结今天学了什么

今天你真正学会的不是“又写了几条接口”，而是：

> 你开始从原生 Django API 过渡到 DRF 的 API 体系了，也第一次真正感受到 DRF 是怎么帮你省掉手写解析、手写序列化和部分样板代码的。

