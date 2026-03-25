# Day 5 任务清单：学会请求对象、中间件、查询参数、分页和 async 边界

## 今天的目标

Day 3 你已经有了基础 CRUD 接口。  
Day 4 你已经把登录、Session 和权限接到了接口里。

今天的重点，是让你的接口从“能用”开始走向“更像真实后端项目”。

今天的主线很明确：

> 学会读懂 Django 的请求对象，给列表接口加查询参数和分页，再写一个请求日志中间件，同时理解 Django 的 async 支持边界。

今天结束后，你应该做到这些事：

- 知道 `HttpRequest` 上最常用的数据都放在哪里
- 会区分 `request.GET`、`request.body`、`request.headers`
- 会给列表接口加过滤、搜索和分页
- 会写一个最基础的中间件
- 会理解中间件在 Django 请求链中的位置
- 会知道 Django 的 async 到底“能用到什么程度”

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 45 分钟 | 看请求响应、中间件、异步支持文档 |
| 中间件实现 | 45 分钟 | 编写请求日志中间件并接到项目里 |
| 接口增强 | 90 分钟 | 给 `GET /api/notes/` 增加过滤、搜索、分页 |
| 联调与复盘 | 60 分钟 | 用 PowerShell 验证请求参数、中间件日志和异步接口 |

---

## 今天的官方文档入口

- 请求和响应对象：https://docs.djangoproject.com/zh-hans/6.0/ref/request-response/
- 中间件：https://docs.djangoproject.com/zh-hans/6.0/topics/http/middleware/
- 异步支持：https://docs.djangoproject.com/zh-hans/6.0/topics/async/
- 执行查询：https://docs.djangoproject.com/zh-hans/6.0/topics/db/queries/

建议阅读顺序：

1. 先看请求和响应对象
2. 再看中间件
3. 最后看异步支持

今天的重点不是把文档全背下来，而是知道：

- 请求里的不同数据从哪里拿
- 中间件是怎么包住请求和响应的
- 什么时候 async 真的有价值

---

## 先看一下你当前项目状态

根据你现在的代码：

- `notes/views.py` 里已经有：
  - `api_login`
  - `api_logout`
  - `api_me`
  - `api_note_list`
  - `api_note_detail`
  - `api_note_create`
  - `api_note_update`
  - `api_note_delete`
- `notes/urls.py` 里已经接好了这些接口
- 你已经有：
  - 认证
  - Session
  - 作者权限

这非常适合做 Day 5。

因为今天不是再加一堆新业务，而是开始让“列表接口更像真实接口”。

你会重点改这些地方：

- `notes/views.py`
- `studynotes/settings.py`
- 新增一个 middleware 文件

---

## 今天你必须先理解的 8 个概念

## 1. `HttpRequest` 是 Django 后端开发的核心入口

你可以把 `request` 理解成：

> Django 帮你打包好的“这次 HTTP 请求的全部信息”。

这个对象里会有很多东西，比如：

- 请求方法
- 查询参数
- 请求头
- 请求体
- 当前用户
- Cookie
- Session

你前几天已经用过一部分了，比如：

- `request.method`
- `request.body`
- `request.user`

今天要把这张图补完整。

## 2. `request.GET` 是什么

`request.GET` 表示 URL 查询参数。

比如请求：

```text
/api/notes/?status=published&page=2
```

你就可以这样取值：

```python
status_value = request.GET.get("status")
page = request.GET.get("page")
```

虽然名字叫 `GET`，但它本质表示的是：

- URL 上的查询字符串参数

不一定只在 GET 请求里出现。

## 3. `request.body` 是什么

`request.body` 是原始请求体，通常是字节串。

你 Day 3 和 Day 4 已经在用它做 JSON 解析了。

可以这样理解：

- `request.GET`：URL 参数
- `request.body`：请求体里的原始内容

这两者不是一回事。

## 4. `request.headers` 是什么

`request.headers` 可以拿到请求头。

比如：

```python
user_agent = request.headers.get("User-Agent")
content_type = request.headers.get("Content-Type")
```

这在日志、中间件、鉴权、调试时都很常用。

## 5. 中间件是什么

你可以先把中间件理解成：

> 在请求到达视图之前、以及响应返回客户端之前，插进去的一层“统一处理逻辑”。

它特别适合处理这些事：

