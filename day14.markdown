# Day 14 任务清单：学会异常处理、DRF 测试、Schema，并完成阶段收尾

## 今天的目标

今天是 DRF 这一轮学习的最后一天。  
前面几天你已经把这些能力串起来了：

- Serializer
- APIView
- GenericAPIView
- ViewSet
- Router
- 认证和权限
- 过滤、搜索、排序、分页

今天不是再往外铺很多新概念，而是把这套能力收拢成一套更完整的 API 工程意识。

今天的关键词是：

- 错误怎么统一处理
- 接口怎么测试
- API 结构怎么被描述
- 项目怎么做阶段收尾

今天学完后，你应该能做到：

- 理解 DRF 的默认异常响应机制
- 会写基础 API 测试
- 会使用 `APIClient`
- 对 DRF 的 Schema / OpenAPI 能力建立基础认知
- 对自己这 14 天的 Django + DRF 学习路线做出阶段总结

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 55 分钟 | 阅读 Exceptions、Testing、Schemas |
| 异常与测试设计 | 35 分钟 | 规划要覆盖的成功和失败场景 |
| 核心编码 | 120 分钟 | 写 DRF 测试并统一错误处理思路 |
| 收尾总结 | 50 分钟 | 整理 README、阶段总结、下一步计划 |

---

## 今天的官方文档入口

- Exceptions  
  https://www.django-rest-framework.org/api-guide/exceptions/
- Testing  
  https://www.django-rest-framework.org/api-guide/testing/
- Schemas  
  https://www.django-rest-framework.org/api-guide/schemas/

建议阅读顺序：

1. 先看 `Exceptions`
2. 再看 `Testing`
3. 最后看 `Schemas`

---

## 先把今天最重要的结论讲清楚

如果你这几天已经明显感觉到 DRF 比原生 Django 写 API 省事很多，那今天你会再进一步感受到：

> DRF 不只是“帮你少写代码”，它还在帮你把 API 项目的很多规则统一起来。

统一体现在哪？

- 校验错误格式统一
- 权限错误格式统一
- 列表分页结构统一
- 测试方式统一
- API 描述方式更统一

这就是为什么学到今天，你已经不仅是在学“几个类怎么用”，而是在学一套 API 工程思路。

---

## 今天你必须理解的 6 个概念

## 1. DRF 已经帮你处理了很多常见异常

比如这些情况：

- 请求体校验失败
- 未认证
- 无权限
- 找不到对象
- 方法不允许

DRF 会自动返回比较标准的错误结构。  
例如你常见到的：

```json
{
  "detail": "Authentication credentials were not provided."
}
```

这意味着：

- 不是所有错误都要你自己 `return Response(...)`
- 很多错误可以通过异常和 DRF 默认机制处理

---

## 2. `raise_exception=True` 是 DRF 统一错误处理的重要入口

你这几天已经多次写过：

```python
serializer.is_valid(raise_exception=True)
```

它的好处非常大：

- 不用自己判断 `if not serializer.is_valid()`
- DRF 会自动生成标准错误响应
- 你的视图代码更干净

今天你要真正把这个习惯固定下来。

---

## 3. 默认异常处理够用，但你要知道它可以定制

DRF 允许你自定义异常处理函数。  
这在真实项目里很常见，比如你想把错误响应统一成：

```json
{
  "code": "permission_denied",
  "message": "你没有权限执行该操作",
  "details": {}
}
```

学习阶段你不一定要完整重构一套，  
但今天至少要知道：

- DRF 默认有异常处理链路
- 以后你可以做统一风格定制

---

## 4. `APIClient` 是 DRF 测试里最值得先掌握的工具

你前面 Django Core 阶段已经接触过：

- `Client`

今天在 DRF 阶段，建议你重点学：

- `APIClient`

它很适合测试：

- JSON 请求
- 认证后的接口访问
- DRF 风格的响应结构

对你现在的项目来说，它比继续只用原生 `Client` 更贴合场景。

---

## 5. API 测试一定要覆盖失败场景

很多人写测试时只测：

- 创建成功
- 获取成功

但对于 API 项目，真正容易出问题的往往是：

- 未登录创建
- 非作者修改
- 非法字段
- 错误状态值
- 访问不存在对象

今天你一定要有意识地把这些失败场景补进去。

---

## 6. `Schema` 的意义不是“多一个概念”，而是让 API 可被描述

Schema / OpenAPI 的意义在于：

