# Day 10 任务清单：学会 `GenericAPIView`、`mixins` 和通用 CRUD 类视图

## 今天的目标

昨天你已经会用 `APIView` 写 DRF 接口了。  
这已经比原生 Django 视图函数清晰很多，但你大概率也会开始发现：

- 列表接口总是要查 queryset
- 详情接口总是要 `get_object`
- 创建接口总是要 `serializer.is_valid()` 再 `save()`
- 更新和删除接口总会出现很多重复逻辑

这正是 DRF 继续往上封装的地方。  
今天要学的核心结论非常简单：

> 如果你的接口本质上是标准 CRUD，那很多重复动作 DRF 已经帮你封装好了。

今天学完后，你应该能做到：

- 理解 `GenericAPIView` 和 `APIView` 的关系
- 看懂 `mixins` 是怎么组合 CRUD 能力的
- 会使用 `ListCreateAPIView`
- 会使用 `RetrieveUpdateDestroyAPIView`
- 知道什么时候该用通用视图，什么时候该自己写 `APIView`

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 45 分钟 | 看 Generic views 和 Mixins |
| 理清封装层级 | 35 分钟 | 把 `APIView`、`GenericAPIView`、通用类视图的关系想明白 |
| 核心编码 | 130 分钟 | 把昨天的 `APIView` 改造成通用 CRUD 类视图 |
| 联调复盘 | 50 分钟 | 观察代码量减少了哪些，哪些能力更容易挂上去 |

---

## 今天的官方文档入口

- Generic views  
  https://www.django-rest-framework.org/api-guide/generic-views/
- Mixins  
  https://www.django-rest-framework.org/api-guide/generic-views/#mixins
- Class-based views 教程  
  https://www.django-rest-framework.org/tutorial/3-class-based-views/

建议阅读顺序：

1. 先看 `Generic views`
2. 看文档里对 `mixins` 的说明
3. 再回头对比你昨天写的 `APIView`

---

## 今天先把 DRF 的封装层级看懂

如果你现在觉得 DRF 类好多，这很正常。  
你先不要死记名字，先记“层级关系”：

## 第 1 层：`APIView`

这是基础类视图。  
你需要自己写：

- `get()`
- `post()`
- `put()`
- `delete()`

优点：

- 灵活
- 好理解
- 适合有明显自定义逻辑的接口

## 第 2 层：`GenericAPIView`

它在 `APIView` 基础上，多给你几件非常常用的工具：

- `queryset`
- `serializer_class`
- `get_queryset()`
- `get_serializer()`
- `get_object()`

也就是说，很多重复代码可以不自己写了。

## 第 3 层：`mixins`

它们不是完整视图，而是“能力模块”，比如：

- `ListModelMixin`
- `CreateModelMixin`
- `RetrieveModelMixin`
- `UpdateModelMixin`
- `DestroyModelMixin`

你可以把它理解成：

- 这是一些“半成品接口能力”

## 第 4 层：通用类视图

例如：

- `ListAPIView`
- `CreateAPIView`
- `ListCreateAPIView`
- `RetrieveUpdateDestroyAPIView`

这些就是 DRF 已经帮你把 `GenericAPIView + mixins` 组合好的现成方案。

一句话记忆：

> `APIView` 更自由，通用类视图更省代码。

---

## 今天你必须理解的 5 个概念

## 1. `queryset` 和 `serializer_class` 是通用视图的核心入口

当你写：

```python
class DrfNoteListCreateView(ListCreateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteDetailSerializer
```

DRF 就知道：

- 数据从哪里来
- 默认使用哪个序列化器

当然，真实项目里通常不会这么简单，  
因为列表和创建往往不应该共用一个序列化器。  
所以今天你还要学习一件事：

## 2. `get_serializer_class()` 用来按动作切换序列化器

比如：

```python
def get_serializer_class(self):
    if self.request.method == "GET":
        return NoteListSerializer
    return NoteWriteSerializer
```

这样你就能做到：

- `GET` 用列表响应结构
- `POST` 用写入校验结构

这比把所有事情硬塞进一个序列化器里干净得多。

---

## 3. `perform_create()` 和 `perform_update()` 很关键

