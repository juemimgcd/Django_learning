# Day 12 任务清单：补上 API 测试和异常处理习惯

## 主线继续不变

今天依然是：

- `APIView`
- `Serializer`
- `service`

这一天补的是质量保障，不是接口抽象重写。

也就是说：

- Day 8 把 DRF 主线搭起来
- Day 9 把 CRUD 补完整
- Day 10 把认证和权限补上
- Day 11 把列表接口工程化
- Day 12 开始把这套主线变成“可验证、可维护”的项目

---

## 今天的目标

把项目从“接口能跑”推进到：

- 关键成功路径有测试
- 关键失败路径有测试
- 校验错误尽量让 DRF 自动处理
- 代码里少写散乱的 `if not serializer.is_valid()`

也就是说，今天的关键词是：

> 可验证、可维护。

---

## 今天这份笔记怎么读

和 Day 8 到 Day 11 一样，今天不要只看代码结论。

你要继续训练这种阅读方式：

1. 先看这段代码要解决什么问题
2. 再看每个类、每个方法负责什么
3. 再看每个参数具体控制什么
4. 最后总结这段代码完成了什么功能

今天最容易混的点有：

- `APIClient`
- `APITestCase`
- `force_authenticate(...)`
- `format="json"`
- `response.data`
- `serializer.is_valid(raise_exception=True)`
- `exception_handler(exc, context)`

如果这些不拆开看，很容易觉得“测试”和“异常处理”都是框架魔法。

---

## 为什么今天先补测试，而不是再学更多新类

因为对真实项目来说：

- 权限、过滤、分页已经做上来以后
- 最应该补的是测试

否则你后面每改一次 view、serializer、service，都不放心。

这也是避免“今天学一种，明天推翻一种”的重要手段：

- 有测试兜底，你才敢稳定迭代

---

## 今天建议看的官方文档

- Testing  
  https://www.django-rest-framework.org/api-guide/testing/
- Exceptions  
  https://www.django-rest-framework.org/api-guide/exceptions/

今天重点看：

1. `APIClient`
2. `APITestCase`
3. `serializer.is_valid(raise_exception=True)`
4. DRF 默认异常响应

---

## 任务 1：把 DRF 测试工具用起来

今天建议从 Django `TestCase` 过渡到 DRF 的：

- `APIClient`
- `APITestCase`

推荐起步写法：

```python
from rest_framework.test import APITestCase


class NoteApiTests(APITestCase):
    ...
```

下面把这段最小示例拆开讲。

### 1.1 `from rest_framework.test import APITestCase`

这一行的意思是：

- 从 DRF 的测试模块里导入 `APITestCase`

为什么今天更推荐它，而不是继续只用 Django 原生 `TestCase`：

- 它内部已经帮你准备好了更适合 API 的测试客户端
- 对 JSON 请求、认证模拟、DRF 响应结构更顺手

---

### 1.2 `class NoteApiTests(APITestCase):`

这行表示：

- 你定义了一组 API 测试
- 这些测试继承自 `APITestCase`

`APITestCase` 可以先理解成：

- “专门给 DRF 接口准备的测试基类”

---

### 1.3 `APITestCase` 和 `APIClient` 的关系

这两个名字经常一起出现，很容易混。

你可以这样理解：

- `APIClient`
  是真正发请求的测试客户端工具
- `APITestCase`
  是一个测试基类，它内部已经给你准备好了 `self.client`

也就是说，当你继承了 `APITestCase`，通常可以直接用：

```python
self.client.get(...)
self.client.post(...)
self.client.patch(...)
```

而这个 `self.client` 本质上就是 DRF 风格的测试客户端。

---

### 1.4 为什么今天要切测试工具，而不是业务接口切写法

因为这是工具升级，不是项目结构推翻。

它解决的是：

- 让你更自然地测试 JSON 请求
- 让你更自然地测试认证后的接口访问
- 让你更自然地检查 DRF 的响应结构

这一步不会破坏你前面已经稳定下来的主线。

---

## 任务 2：先把最小测试闭环补全

今天至少覆盖这些场景：