- 告诉别人你的 API 长什么样
- 帮助工具生成文档、调试页面、客户端代码等

今天你不用把文档系统做得很复杂，  
但要建立一个认知：

> 现代 API 项目不只是“代码能跑”，还要“别人容易看懂和使用”。

---

## 今天的项目任务

今天建议完成这些事：

1. 在 `notes/tests.py` 或拆分后的测试文件中新增 DRF 测试
2. 用 `APIClient` 覆盖列表、创建、详情、更新、删除的关键场景
3. 重点覆盖未登录、非作者、非法数据等失败场景
4. 了解 DRF 默认异常处理和自定义异常处理入口
5. 初步了解 Schema/OpenAPI 能力
6. 为当前项目写一份阶段性总结

---

## 今天先把测试范围规划清楚

建议你至少覆盖下面这些场景：

## 1. 列表接口

- 匿名用户可以获取列表
- 返回结构包含分页字段

## 2. 创建接口

- 未登录创建失败
- 登录后创建成功
- 缺少标题创建失败
- 非法状态值创建失败

## 3. 详情接口

- 可以获取存在对象
- 不存在对象返回 404

## 4. 更新接口

- 作者本人可以更新
- 非作者更新失败

## 5. 删除接口

- 作者本人可以删除
- 非作者删除失败

这就是一套很有价值的 API 测试最小闭环。

---

## 推荐测试写法

如果你暂时还没拆测试目录，  
可以先在 `notes/tests.py` 中写。

例如：

```python
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Note


class NoteViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="alice", password="password123")
        self.user2 = User.objects.create_user(username="bob", password="password123")

        self.note = Note.objects.create(
            title="First note",
            content="hello drf",
            author=self.user1,
            status="draft",
        )
```

---

## 1. 测列表接口

```python
    def test_note_list_should_be_public(self):
        response = self.client.get("/drf/v4/notes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
```

这个测试主要验证两件事：

- 匿名用户能访问
- 分页结构生效

---

## 2. 测未登录创建失败