- 请求日志
- 身份恢复
- 安全检查
- 统一异常处理
- 请求耗时统计

所以你会发现，Django 的很多“框架能力”其实都建立在中间件上。

## 6. 为什么列表接口一定要学查询参数

因为真实项目里，列表接口几乎不可能永远只做：

- “查全部”

通常总会逐渐出现这些需求：

- 按状态筛选
- 按作者筛选
- 按标签筛选
- 按关键词搜索
- 分页

如果你今天把这条线学会了，你对 Django ORM 和请求对象的理解会明显加深。

## 7. 分页不是锦上添花，而是基本素养

当数据少的时候，`all()` 看起来很方便。  
但数据一多，直接全返回通常是不合适的。

分页的意义是：

- 控制单次返回量
- 减少响应体大小
- 让客户端更容易处理数据

今天你不需要做复杂分页，只做最基础版就够了。

## 8. Django 的 async 不是 FastAPI 那种“天然 API-first async”

这是今天最容易误判的一点。

Django 当然支持 async 视图，但你要先建立正确预期：

- 可以写 `async def`
- 可以在异步视图里做一些异步 IO
- 但 Django 整体不是完全围绕 async 设计的
- ORM 也不是你熟悉的那种完全 async-first 体验

所以今天学 async 的目标不是“把项目全改异步”，而是：

- 理解它能做什么
- 理解它现在不该乱用到什么程度

---

## 今天建议完成的功能

今天围绕现有项目，建议完成这些增强：

- 给 `GET /api/notes/` 增加过滤能力：
  - `status`
  - `author_id`
  - `tag_id`
  - `keyword`
- 给 `GET /api/notes/` 增加基础分页：
  - `page`
  - `page_size`
- 写一个请求日志中间件
- 增加一个简单异步接口

---

## 任务 1：先学会从请求对象里拿查询参数

### 1.1 建议先用最小例子理解

比如请求：

```text
GET /api/notes/?status=published&page=1&page_size=5
```

在 Django 里，你可以这样拿：

```python
status_value = request.GET.get("status")
page = request.GET.get("page", "1")
page_size = request.GET.get("page_size", "10")
```

### 1.2 这里你要记住的事情

#### `get("key")`

没有这个参数时，返回 `None`。

#### `get("key", "default")`

没有时，返回默认值。

#### 为什么默认值通常先写成字符串

因为 URL 参数本来就是字符串。

比如：

```python
page = int(request.GET.get("page", "1"))
```

先拿字符串，再手动转成整数，这个思路最稳定。

---

## 任务 2：增强 `api_note_list`，支持过滤

今天最核心的功能增强就是这个。

## 2.1 先想清楚要支持哪些过滤条件

建议支持：

- `status`
- `author_id`
- `tag_id`
- `keyword`

例如：

```text
/api/notes/?status=published
/api/notes/?author_id=1
/api/notes/?tag_id=2
/api/notes/?keyword=django
```

## 2.2 推荐改造思路

你可以把 `api_note_list` 先改造成这种结构：

```python
def api_note_list(request):
    if request.method != "GET":
        return json_error("method not allowed", 405)

    notes = Note.objects.select_related("author").prefetch_related("tags").all()

    status_value = request.GET.get("status")
    author_id = request.GET.get("author_id")
    tag_id = request.GET.get("tag_id")
    keyword = request.GET.get("keyword")

    if status_value:
        notes = notes.filter(status=status_value)

    if author_id:
        notes = notes.filter(author_id=author_id)

    if tag_id:
        notes = notes.filter(tags__id=tag_id)

    if keyword:
        notes = notes.filter(title__icontains=keyword)

    notes = notes.distinct()

    data = {
        "count": notes.count(),
        "results": [serialize_note(note) for note in notes],
    }
    return JsonResponse(data, status=200)
```

## 2.3 这里你要看懂什么

#### `filter(...)`

是 QuerySet 最常用的条件查询方式。

#### `tags__id=tag_id`

表示跨关联关系过滤。

你可以把双下划线 `__` 理解成：

- 沿着关联字段继续往里找

#### `title__icontains=keyword`

表示不区分大小写的包含搜索。

这在关键词搜索里很常见。

#### `distinct()`

因为按标签多对多过滤时，某些查询场景可能会出现重复结果。  
先加上 `distinct()` 是个不错的习惯。

---