你昨天在 `APIView` 里可能写过：

```python
serializer.save(author=request.user)
```

今天在通用类视图里，推荐放到：

```python
def perform_create(self, serializer):
    serializer.save(author=self.request.user)
```

这样做的好处是：

- 作者来自当前登录用户，而不是前端
- 保存逻辑集中在类视图自己的生命周期方法里
- 结构更接近 DRF 官方推荐方式

同理更新时也可以在 `perform_update()` 里统一处理。

---

## 4. `get_queryset()` 比直接写死 `queryset` 更灵活

如果你以后要按用户、状态、关键词筛选数据，就会发现：

```python
def get_queryset(self):
    return Note.objects.select_related("author").prefetch_related("tags")
```

比简单的：

```python
queryset = Note.objects.all()
```

更适合扩展。

所以今天建议你直接养成一个习惯：

- 简单接口可以写 `queryset`
- 稍微有筛选和优化需求，就优先写 `get_queryset()`

---

## 5. 通用视图擅长“标准 CRUD”，不擅长“复杂业务编排”

这一点一定要记住。  
不是所有接口都应该硬套 `ListCreateAPIView`。

适合通用视图的：

- 笔记列表
- 笔记详情
- 新建
- 更新
- 删除

不太适合通用视图的：

- 一个接口里要触发很多业务动作
- 非标准动作很多
- 状态流转复杂
- 不是典型的资源式 API

遇到这种情况，你就退回 `APIView`，甚至更定制的实现。

---

## 今天的项目任务

我们把昨天的 `APIView` 版本继续升级，目标是得到一组更 DRF 原生的通用类视图。

今天建议完成这些事：

1. 把昨天的列表/创建接口改成 `ListCreateAPIView`
2. 把昨天的详情/更新/删除接口改成 `RetrieveUpdateDestroyAPIView`
3. 用 `get_serializer_class()` 区分读写序列化器
4. 用 `perform_create()` 注入 `author=self.request.user`
5. 用 `get_queryset()` 做 `select_related()` 和 `prefetch_related()`

---

## 推荐代码结构

在 `notes/views.py` 中新增下面这组视图。

## 1. 列表 + 创建通用视图

```python
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Note
from .serializers import NoteListSerializer, NoteDetailSerializer, NoteWriteSerializer


class DrfNoteListCreateGenericView(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return (
            Note.objects.select_related("author")
            .prefetch_related("tags")
            .all()
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return NoteListSerializer
        return NoteWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

### 这段代码你要重点看 3 件事

1. `GET` 和 `POST` 不再手动写方法体了
2. DRF 自动帮你处理很多标准 CRUD 流程
3. 你只需要覆盖“需要自定义的部分”

这正是通用视图最大的价值。

---

## 2. 详情 + 更新 + 删除通用视图

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class DrfNoteDetailGenericView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return (
            Note.objects.select_related("author")
            .prefetch_related("tags", "comments")
            .all()
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return NoteDetailSerializer
        return NoteWriteSerializer
```

这时你会发现一个问题：

- 更新和删除虽然已经能跑
- 但“只有作者能改/删”这件事还没有优雅封装

很好，这正是 Day 12 要专门解决的问题。  
今天你可以先接受一个现实：

> 通用视图解决的是“通用 CRUD 动作”，但对象级权限还需要单独补。

---

## 今天建议加一个“我的笔记”接口

为了更好练习 `get_queryset()`，你可以新增一个：

- `/drf/v3/my-notes/`

它只返回当前登录用户自己的笔记。

例如：