### 列表

- 匿名用户可以获取列表
- 返回分页结构

### 创建

- 未登录创建失败
- 登录后创建成功
- 缺少标题创建失败

### 详情

- 获取存在对象成功
- 获取不存在对象返回 404

### 更新

- 作者本人更新成功
- 非作者更新失败

### 删除

- 作者本人删除成功
- 非作者删除失败

这套覆盖已经足够支撑你后面继续迭代。

为什么今天一开始就强调失败场景：

- 因为 API 项目最容易出问题的，往往不是 happy path
- 而是权限、认证、非法输入、对象不存在这些边界

---

## 任务 3：把 view 中的校验写法统一成 `raise_exception=True`

今天建议把所有这类写法：

```python
serializer = NoteCreateSerializer(data=request.data)
if not serializer.is_valid():
    return Response(serializer.errors, status=400)
```

统一收敛成：

```python
serializer = NoteCreateSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
```

下面把这两种写法拆开比较。

### 3.1 `serializer = NoteCreateSerializer(data=request.data)`

这行的意思是：

- 使用创建 serializer 接收前端输入
- `data=request.data` 表示当前传进去的是“待校验的输入数据”

这里的 `request.data` 是：

- DRF 已经解析好的请求体数据

---

### 3.2 `if not serializer.is_valid():`

这种旧写法的意思是：

- 先手动执行校验
- 如果失败，再自己手动返回错误响应

它不是错，但问题是：

- 你每个接口都要重复写一层 `if`
- 错误处理风格容易不统一

---

### 3.3 `serializer.is_valid(raise_exception=True)`

这行代码里：

- `is_valid()`
  执行 serializer 校验
- `raise_exception=True`
  表示如果校验失败，直接抛出异常

这里的关键点是：

- 失败后不是你自己 `return Response(...)`
- 而是交给 DRF 的异常处理链路

这行代码完成的功能是：

- 让输入校验失败时自动生成 DRF 标准错误响应

---

### 3.4 为什么更推荐 `raise_exception=True`

好处有 3 个：

1. 少一层重复判断
2. 错误响应交给 DRF 统一处理
3. view 代码更干净

所以今天你要固定一个项目默认习惯：

> 只要是 serializer 校验，优先写成 `is_valid(raise_exception=True)`。

---

## 任务 4：明确哪些错误应该交给 DRF 处理

今天开始，你要有这个意识：

- 校验错误，优先交给 serializer 抛
- 权限错误，优先交给权限系统抛
- 找不到对象，优先抛 404

不要把所有错误都手写成：

```python
return Response({"error": "xxx"}, status=400)
```

真实项目里，越统一越容易维护和测试。

---

### 4.1 校验错误

例如：

- 字段缺失
- 字段类型不对
- 枚举值不合法

这些更适合交给：

- serializer

例如：

```python
serializer = NoteCreateSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
```

---

### 4.2 权限错误

例如：

- 未登录用户写接口
- 非作者修改别人的 note

这些更适合交给：

- `permission_classes`
- 自定义权限类

例如：

```python
permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
```

---

### 4.3 找不到对象

例如：

- 访问一个不存在的 note id

这些更适合交给：

- `get_object_or_404(...)`
- 或者直接抛 404 异常

你今天要固定的思路是：

- 能交给 DRF 默认机制处理的错误，尽量不要自己手搓一套返回格式

---

## 任务 5：认识自定义异常处理入口，但今天不强推

你今天应该知道 DRF 可以统一接一个异常处理函数，例如：

```python
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "message": response.data.get("detail", "request failed"),
            "errors": response.data,
        }
    return response
```

下面把这段代码拆开讲。

### 5.1 `from rest_framework.views import exception_handler`

这一行导入的是：

- DRF 默认异常处理函数

它的作用是：

- 接收一个异常
- 如果这个异常属于 DRF 能识别的类型
- 就返回标准响应对象

---

### 5.2 `def custom_exception_handler(exc, context):`

这个函数有两个参数：

- `exc`
  当前抛出的异常对象
- `context`
  当前异常发生时的上下文信息