## 任务 3：给列表接口加基础分页

今天不用做复杂分页，先做最简单、最实用的一版。

## 3.1 推荐支持的参数

- `page`
- `page_size`

例如：

```text
/api/notes/?page=1&page_size=5
```

## 3.2 推荐实现方式

你今天可以先手写分页逻辑，不一定非要一上来用 Django 的 `Paginator`。

比如：

```python
page = request.GET.get("page", "1")
page_size = request.GET.get("page_size", "10")

try:
    page = int(page)
    page_size = int(page_size)
except ValueError:
    return json_error("page and page_size must be integers", 400)

if page < 1:
    return json_error("page must be >= 1", 400)
if page_size < 1:
    return json_error("page_size must be >= 1", 400)
if page_size > 50:
    return json_error("page_size must be <= 50", 400)

total = notes.count()
offset = (page - 1) * page_size
notes = notes[offset : offset + page_size]
```

然后返回时这样组织：

```python
data = {
    "count": total,
    "page": page,
    "page_size": page_size,
    "results": [serialize_note(note) for note in notes],
}
```

## 3.3 为什么分页建议加上最大值限制

比如：

- `page_size <= 50`

这是为了避免有人一次请求要 10000 条数据。

哪怕是学习项目，也建议早点建立这种意识。

---

## 任务 4：把过滤和分页合并进同一个列表接口

今天建议你最终把 `api_note_list` 做成这样一个流程：

1. 先限制请求方法
2. 创建基础 QuerySet
3. 读取查询参数
4. 叠加过滤条件
5. 计算分页
6. 返回结构化 JSON

## 4.1 推荐最终结构

```python
def api_note_list(request):
    if request.method != "GET":
        return json_error("method not allowed", 405)

    notes = Note.objects.select_related("author").prefetch_related("tags").all()

    status_value = request.GET.get("status")
    author_id = request.GET.get("author_id")
    tag_id = request.GET.get("tag_id")
    keyword = request.GET.get("keyword")
    page = request.GET.get("page", "1")
    page_size = request.GET.get("page_size", "10")

    if status_value:
        notes = notes.filter(status=status_value)
    if author_id:
        notes = notes.filter(author_id=author_id)
    if tag_id:
        notes = notes.filter(tags__id=tag_id)
    if keyword:
        notes = notes.filter(title__icontains=keyword)

    notes = notes.distinct()

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return json_error("page and page_size must be integers", 400)

    if page < 1:
        return json_error("page must be >= 1", 400)
    if page_size < 1:
        return json_error("page_size must be >= 1", 400)
    if page_size > 50:
        return json_error("page_size must be <= 50", 400)

    total = notes.count()
    offset = (page - 1) * page_size
    notes = notes[offset : offset + page_size]

    data = {
        "count": total,
        "page": page,
        "page_size": page_size,
        "results": [serialize_note(note) for note in notes],
    }
    return JsonResponse(data, status=200)
```

## 4.2 这里你要真正理解的点

列表接口不是简单的“查表然后返回”。

从今天开始，它已经开始变成一个真正有后端味道的接口：

- 会读请求参数
- 会根据条件动态拼查询
- 会限制返回数量
- 会做参数校验

这正是后端开发最常见的事情之一。

---

## 任务 5：写一个请求日志中间件

今天第二个重点，是体验 Django 的中间件机制。

## 5.1 这个中间件要做什么

建议你先写一个最朴素但很有价值的版本：

- 记录请求方法
- 记录请求路径
- 记录响应状态码
- 记录请求耗时

这已经是很多项目里非常实用的最小中间件了。

## 5.2 建议新建文件

在 `notes/` 下新建：

```text
notes/middleware.py
```

## 5.3 推荐代码

```python
import time
import uuid


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        request.request_id = request_id
        start_time = time.perf_counter()

        response = self.get_response(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        print(
            f"[request_id={request_id}] "
            f"{request.method} {request.path} "
            f"status={response.status_code} "
            f"duration_ms={duration_ms:.2f}"
        )

        response["X-Request-ID"] = request_id
        return response
```

## 5.4 这段代码你要看懂什么

#### `__init__(self, get_response)`

中间件初始化时，Django 会把下一个处理环节传给你。

#### `__call__(self, request)`

每次请求进来时都会走这里。

#### `self.get_response(request)`