```python
    def test_anonymous_user_cannot_create_note(self):
        payload = {
            "title": "New note",
            "content": "created by anonymous",
            "status": "draft",
        }

        response = self.client.post("/drf/v4/notes/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

注意：

- 具体是 `401` 还是 `403`，要以你当前认证配置和实际返回为准
- 测试时要根据你的项目真实行为写断言

这件事很重要，不要死背某个状态码。

---

## 3. 测登录后创建成功

```python
    def test_authenticated_user_can_create_note(self):
        self.client.force_authenticate(user=self.user1)

        payload = {
            "title": "Created note",
            "content": "created by user1",
            "status": "draft",
        }

        response = self.client.post("/drf/v4/notes/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

这里你会第一次明显感受到：

- `force_authenticate()` 对测试真的很方便

---

## 4. 测非作者更新失败

```python
    def test_non_author_cannot_update_note(self):
        self.client.force_authenticate(user=self.user2)

        payload = {
            "title": "Hacked title",
            "content": "should fail",
            "status": "draft",
        }

        response = self.client.put(f"/drf/v4/notes/{self.note.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

这类测试是今天最有价值的部分之一。

---

## 5. 测字段校验失败

```python
    def test_create_note_without_title_should_fail(self):
        self.client.force_authenticate(user=self.user1)

        payload = {
            "title": "",
            "content": "content only",
            "status": "draft",
        }

        response = self.client.post("/drf/v4/notes/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
```

这个测试是在验证：

- serializer 校验是否真的生效
- 错误字段是不是按预期返回

---

## 今天建议认识一下自定义异常处理入口

你不一定今天就把它接到项目里，  
但至少建议你知道形态大概长什么样。

比如可以新建 `notes/exceptions.py`：

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

然后在 `settings.py` 里接入：

```python
REST_FRAMEWORK = {
    ...
    "EXCEPTION_HANDLER": "notes.exceptions.custom_exception_handler",
}
```

学习阶段你不一定非要开启它，  
但你至少要知道：

- 统一错误响应风格是可以做的

---

## 今天建议了解一下 Schema / OpenAPI 基础

DRF 官方提供了 Schema 能力。  
今天你不用在这个学习项目里做很多复杂配置，  
但建议你完成两件事：

1. 知道 DRF 有 Schema 机制
2. 知道它服务于 API 描述和文档生成

你可以先记住一个概念：

- `AutoSchema`

它是 DRF 文档里经常出现的关键词。  
今天不用深挖，先建立认知就够了。

---

## 今天推荐你主动观察的 7 个现象

## 1. 标准错误格式让测试更容易写

因为错误结构更统一，  
你写断言时会更有抓手。

## 2. 失败场景测试往往比成功场景更有价值

尤其是：

- 权限
- 认证
- 校验

这些部分，最怕的就是越权和漏校验。

## 3. `APIClient` 比原生 `Client` 更贴合 DRF 场景

尤其是在发 JSON 请求和做认证模拟时，体验更顺。

## 4. 你会越来越习惯“让框架抛异常，而不是自己满地 return”

这是一种很重要的 API 框架使用习惯。

## 5. 文档化意识开始形成

到今天你应该已经感受到：

- 可维护 API 不只是“代码写完”
- 还包括测试、错误格式和文档描述

## 6. 你已经具备把当前项目继续做大的基础了

无论你后面继续做：

- JWT
- 文件上传
- 缓存
- Celery
- 部署

现在这套 DRF 主线都已经够你承接下去了。

## 7. 你会更清楚自己到底在学“Django”还是在学“Django API 开发”

到这里，其实你已经把“Django 后端 API 主线”学得很成体系了。

---

## 今天怎么测试

运行测试：

```powershell
python manage.py test
```

如果你想只跑某一组：

```powershell
python manage.py test notes.tests
```

如果你后面把测试拆开，也可以指定具体模块。

今天建议你至少验证：

- 列表公开访问
- 未登录创建失败
- 登录创建成功
- 非作者更新失败
- 校验失败返回 400
- 不存在对象返回 404

---

## 今天的易错点

## 1. 只写 happy path 测试

这是最常见的测试误区。  
今天一定要优先补失败场景。

## 2. 对状态码断言死记硬背

有些场景到底是 `401` 还是 `403`，  
和你的认证配置有关。  
以当前项目真实行为为准。

## 3. 测试里没有造出“不同作者”的数据

如果只有一个用户，你根本测不出对象级权限是否生效。

## 4. 以为 Schema 今天必须深入到高级定制

不用。  
今天的目标只是建立正确认知，不是把文档系统做成大工程。

## 5. 误以为“测试跑通”就等于“项目已经生产可用”

测试很重要，但它只是质量保障的一部分。  
部署、安全、日志、监控这些以后还会继续补。

---

## 今天结束后的验收标准

- 你会用 `APITestCase` 或 `APIClient`
- 你能为 DRF 接口写成功和失败两类测试
- 你能解释 DRF 默认异常处理的大致作用
- 你知道 DRF 提供 Schema / OpenAPI 能力
- 你能总结当前项目的 DRF 改造主线

---

## 这 7 天 DRF 学完后，你已经掌握了什么

如果你认真把 Day 8 到 Day 14 走完，你已经掌握了 DRF 的核心主线：

- `Serializer`
- `ModelSerializer`
- `Request` / `Response`
- `APIView`
- `GenericAPIView`
- 通用类视图
- `ViewSet` / `Router`
- 认证与权限
- 对象级权限
- 过滤、搜索、排序、分页
- 异常与测试基础

这已经足够你做一套中小型的 Django API 项目了。

---

## 接下来学什么最合适

如果你想继续沿“后端 API”方向走，下一阶段最推荐的是：

1. JWT 认证
2. 文件上传
3. 缓存和性能优化
4. Celery 异步任务
5. Docker 和部署
6. 日志、监控和生产环境排查

如果你想补回 Django 全家桶的其它部分，也可以回头再补：

1. 模板
2. 表单
3. Admin 深度定制
4. Django 信号
5. 自定义用户模型

---

## 今天的复盘问题

建议你写下这 4 个问题的答案：

1. DRF 相比原生 Django JSON API，最让你省力的地方到底是什么？
2. 你现在最顺手的是 `APIView`、通用类视图，还是 `ViewSet`？
3. 你最想继续深挖的下一块是什么：认证、测试、部署，还是性能？
4. 如果让你重新搭一个 API 项目，你会优先用 DRF 的哪套组织方式？

---

## 阶段总结

到这里，你这条学习线可以这样理解：

- Day 1 到 Day 7：学 Django Core 后端基础
- Day 8 到 Day 14：学 DRF，把 API 层工程化

如果你的目标是：

- 用 Django 做后端
- 做 API 服务
- 从 FastAPI 迁移一部分思维过来

那你现在已经走完了一条非常完整、也非常实用的主线。