你可以先把 `context` 理解成：

- “这次异常发生时，DRF 顺手带给你的附加信息”

例如里面可能包含：

- 当前 view
- 当前 request

---

### 5.3 `response = exception_handler(exc, context)`

这行的意思是：

- 先调用 DRF 自己的默认异常处理器

为什么先这么做，而不是完全自己从头写：

- 因为 DRF 已经帮你处理了很多常见异常
- 你通常只是在它返回结果的基础上再做包装

这行完成的功能是：

- 先拿到 DRF 原本想返回的错误响应

---

### 5.4 `if response is not None:`

这一行的意思是：

- 只有当 DRF 默认处理器成功生成了响应时
- 你才继续包装它

如果 `response is None`：

- 说明这个异常 DRF 默认没处理掉
- 那通常应该让它继续向上冒

---

### 5.5 `response.data = {...}`

这几行的意思是：

- 你把 DRF 默认的错误响应结构改造成自己项目想要的统一格式

例如：

- `message`
  作为更高层的错误摘要
- `errors`
  保留原始错误明细

这段包装完成的功能是：

- 让项目的错误返回风格更统一

---

### 5.6 为什么今天不建议强制接入项目主线

原因很简单：

- 你现在更需要先吃透 DRF 默认错误结构
- 再决定以后项目是否要统一包装成自定义格式

所以今天的建议是：

- 先知道它的入口长什么样
- 但不强迫自己立刻接进项目

---

## 任务 6：今天重点观察失败场景

今天的测试重点不在 happy path，而在：

- 未登录
- 越权
- 非法字段
- 非法状态值
- 不存在对象

因为这些才是最容易在项目里出事故的地方。

你今天最好主动问自己：

- 这个接口失败时，返回结构是不是统一的
- 这个接口失败时，状态码是不是合理的
- 这个接口失败时，是不是被正确的那一层拦住了

例如：

- 校验失败，应该是 serializer 那层拦住
- 越权，应该是 permission 那层拦住
- 对象不存在，应该是对象获取那层拦住

---

## 任务 7：写一组最小 DRF API 测试

推荐测试片段：

```python
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Note, Tag


User = get_user_model()


class NoteApiTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="alice", password="secret123")
        self.other_user = User.objects.create_user(username="bob", password="secret123")
        self.tag = Tag.objects.create(name="python")
        self.note = Note.objects.create(
            author=self.author,
            title="Owned note",
            content="only author can edit",
            status=Note.STATUS_DRAFT,
        )

    def test_note_list_should_be_public(self):
        response = self.client.get("/api/notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_anonymous_user_cannot_create_note(self):
        payload = {
            "title": "New note",
            "content": "created by anonymous",
            "status": "draft",
        }
        response = self.client.post("/api/notes/create/", payload, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_authenticated_user_can_create_note(self):
        self.client.force_authenticate(user=self.author)
        payload = {
            "title": "Created note",
            "content": "created by author",
            "status": "draft",
            "tag_ids": [self.tag.id],
        }
        response = self.client.post("/api/notes/create/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_author_cannot_update_note(self):
        self.client.force_authenticate(user=self.other_user)
        payload = {"title": "hack"}
        response = self.client.patch(f"/api/notes/{self.note.id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_note_without_title_should_fail(self):
        self.client.force_authenticate(user=self.author)
        payload = {
            "title": "",
            "content": "content only",
            "status": "draft",
        }
        response = self.client.post("/api/notes/create/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
```

下面把这组测试拆开讲。

### 7.1 `from rest_framework import status`

这一行导入的是：

- DRF 提供的状态码常量

这样你写断言时不需要自己记魔法数字：

- `status.HTTP_200_OK`
- `status.HTTP_201_CREATED`
- `status.HTTP_400_BAD_REQUEST`

---

### 7.2 `class NoteApiTests(APITestCase):`

这行表示：

- 你正在写一组 DRF 风格的接口测试

`APITestCase` 已经给你准备好：

- 数据库隔离环境
- DRF 风格测试客户端

---

### 7.3 `def setUp(self):`