这一步就是把请求继续传下去：

- 可能传给下一个中间件
- 最终传到视图

#### 为什么先记录开始时间，再拿响应后计算耗时

因为你要统计的是整次请求处理花了多久。

#### `response["X-Request-ID"] = request_id`

这是一个很实用的小增强：

- 让客户端也能拿到这次请求的唯一标识

真实项目里排查问题时很有帮助。

---

## 任务 6：把中间件接到 `settings.py`

### 6.1 修改 `studynotes/settings.py`

把你的中间件加到 `MIDDLEWARE` 里：

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'notes.middleware.RequestLogMiddleware',
]
```

### 6.2 放在前面还是后面

今天这个学习版中间件放后面就可以。

原因是：

- 你更容易先看到 Django 默认中间件已经处理后的请求结果

以后你对中间件顺序更熟之后，再去深入研究“放前还是放后”的影响。

---

## 任务 7：验证中间件是否生效

启动服务后，访问：

- `/health/`
- `/api/ping/`
- `/api/notes/`

你应该在终端看到类似：

```text
[request_id=xxxxxx] GET /api/notes/ status=200 duration_ms=12.34
```

同时响应头里也会带上：

```text
X-Request-ID: xxxxxx
```

这就说明你的中间件已经工作了。

---

## 任务 8：增加一个简单异步接口

今天学 async 的目标不是重构整个项目，而是先体验 Django 的异步入口。

## 8.1 推荐新增接口

比如在 `notes/views.py` 里加：

```python
import asyncio
```

然后写：

```python
async def api_async_ping(request):
    await asyncio.sleep(0.1)
    return JsonResponse({"message": "async pong"})
```

并在 `notes/urls.py` 里加：

```python
path("api/async-ping/", views.api_async_ping, name="api_async_ping"),
```

## 8.2 这个接口的意义是什么

它的意义不是业务价值，而是学习价值：

- 让你确认 Django 确实能接 async 视图
- 让你理解“async 视图”和“异步 ORM”不是同一回事

---

## 任务 9：理解为什么今天不建议把所有视图都改成 async

这是 Day 5 非常重要的一点。

很多有 FastAPI 背景的人，一看到 Django 支持 async，就会有一个自然冲动：

- 那是不是把所有接口都改成 `async def` 更好？

今天答案是：

- 不是

原因很简单：

- Django 整体不是完全 async-first 设计
- ORM 使用方式和生态体验，和 FastAPI 常见 async 栈不一样
- 如果没有明显的异步 IO 场景，盲目 async 并不会自动更好

所以今天你要建立的判断是：

- Django 支持 async
- 但不要因为“支持”就无脑全改

这就是“async 边界感”。

---

## 任务 10：用 PowerShell 测试过滤、分页和异步接口

今天你要重点学会通过查询参数调接口。

## 10.1 测试按状态过滤

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri "http://127.0.0.1:8000/api/notes/?status=published"
```

## 10.2 测试按作者过滤

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri "http://127.0.0.1:8000/api/notes/?author_id=1"
```

## 10.3 测试按标签过滤

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri "http://127.0.0.1:8000/api/notes/?tag_id=1"
```

## 10.4 测试关键词搜索

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri "http://127.0.0.1:8000/api/notes/?keyword=django"
```

## 10.5 测试分页

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri "http://127.0.0.1:8000/api/notes/?page=1&page_size=2"
```