```python
from rest_framework.permissions import IsAuthenticated


class DrfMyNoteListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Note.objects.select_related("author")
            .prefetch_related("tags")
            .filter(author=self.request.user)
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return NoteListSerializer
        return NoteWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

这个接口很适合让你体会：

- `get_queryset()` 可以天然接管“按当前用户筛选”
- 很多列表逻辑根本不需要写在 `get()` 方法体里

---

## 路由建议

今天建议在 `notes/urls.py` 中新增：

```python
path("drf/v3/notes/", views.DrfNoteListCreateGenericView.as_view(), name="drf-v3-note-list-create"),
path("drf/v3/notes/<int:pk>/", views.DrfNoteDetailGenericView.as_view(), name="drf-v3-note-detail"),
path("drf/v3/my-notes/", views.DrfMyNoteListView.as_view(), name="drf-v3-my-note-list"),
```

继续保留前几天的版本，不要删。  
你现在是在“搭理解台阶”，不是追求项目代码最短。

---

## 今天推荐你主动观察的 6 个现象

## 1. 代码量开始明显下降

尤其是：

- 列表
- 创建
- 更新
- 删除

这些标准动作里的样板代码越来越少。

## 2. “自定义点”变得更明确了

你开始把注意力集中在这些方法上：

- `get_queryset()`
- `get_serializer_class()`
- `perform_create()`
- `perform_update()`

这比自己从零写整个方法体更聚焦。

## 3. 读写职责分离更自然

你会更容易接受：

- 读接口用一个 serializer
- 写接口用另一个 serializer

这是非常正常的 API 设计。

## 4. 查询优化更容易统一挂进去

像：

- `select_related("author")`
- `prefetch_related("tags", "comments")`

你现在能直接放在 `get_queryset()` 里，不用每个方法都重复写。

## 5. 权限问题开始变得更显眼

因为 CRUD 主体已经简化后，  
你会更明显地感受到：

- “谁能改”
- “谁能删”
- “匿名用户能看什么”

这些问题才是真正影响 API 行为的重点。

## 6. 你会开始理解 DRF 的“约定优于重复”

DRF 的很多设计都是在说：

- 如果这是标准资源式接口，那就别每次都自己重复写一遍

这和你以前手写原生 Django JSON API 的体验差别会越来越大。

---

## 今天怎么测试

启动服务：

```powershell
python manage.py runserver
```

### 1. 测试列表

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v3/notes/" -Method Get
```

### 2. 测试我的笔记

未登录时：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v3/my-notes/" -Method Get
```

应该返回认证错误。

### 3. 测试创建

```powershell
$body = @{
    title = "Day 10 Generic View"
    content = "练习 DRF GenericAPIView 和通用类视图"
    status = "draft"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v3/notes/" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

### 4. 测试详情、更新、删除

观察这些标准资源接口是不是越来越像你熟悉的现代 REST API 形式。

---

## 今天的易错点

## 1. 以为 `GenericAPIView` 就是完整 CRUD

不是。  
它是“更强的基础类”。  
真正让你少写代码的是：

- `mixins`
- 或已经组合好的通用类视图

## 2. `get_serializer_class()` 里忘了区分请求方法

如果你列表和创建共用一个视图，  
往往需要按方法切换 serializer。

## 3. 忘了 `perform_create()`

如果你不在这里注入 `author=self.request.user`，  
创建时作者字段通常就会出问题。

## 4. 以为通用视图会自动解决对象级权限

不会。  
今天它主要解决的是 CRUD 样板代码问题。  
真正的“只允许作者改自己的对象”，后面还要配权限类。

## 5. 在 `get_queryset()` 里做太重的业务逻辑

`get_queryset()` 更适合做：

- 查询优化
- 当前用户过滤
- 状态过滤
- 搜索条件拼接

不要在里面塞太多和查询无关的复杂业务。

---

## 今天结束后的验收标准

- 你能解释 `APIView` 和 `GenericAPIView` 的区别
- 你能说清楚 `mixins` 的作用是什么
- 你能独立写出 `ListCreateAPIView`
- 你能用 `RetrieveUpdateDestroyAPIView` 做标准详情 CRUD
- 你能把作者注入放到 `perform_create()` 里
- 你能理解为什么 DRF 适合标准资源式接口

---

## 今天的复盘问题

建议你写下这 3 个问题的答案：

1. `APIView` 和通用类视图，分别适合什么场景？
2. 为什么 `get_queryset()` 是 DRF 里很重要的扩展点？
3. 通用类视图帮你省掉的，到底是哪一类重复代码？

---

## 明天会学什么

明天我们继续往更高一层走：  
你会接触到 DRF 非常标志性的两样东西：

- `ViewSet`
- `Router`

这一天会让你真正理解：

> 为什么很多 DRF 项目看起来“只写一个类和一个路由注册”，却能跑出整套 CRUD API。