这个方法的作用是：

- 在每个测试方法运行前准备测试数据

今天这里准备了：

- 两个用户
- 一个标签
- 一条 note

为什么要准备两个用户：

- 因为今天的重点之一是权限测试
- 只准备一个用户，你测不出“非作者”这个场景

---

### 7.4 `response = self.client.get("/api/notes/")`

这一行的意思是：

- 用测试客户端向列表接口发一个 GET 请求

这里不用手动拼 `http://127.0.0.1:8000`，因为：

- 测试客户端是在 Django 测试环境内部直接调路由

---

### 7.5 `self.assertIn("results", response.data)`

这里的 `response.data` 是 DRF 测试里很方便的一点。

它表示：

- DRF 已经帮你把响应体解析成了 Python 数据结构

你不需要自己再写：

- `response.json()`

这行断言完成的功能是：

- 检查分页结构里有没有 `results`

---

### 7.6 `response = self.client.post(..., format="json")`

这里的 `format="json"` 很关键。

它的意思是：

- 告诉 `APIClient`：这次请求体按 JSON 发送

为什么在 DRF 测试里推荐这样写，而不是自己手写 `content_type="application/json"`：

- 因为 `APIClient` 已经帮你做了更贴合 DRF 的处理

---

### 7.7 `self.client.force_authenticate(user=self.author)`

这一行的作用是：

- 在测试里直接把当前请求客户端认证成某个用户

这和你前面学过的 `force_login(...)` 很像，但它更贴近 DRF 测试场景。

它完成的功能是：

- 让你不用真的走登录接口，也能直接测试“已认证用户访问”

---

### 7.8 `self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])`

这里为什么不一定写死一个状态码：

- 因为匿名用户写接口在不同认证配置下，可能返回 401 或 403
- 学习阶段先抓住“它必须失败”这个核心更重要

当然，等你的认证配置固定后，也可以收紧成一个明确状态码断言。

---

### 7.9 `self.assertIn("title", response.data)`

这行的作用是：

- 验证校验失败时，错误是不是准确落在了 `title` 字段上

这类断言很重要，因为它不只是测：

- 失败了没有

它还在测：

- 错误是不是按预期出在正确字段上

---

### 7.10 这组测试完成了什么功能

它完成了最小但非常有价值的一套 API 质量保障：

1. 测列表公开可访问
2. 测匿名写接口失败
3. 测已认证用户创建成功
4. 测非作者更新失败
5. 测字段校验失败返回 400 且错误落在正确字段

这已经足够给你当前的主线提供第一层稳定的安全网。

---

## 补充知识：为什么今天不急着上 `GenericAPIView`

因为 `APIView` 本身并不妨碍你写出：

- 干净的测试
- 统一的错误处理
- 稳定的权限逻辑

今天的问题根本不是“类够不够高级”，而是：

- 项目是否可验证

所以今天继续守住主线，不折腾抽象层级。

---

## 今天不做什么

- 不把主项目重写成 `GenericAPIView`
- 不把主项目重写成 `ViewSet`
- 不为了统一错误格式而过早接自定义异常处理

今天先把默认 DRF 机制和测试补牢。

---

## 今天的交付标准

- [ ] 使用 `APIClient` 或 `APITestCase`
- [ ] 列表、创建、详情、更新、删除至少各有 1 个测试
- [ ] 失败场景测试数量不少于成功场景
- [ ] 主流程接口使用 `serializer.is_valid(raise_exception=True)`
- [ ] 你能看懂 DRF 默认错误响应结构

---

## 今日复盘问题

1. 为什么测试是避免“边学边推翻”的关键保障？
2. 为什么 `raise_exception=True` 比手动 `if not is_valid()` 更适合作为项目默认写法？
3. 为什么失败场景测试往往比成功场景更有价值？
4. `force_authenticate(...)` 和 `format="json"` 在 DRF 测试里分别解决什么问题？
5. 什么时候才值得接自定义异常处理？

---

## 一句总结

今天你不是学新接口写法，而是在让已有主线具备真实项目必须有的质量保障能力。