## 10.6 测试异步接口

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri "http://127.0.0.1:8000/api/async-ping/"
```

### 你今天要重点观察什么

- 查询参数是否真的影响结果
- 分页后的 `count` 和 `results` 是否合理
- 非法参数是否会触发 `400`
- 中间件日志有没有打印出来
- 响应头中是否带有 `X-Request-ID`

---

## 今天你必须真正理解的 4 条链路

## 1. 查询参数链路

- 客户端把条件写进 URL
- Django 通过 `request.GET` 取值
- ORM 根据这些值动态拼查询
- 最终返回筛选后的结果

## 2. 分页链路

- 客户端传 `page` 和 `page_size`
- Django 计算偏移量
- QuerySet 切片
- 返回当前页数据

## 3. 中间件链路

- 请求先进入中间件
- 中间件记录开始时间
- 请求继续流向视图
- 视图返回响应
- 响应回到中间件
- 中间件补充日志和响应头

## 4. 异步接口链路

- Django 接收到异步视图
- 视图里执行异步等待
- 返回 JSON 响应

这 4 条链路只要你能说清楚，Day 5 的核心就已经掌握得很不错了。

---

## 今天不需要做什么

为了让 Day 5 聚焦，你今天先不要展开这些内容：

- 不需要引入 DRF 分页器
- 不需要做复杂全文检索
- 不需要把所有接口改成 class-based views
- 不需要把所有接口改成 async
- 不需要做统一异常中间件

今天重点是：

- 先把 Django 原生请求对象和中间件这条主线吃透

---

## 常见报错和排查方法

## 1. `request.GET` 总是拿不到值

通常说明：

- 你把参数传到了请求体里
- 但你以为它是查询参数

要记住：

- URL 后面的 `?a=1&b=2` 才是 `request.GET`

## 2. 分页报整数转换错误

通常说明：

- `page` 或 `page_size` 不是合法整数

比如：

```text
/api/notes/?page=abc
```

这种情况应该返回 `400`，而不是让程序直接报错。

## 3. 中间件没有生效

通常说明：

- 你写了 `middleware.py`
- 但没有加到 `settings.py` 的 `MIDDLEWARE`

先检查：

- 路径是不是 `notes.middleware.RequestLogMiddleware`
- 拼写是否正确

## 4. 异步接口能跑，但你感觉“没什么特别”

这其实很正常。

因为今天这个异步接口只是用来帮助你理解：

- Django 支持 async 入口

它不是为了马上带来巨大的性能收益。

## 5. 查询结果重复

如果你按多对多字段过滤，有时可能会出现重复项。

这时别忘了：

```python
notes = notes.distinct()
```

---

## 今天的交付标准

今天结束前，你至少应该完成这些事：

- [ ] 理解 `request.GET`、`request.body`、`request.headers`
- [ ] 给 `GET /api/notes/` 增加 `status` 过滤
- [ ] 给 `GET /api/notes/` 增加 `author_id` 过滤
- [ ] 给 `GET /api/notes/` 增加 `tag_id` 过滤
- [ ] 给 `GET /api/notes/` 增加 `keyword` 搜索
- [ ] 给 `GET /api/notes/` 增加基础分页
- [ ] 新建 `notes/middleware.py`
- [ ] 编写请求日志中间件
- [ ] 在 `settings.py` 里注册中间件
- [ ] 新增一个简单 async 接口
- [ ] 用 PowerShell 成功验证过滤、分页和中间件日志

只要这些都完成，Day 5 就算达标。

---

## 今天结束后，项目结构通常会新增或修改这些位置

```text
notes/
├─ middleware.py
├─ views.py
└─ urls.py

studynotes/
└─ settings.py
```

今天的新增文件不多，但这是你第一次比较明显地接触 Django 的“框架级扩展点”。

---

## 今日复盘问题

今天结束后，试着不用看文档，自己回答这些问题：

1. `request.GET`、`request.body`、`request.headers` 分别适合拿什么数据？
2. 为什么列表接口通常需要过滤和分页？
3. 为什么 `tag_id` 过滤时容易用到双下划线查询？
4. 中间件和视图的关系是什么？
5. 为什么中间件特别适合做日志和统一处理？
6. Django 为什么不能因为“支持 async”就把所有视图都改成异步？

如果你能比较顺畅地回答这些问题，说明你今天已经不仅仅是在“改接口”，而是真正开始理解 Django 框架是怎么组织后端能力的。

---

## 可选加分任务

如果你今天状态不错，可以多做两个增强：

### 加分任务 1：给日志中间件加上当前用户名

比如在日志里额外输出：

- 当前请求用户是谁

如果用户未登录，就输出 `anonymous`

### 加分任务 2：支持按多个状态过滤

比如：

```text
/api/notes/?status=draft&status=published
```

这个加分任务会让你开始接触：

- `request.GET.getlist()`

这是 Django 请求对象里一个很实用的细节。

---

## 一句总结今天学了什么

今天你真正学会的不是“又加了几个查询参数”，而是：

> 你开始从“会写接口”走向“会组织请求处理流程”，也第一次真正碰到了 Django 作为框架在请求链、中间件和扩展点上的设计方式。

这一关打通之后，Day 6 再去做测试和安全，你会轻松很多。
